#!/usr/bin/env python3
"""Ciclo Studio v10: inspect, init, run e resume; nenhuma geracao cega de codigo.

O agente revisa o resultado e prepara a proxima versao. Este runner executa
uma rodada por versao, com limite duravel, snapshots e nenhuma repeticao de
envio apos timeout. Chave existente obrigatoria, nunca salva no relatorio.
"""
import argparse
import ast
import base64
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time

from studio_runner import status_de

RPC = "https://studio.genlayer.com/api"
LAYOUT = ("case_id", "case_url", "status", "painel", "termo_opcao")
FINAL = {"FINALIZED", "UNDETERMINED", "CANCELED", "CANCELLED"}


class CycleError(RuntimeError):
    pass


def safe_rpc_error(obj, method):
    """Nunca propagar message/data: o Studio pode incluir node_config sensivel."""
    error = obj.get("error") if isinstance(obj, dict) else None
    code = error.get("code", "UNKNOWN") if isinstance(error, dict) else "UNKNOWN"
    return CycleError("RPC_ERROR:" + str(code) + ":" + str(method))


def redact(data):
    """Recibos do Studio podem incluir segredos de node_config; nao persisti-los."""
    if isinstance(data, dict):
        return {k: ("[REDACTED]" if re.sub(r"[^a-z]", "", k.lower()) in
                    {"privatekey", "apikey", "secret", "password", "accesstoken", "authorization"}
                    else redact(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [redact(v) for v in data]
    return data


def sha(code):
    return hashlib.sha256(code).hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(prefix=".journal-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(redact(data), f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def version_of(code):
    tree = ast.parse(code.decode("utf-8"))
    versions = [n.value.value for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "VERSAO" for t in n.targets)
                and isinstance(n.value, ast.Constant)]
    if (len(versions) != 1 or not isinstance(versions[0], str)
            or not re.fullmatch(r"[1-9]\d*\.\d+\.\d+-experimental", versions[0])
            or int(versions[0].split('.')[0]) < 10):
        raise CycleError("O candidato deve declarar VERSAO=M.x.y-experimental literal, major >= 10")
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and any(
        isinstance(b, ast.Attribute) and b.attr == "Contract" for b in n.bases)]
    if len(classes) != 1:
        raise CycleError("Esperado exatamente um contrato")
    fields = [n for n in classes[0].body if isinstance(n, ast.AnnAssign)]
    if tuple(n.target.id for n in fields) != LAYOUT or any(not isinstance(n.annotation, ast.Name) or n.annotation.id != "str" for n in fields):
        raise CycleError("Layout de storage deve permanecer exatamente o da v10.2")
    methods = {n.name for n in classes[0].body if isinstance(n, ast.FunctionDef)}
    if not {"upgrade", "get_version", "get_code_hash", "can_upgrade", "analyze_case", "get_case", "get_termo_opcao"} <= methods:
        raise CycleError("Candidato sem interface de upgrade/leitura/analise exigida")
    compile(tree, "candidato.py", "exec")
    return versions[0]


def tx_hash(v):
    h = v.hex() if hasattr(v, "hex") else str(v)
    h = h if h.startswith("0x") else "0x" + h
    if not re.fullmatch(r"0x[0-9a-fA-F]{64}", h):
        raise CycleError("Hash de transacao invalido")
    return h


def final_receipt(tx):
    lr = (tx.get("consensus_data") or {}).get("leader_receipt")
    if isinstance(lr, list):
        return lr[0] if lr and isinstance(lr[0], dict) else {}
    return lr if isinstance(lr, dict) else {}


def execution(tx):
    """Nao tratar MAJORITY_AGREE ou ausencia de erro como prova de sucesso."""
    return final_receipt(tx).get("execution_result") or tx.get("execution_result")


def summary(tx):
    lr = final_receipt(tx)
    errors = []
    diagnostics = []
    def collect(obj):
        if isinstance(obj, dict):
            if obj.get("execution_result") == "ERROR":
                raw = obj.get("result")
                if isinstance(raw, str):
                    try:
                        data = base64.b64decode(raw, validate=True)
                        if data and data[0] in (1, 2):
                            errors.append(data[1:].decode("utf-8"))
                    except (ValueError, UnicodeError):
                        pass
            for v in obj.values():
                collect(v)
        elif isinstance(obj, list):
            for v in obj:
                collect(v)
    collect(tx.get("consensus_data"))
    collect(tx.get("consensus_history"))
    # Monitoring e consensus_data repetem recibos do historico. Nao percorrer
    # recursivamente esses espelhos para contar diagnosticos/votos.
    rounds = (tx.get("consensus_history") or {}).get("consensus_results") or []
    def diag(rec, index):
        if not isinstance(rec, dict):
            return
        g = rec.get("genvm_result") or {}
        codes = re.findall(r"(?m)^MEDIARE_DIAG:([A-Z_]+)$", g.get("stdout") or "")
        if codes:
            diagnostics.append({"round": index, "mode": rec.get("mode"), "vote": rec.get("vote"), "codes": codes})
    for i, round_result in enumerate(rounds):
        for key in ("leader_result", "validator_results"):
            for rec in round_result.get(key) or []:
                diag(rec, i)
    if not rounds:
        data = tx.get("consensus_data") or {}
        for rec in data.get("validators") or []:
            diag(rec, None)
        diag(lr, None)
    return {"status": status_de(tx), "exec": execution(tx), "result_name": tx.get("result_name"),
            "rotacoes": tx.get("rotation_count"), "rodadas": tx.get("num_of_rounds"),
            "erros": sorted(set(errors)), "gas_usado": lr.get("gas_used"),
            "execution_stats": lr.get("execution_stats"),
            "diagnosticos": diagnostics,
            "custo_monetario": None}  # nao inventar conversao de gas/tokens em dinheiro


def successful(tx):
    return status_de(tx) == "FINALIZED" and execution(tx) == "SUCCESS"


def contract_address(tx):
    found = set()
    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("contract_address", "contractAddress") and isinstance(v, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", v):
                    found.add(v)
                else:
                    walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(tx.get("data"))
    if len(found) != 1:
        raise CycleError("Endereco do deploy ausente/ambiguo no recibo; nao deployar novamente")
    return found.pop()


def decode_state(value):
    for _ in range(3):
        if not isinstance(value, str):
            break
        value = json.loads(value)
    if not isinstance(value, dict):
        raise CycleError("get_case nao retornou objeto JSON")
    return value


def evaluate(state, expected_version, cid):
    p = decode_state(state.get("painel"))
    if state.get("versao") != expected_version or p.get("versao") != expected_version or state.get("case_id") != cid:
        raise CycleError("Estado antigo ou versao/caso diferentes da rodada")
    if state.get("status") != "termo_opcao_disponivel" or not isinstance(state.get("termo_opcao"), str) or not state["termo_opcao"].strip():
        raise CycleError("Termo ausente apesar de execucao aceita")
    cons = p.get("consolidado") or {}
    items = cons.get("pedidos") or []
    if not items or cons.get("painel_completo") is not True:
        raise CycleError("Painel incompleto")
    result = {"execucao_valida": True, "merito": "PENDENTE_REVISAO", "pedidos": [], "total_devido": cons.get("faixa_total_centavos")}
    for item in items:
        n = item.get("negociacao") or {}
        result["pedidos"].append({"id": item.get("pedido_id"), "conclusao": item.get("status"),
                                  "negociacao": n.get("estado"), "tipo": (n.get("opcao") or {}).get("tipo"),
                                  "faixa_negociacao": n.get("faixa_centavos"),
                                  "faixa_discussao": n.get("faixa_discussao_centavos")})
    return result


class Studio:
    """SDK 0.18; RPC cru para evitar decodificador antigo de recibos/status."""
    def __init__(self, key_path, endpoint=RPC):
        from genlayer_py import create_account
        from genlayer_py.chains import studionet
        from genlayer_py.client.genlayer_client import GenLayerClient
        import requests
        from types import MethodType
        self.account = create_account(Path(key_path).read_text().strip())
        chain = copy.deepcopy(studionet)
        chain.rpc_urls["default"]["http"] = [endpoint]
        self.client = GenLayerClient(chain, self.account)
        self.before_send = None
        self.after_send = None
        self.endpoint = endpoint
        def request(provider, method, params):
            if method == "eth_sendRawTransaction" and self.before_send:
                self.before_send()
            r = requests.post(endpoint, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                              headers={"User-Agent": "genlayer-py", "Content-Type": "application/json"}, timeout=30)
            r.raise_for_status()
            obj = r.json()
            if obj.get("error"):
                raise safe_rpc_error(obj, method)
            if method == "eth_sendRawTransaction" and self.after_send:
                self.after_send(obj["result"])
            return obj
        self.client.provider.make_request = MethodType(request, self.client.provider)
        self.chain_id = self.client.chain_id
        if self.chain_id != 61999 or endpoint != RPC:
            raise CycleError("Este runner so autoriza a Studionet oficial, chain ID 61999")

    def receipt(self, h):
        return self.client.provider.make_request("eth_getTransactionByHash", [h])["result"]

    def read(self, addr, method):
        from genlayer_py.types import TransactionHashVariant
        print(json.dumps({"consulta": method}), flush=True)
        return self.client.read_contract(address=addr, function_name=method, args=[],
                                         transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)

    def recover_hash(self, evm_hash):
        from web3.logs import DISCARD
        self.client.initialize_consensus_smart_contract()
        rec = self.client.w3.eth.get_transaction_receipt(evm_hash)
        if rec.status != 1:
            raise CycleError("Envio EVM revertido; exige revisao")
        abi = self.client.chain.consensus_main_contract["abi"]
        contract = self.client.w3.eth.contract(abi=abi)
        for name in ("NewTransaction", "CreatedTransaction"):
            events = contract.get_event_by_name(name).process_receipt(rec, DISCARD)
            if len(events) == 1:
                return tx_hash(events[0]["args"]["txId"])
        raise CycleError("Envio sem hash GenLayer recuperavel; exige revisao")


class Cycle:
    def __init__(self, studio, out, poll=10, timeout=1200):
        self.s = studio
        self.out = Path(out)
        self.poll, self.timeout = poll, timeout
        self.path = self.out / "cycle.json"
        self.m = read_json(self.path) if self.path.exists() else None
        if self.m and (self.m["account"].lower() != self.s.account.address.lower() or self.m["chain_id"] != self.s.chain_id):
            raise CycleError("Conta/rede diferem do ciclo registrado")

    def save(self):
        write_json(self.path, self.m)

    def stage(self, name, code):
        p = self.out / name
        if p.exists() and p.read_bytes() != code:
            raise CycleError("Snapshot imutavel ja existe com outro conteudo")
        if not p.exists():
            with p.open("xb") as f:
                f.write(code)
        return p

    def operation(self, kind, version=None):
        for op in self.m["ops"]:
            if op["kind"] == kind and op.get("version") == version:
                return op
        if any(op["state"] != "done" for op in self.m["ops"]):
            raise CycleError("Ha operacao pendente/incerta. Use resume antes de enviar outra")
        op = {"kind": kind, "version": version, "state": "prepared", "started": time.time()}
        self.m["ops"].append(op)
        self.save()
        return op

    def check_budget(self):
        if time.time() >= self.m["deadline"]:
            raise CycleError("Limite de 6 horas atingido; somente consultas de recibos pendentes permitidas")
        if self.m["send_attempts"] >= self.m["max_calls"]:
            raise CycleError("Limite de chamadas de execucao atingido")

    def submit(self, op, fn):
        if op["state"] != "prepared":
            raise CycleError("Envio ja tentado; somente retomar consulta, nunca reenviar")
        self.check_budget()
        # Intervalo contado DEPOIS do termino da execucao anterior. O orcamento
        # persistido inclui deploy, upgrade, analyze e envios de resultado incerto.
        remaining = self.m.get("next_send_at", 0) - time.time()
        if remaining > 0:
            time.sleep(min(remaining, 15))
        self.check_budget()
        self.m["send_attempts"] += 1
        op["state"] = "sending"
        self.save()
        def before():
            op["broadcast_started"] = True
            self.save()
        def after(h):
            op["evm_hash"] = tx_hash(h)
            self.save()
        self.s.before_send, self.s.after_send = before, after
        try:
            op["hash"] = tx_hash(fn())
            op["state"] = "pending"
            self.save()
            print(json.dumps({"etapa": op["kind"], "hash": op["hash"]}), flush=True)
        except BaseException as exc:
            op.update(state="uncertain", error_type=type(exc).__name__)
            self.save()
            raise
        finally:
            self.s.before_send = self.s.after_send = None

    def wait(self, op):
        if op["state"] == "done":
            return read_json(self.out / op["receipt"])
        if not op.get("hash"):
            if not op.get("evm_hash"):
                raise CycleError("Envio incerto sem hash; nao repetir. Conferir conta/transacoes no Studio")
            op["hash"] = self.s.recover_hash(op["evm_hash"])
            op["state"] = "pending"
            self.save()
        start, last = time.monotonic(), None
        while True:
            tx = self.s.receipt(op["hash"])
            if isinstance(tx, dict):
                st = status_de(tx)
                if st != last:
                    print(json.dumps({"etapa": op["kind"], "status": st, "exec": execution(tx)}), flush=True)
                    last = st
                op["receipt"] = "receipt-" + op["hash"][2:] + ".json"
                write_json(self.out / op["receipt"], tx)
                if st in FINAL:
                    op.update(state="done", summary=summary(tx), elapsed_s=round(time.time() - op["started"], 2))
                    self.m["next_send_at"] = time.time() + 15
                    self.save()
                    return tx
            if time.monotonic() - start >= self.timeout:
                self.save()
                raise CycleError("Timeout de observacao; nao enviar outra transacao. Use resume")
            time.sleep(self.poll)

    def initialize(self, max_versions, cid, contract=None, max_calls=1000):
        if self.m:
            raise CycleError("Ciclo ja inicializado. Use run/resume")
        if contract:
            self.check_upgrade(contract)
        self.m = {"account": self.s.account.address, "chain_id": self.s.chain_id, "endpoint": self.s.endpoint,
                  "max_versions": max_versions, "case_id": cid, "contract": contract, "versions": [], "ops": [],
                  "started": time.time(), "deadline": time.time() + 6 * 3600,
                  "max_calls": max_calls, "send_attempts": 0, "next_send_at": 0}
        self.save()
        if not contract:
            code = Path(__file__).with_name("studio_bootstrap.py").read_bytes()
            self.stage("bootstrap.py", code)
            self.s.client.get_contract_schema_for_code(code)
            op = self.operation("deploy")
            self.submit(op, lambda: self.s.client.deploy_contract(code=code, args=[], account=self.s.account))
            self.finish_deploy(op)

    def finish_deploy(self, op):
        tx = self.wait(op)
        if not successful(tx):
            raise CycleError("Deploy sem SUCCESS confirmado; nao repetir automaticamente")
        self.m["contract"] = contract_address(tx)
        self.save()
        self.check_upgrade(self.m["contract"])

    def check_upgrade(self, addr):
        methods = self.s.client.get_contract_schema(addr).get("methods", {})
        if not {"upgrade", "get_version", "get_code_hash", "can_upgrade"} <= set(methods):
            raise CycleError("Contrato nao tem interface de upgrade exigida; usar nova instancia bootstrap")
        if self.s.read(addr, "can_upgrade") is not True:
            raise CycleError("A conta local nao e autorizada a atualizar este contrato")

    def run(self, source, upgrade_only=False):
        if not self.m or not self.m.get("contract"):
            raise CycleError("Inicialize/retome o bootstrap primeiro")
        if self.unfinished_restore():
            raise CycleError("Rollback sem verificacao final; use resume")
        code = Path(source).read_bytes()
        version, digest = version_of(code), sha(code)
        rows = [v for v in self.m["versions"] if v["version"] == version]
        if rows:
            row = rows[0]
            if row["sha256"] != digest:
                raise CycleError("Mesma versao com outro codigo: incremente a revisao")
            if bool(row.get("upgrade_only")) != bool(upgrade_only):
                raise CycleError("Modo da rodada difere do registro; use resume")
            if row.get("finished"):
                print(json.dumps(row, ensure_ascii=False), flush=True)
                return
        else:
            self.check_budget()
            if len(self.m["versions"]) >= self.m["max_versions"]:
                raise CycleError("Limite de versoes atingido; nova autorizacao necessaria")
            if any(not v.get("finished") for v in self.m["versions"]):
                raise CycleError("Rodada anterior incompleta; retome antes de criar outra")
            if any(o["state"] != "done" for o in self.m["ops"]):
                raise CycleError("Operacao incerta/pendente impede nova rodada")
            self.check_upgrade(self.m["contract"])
            self.s.client.get_contract_schema_for_code(code)
            snapshot = version + ".py"
            self.stage(snapshot, code)
            row = {"version": version, "sha256": digest, "snapshot": snapshot,
                   "upgrade_only": bool(upgrade_only), "finished": False}
            self.m["versions"].append(row)
            self.save()
        self.continue_round(row, upgrade_only=upgrade_only)

    def continue_round(self, row, upgrade_only=False):
        upgrade_only = bool(upgrade_only or row.get("upgrade_only"))
        addr, version = self.m["contract"], row["version"]
        code = (self.out / row["snapshot"]).read_bytes()
        if sha(code) != row["sha256"]:
            raise CycleError("Snapshot alterado depois de registrado")
        op = self.operation("upgrade", version)
        if op["state"] == "prepared":
            self.submit(op, lambda: self.s.client.write_contract(address=addr, function_name="upgrade", args=[code], account=self.s.account))
        if not successful(self.wait(op)):
            row.update(finished=True, result="UPGRADE_FAILED")
            self.save()
            return
        if self.s.read(addr, "get_version") != version or self.s.read(addr, "get_code_hash") != row["sha256"]:
            raise CycleError("Versao/hash remoto nao correspondem ao snapshot; parar antes de analyze_case")
        if upgrade_only:
            row.update(finished=True, result="UPGRADE_ONLY_VERIFIED")
            self.save()
            print(json.dumps(row, ensure_ascii=False), flush=True)
            return
        op = self.operation("analyze_case", version)
        if op["state"] == "prepared":
            self.submit(op, lambda: self.s.client.write_contract(address=addr, function_name="analyze_case",
                        args=[self.m["case_id"]], account=self.s.account))
        tx = self.wait(op)
        row["transaction"] = op["hash"]
        if successful(tx):
            state = decode_state(self.s.read(addr, "get_case"))
            term = self.s.read(addr, "get_termo_opcao")
            if term != state.get("termo_opcao"):
                raise CycleError("Getters devolveram documentos diferentes")
            row["evaluation"] = evaluate(state, version, self.m["case_id"])
            write_json(self.out / (version + "-state.json"), state)
            self.stage(version + "-termo.md", term.encode("utf-8"))
            row["result"] = "SUCCESS_REVIEW_REQUIRED"
        else:
            row["result"] = "EXECUTION_FAILED" if execution(tx) == "ERROR" else "NO_CONFIRMED_SUCCESS"
        row["finished"] = True
        self.save()
        print(json.dumps(row, ensure_ascii=False), flush=True)

    def resume(self):
        if not self.m:
            raise CycleError("Ciclo inexistente")
        if not self.m.get("contract"):
            self.finish_deploy(self.operation("deploy"))
        restore = self.unfinished_restore()
        if restore:
            self.finish_rollback(restore)
            return
        for row in self.m["versions"]:
            if not row.get("finished"):
                self.continue_round(row)
                return
        print("Nenhuma rodada incompleta; preparar nova revisao e usar run.")

    def unfinished_restore(self):
        if not self.m:
            return None
        return next((o for o in self.m["ops"] if o["kind"] == "rollback" and not o.get("restore_result")), None)

    def rollback(self, version, reason):
        if (not self.m or not self.m.get("contract") or self.unfinished_restore()
                or any(o["state"] != "done" for o in self.m["ops"])
                or any(not v.get("finished") for v in self.m["versions"])):
            raise CycleError("Finalize/retome a rodada atual antes de rollback")
        rows = [v for v in self.m["versions"] if v["version"] == version]
        if len(rows) != 1 or not reason.strip():
            raise CycleError("Rollback exige versao registrada e motivo")
        row = rows[0]
        code = (self.out / row["snapshot"]).read_bytes()
        if sha(code) != row["sha256"] or version_of(code) != version:
            raise CycleError("Snapshot de rollback nao corresponde ao registro")
        self.check_budget()
        self.check_upgrade(self.m["contract"])
        # ID proprio: voltar duas vezes ao mesmo marco sao duas operacoes,
        # mas retomar uma operacao interrompida nunca e um novo envio.
        op = self.operation("rollback", version + "#" + str(len(self.m["ops"]) + 1))
        op.update(target_version=version, sha256=row["sha256"], snapshot=row["snapshot"], reason=reason)
        self.save()
        self.submit(op, lambda: self.s.client.write_contract(address=self.m["contract"], function_name="upgrade",
                    args=[code], account=self.s.account))
        self.finish_rollback(op)

    def finish_rollback(self, op):
        if not successful(self.wait(op)):
            op["restore_result"] = "FAILED"
            self.save()
            raise CycleError("Rollback nao confirmado; conferir recibo")
        addr = self.m["contract"]
        if self.s.read(addr, "get_version") != op["target_version"] or self.s.read(addr, "get_code_hash") != op["sha256"]:
            raise CycleError("Rollback sem identidade remota confirmada; somente retomar consultas")
        op["restore_result"] = "VERIFIED"
        self.save()
        print(json.dumps({"rollback": op["target_version"], "hash": op["hash"],
                          "status": "VERIFIED", "aviso": "Codigo restaurado; estado/termo anterior nao e desfeito"}), flush=True)

    def skip(self, reason):
        """Encerrar revisao antes da analise, somente sem transacao pendente."""
        if not self.m or any(o["state"] != "done" for o in self.m["ops"]):
            raise CycleError("Nao encerrar rodada com envio incerto/pendente")
        rows = [v for v in self.m["versions"] if not v.get("finished")]
        if len(rows) != 1 or not reason.strip():
            raise CycleError("Exige uma rodada incompleta e motivo de revisao")
        row = rows[0]
        if any(o["kind"] == "analyze_case" and o.get("version") == row["version"] for o in self.m["ops"]):
            raise CycleError("Analise ja registrada; retomar resultado, nao pular")
        row.update(finished=True, result="SKIPPED_BEFORE_ANALYSIS", review=reason)
        self.save()
        print(json.dumps(row, ensure_ascii=False), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("inspect", "init", "run", "resume", "skip", "rollback"))
    ap.add_argument("--key-file", required=True, help="arquivo de chave EXISTENTE, nunca valor da chave")
    ap.add_argument("--out", default="res_cycle_v10")
    ap.add_argument("--contract")
    ap.add_argument("--source")
    ap.add_argument("--version", help="versao exata registrada para rollback")
    ap.add_argument("--reason", help="justificativa obrigatoria de skip, registrada no journal")
    ap.add_argument("--max-versions", type=int)
    ap.add_argument("--case-id", default="5")
    ap.add_argument("--max-calls", type=int, default=1000, help="limite de envios (deploy + upgrades + analises), maximo 1000")
    ap.add_argument("--poll", type=int, default=15)
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--execute", action="store_true", help="autoriza envios dentro do ciclo configurado")
    ap.add_argument("--upgrade-only", action="store_true", help="instala e verifica a versao sem chamar analyze_case")
    args = ap.parse_args()
    if not 1 <= args.poll <= 60 or args.timeout < args.poll:
        ap.error("poll deve estar entre 1 e 60 e timeout >= poll")
    cid = args.case_id.zfill(4)
    if not re.fullmatch(r"[0-9]{4}", cid):
        ap.error("case-id invalido")
    if args.action != "inspect" and not args.execute:
        ap.error("Use --execute somente apos autorizar os envios e o limite do ciclo")
    if not 1 <= args.max_calls <= 1000:
        ap.error("max-calls deve estar entre 1 e 1000")
    if args.action == "init" and (args.max_versions is None or not 1 <= args.max_versions <= 499):
        ap.error("init exige --max-versions entre 1 e 499")
    if args.action == "run" and not args.source:
        ap.error("run exige --source")
    if args.upgrade_only and args.action != "run":
        ap.error("--upgrade-only so pode ser usado com run")
    if args.action == "skip" and not args.reason:
        ap.error("skip exige --reason")
    if args.action == "rollback" and (not args.version or not args.reason):
        ap.error("rollback exige --version e --reason")
    os.umask(0o077)
    studio = Studio(args.key_file)
    if args.action == "inspect":
        result = {"chain_id": studio.chain_id, "account": studio.account.address,
                  "balance_wei": studio.client.get_balance(studio.account.address)}
        if args.contract:
            result["schema"] = studio.client.get_contract_schema(args.contract)
        print(json.dumps(result, ensure_ascii=False, default=str))
        return
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (out / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise CycleError("Outro processo esta operando este ciclo") from None
        c = Cycle(studio, out, args.poll, args.timeout)
        if args.action == "init":
            c.initialize(args.max_versions, cid, args.contract, args.max_calls)
        elif args.action == "run":
            c.run(args.source, upgrade_only=args.upgrade_only)
        elif args.action == "skip":
            c.skip(args.reason)
        elif args.action == "rollback":
            c.rollback(args.version, args.reason)
        else:
            c.resume()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Nao imprimir traceback do SDK, pois pode conter dados de requisicao.
        print(str(exc) if isinstance(exc, CycleError) else "ERRO_DE_INFRAESTRUTURA:" + type(exc).__name__, file=sys.stderr)
        sys.exit(2)
