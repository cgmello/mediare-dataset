#!/usr/bin/env python3
"""Campanha Fase 2: executa a versao congelada do IC nos 500 casos.

O runner e serial, retomavel e fail-closed. Gabaritos nunca sao enviados ao IC.
Recibos sao sanitizados antes de persistir e o log operacional contem apenas
campos selecionados pelo proprio runner.
"""
import argparse
from collections import Counter, defaultdict
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
import time

from studio_cycle import (
    CycleError,
    FINAL,
    Studio,
    decode_state,
    evaluate,
    execution,
    read_json,
    redact,
    sha,
    status_de,
    successful,
    summary,
    tx_hash,
    version_of,
    write_json,
)


SCHEMA_VERSION = 1
DEFAULT_CONTRACT = "0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B"
LABELS = (
    "SATISFATORIO_AUTOMATICO",
    "REVISAR_UTILIDADE",
    "INSATISFATORIO_CONTEUDO",
    "INSATISFATORIO_TECNICO",
)


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def atomic_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(prefix=".phase2-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def append_event(out, kind, **fields):
    """Log append-only com vocabulario controlado; nunca recebe resposta RPC."""
    event = {"at": utc_now(), "event": kind, **fields}
    path = Path(out) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(redact(event), ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_case(dataset, cid):
    obj = read_json(Path(dataset) / "casos" / (cid + ".json"))
    if obj.get("id") != cid or not isinstance(obj.get("documentos"), dict):
        raise CycleError("Caso local invalido: " + cid)
    return obj


def discover_cases(dataset, maximum=500, selected=None):
    root = Path(dataset)
    files = sorted((root / "casos").glob("[0-9][0-9][0-9][0-9].json"))
    available = [p.stem for p in files]
    if selected is None:
        ids = available
        expected = [f"{n:04d}" for n in range(1, maximum + 1)]
        if ids != expected:
            raise CycleError(f"Dataset deve conter exatamente os casos 0001..{maximum:04d}")
    else:
        ids = selected
        if (len(ids) != maximum or len(set(ids)) != len(ids)
                or any(not re.fullmatch(r"\d{4}", cid) or cid not in available for cid in ids)):
            raise CycleError("Selecao deve conter IDs existentes, unicos e com quatro digitos")
    missing = [cid for cid in ids if not (root / "gabaritos" / (cid + ".json")).is_file()]
    if missing:
        raise CycleError("Gabaritos locais ausentes; primeiro ID: " + missing[0])
    return ids


def classify_success(state, evaluation):
    """Triagem operacional estrita; nao substitui avaliacao juridica semantica."""
    panel = decode_state(state.get("painel"))
    items = (panel.get("consolidado") or {}).get("pedidos") or []
    reasons = []
    statuses = Counter()
    option_types = Counter()
    negotiation_states = Counter()
    broad_formula = False
    actionable = 0

    for item in items:
        statuses[str(item.get("status") or "ausente")] += 1
        neg = item.get("negociacao") or {}
        nstate = str(neg.get("estado") or "ausente")
        negotiation_states[nstate] += 1
        option = neg.get("opcao") or {}
        otype = str(option.get("tipo") or "ausente")
        option_types[otype] += 1
        if otype != "sem_opcao":
            actionable += 1
        if otype == "formula":
            discussion = neg.get("faixa_discussao_centavos")
            base = (option.get("base") or {}).get("valor_centavos")
            if neg.get("faixa_centavos") is None and discussion == [0, base]:
                broad_formula = True

    if negotiation_states.get("retida_pela_auditoria"):
        reasons.append("OPCAO_RETIDA_PELA_AUDITORIA")
    if not items or evaluation.get("execucao_valida") is not True:
        reasons.append("PAINEL_SEM_COBERTURA_VALIDA")
    if reasons:
        label = "INSATISFATORIO_CONTEUDO"
    else:
        if actionable == 0:
            reasons.append("SEM_OPCAO_ACIONAVEL")
        if broad_formula:
            reasons.append("FORMULA_COM_ENVELOPE_ZERO_A_CEM")
        if actionable and all(t in {"diligencia", "sem_opcao"} for t in option_types):
            reasons.append("SOMENTE_DILIGENCIA")
        if negotiation_states.get("sem_opcao"):
            reasons.append("HA_PEDIDO_SEM_OPCAO")
        label = "REVISAR_UTILIDADE" if reasons else "SATISFATORIO_AUTOMATICO"

    return {
        "label": label,
        "satisfatorio": label == "SATISFATORIO_AUTOMATICO",
        "motivos": sorted(set(reasons)),
        "pedidos": len(items),
        "status_pedidos": dict(sorted(statuses.items())),
        "tipos_opcao": dict(sorted(option_types.items())),
        "estados_negociacao": dict(sorted(negotiation_states.items())),
        "observacao": "triagem operacional; alinhamento semantico ao gabarito requer revisao posterior",
    }


def classify_failure(tx_summary):
    reason = ("CONSENSO_MAJORITY_DISAGREE" if tx_summary.get("result_name") == "MAJORITY_DISAGREE"
              else "TRANSACAO_SEM_SUCESSO_CONFIRMADO")
    return {
        "label": "INSATISFATORIO_TECNICO",
        "satisfatorio": False,
        "motivos": [reason],
        "pedidos": 0,
        "status_pedidos": {},
        "tipos_opcao": {},
        "estados_negociacao": {},
        "observacao": "triagem operacional; nenhuma conclusao de merito foi inferida",
        "status_transacao": tx_summary.get("status"),
        "execucao": tx_summary.get("exec"),
    }


def committed_success(tx):
    """Execucao do lider so grava estado quando o consenso tambem aprova."""
    return successful(tx) and tx.get("result_name") == "MAJORITY_AGREE"


def result_files(out):
    return sorted((Path(out) / "results").glob("[0-9][0-9][0-9][0-9].json"))


def render_report(out, manifest):
    results = [read_json(p) for p in result_files(out)]
    labels = Counter(r["impressao"]["label"] for r in results)
    statuses = Counter(r["transacao"].get("status") for r in results)
    origins = defaultdict(Counter)
    categories = defaultdict(Counter)
    diagnostics = Counter()
    rotations = 0
    for result in results:
        label = result["impressao"]["label"]
        origins[result.get("origem") or "desconhecida"][label] += 1
        categories[result.get("categoria") or "desconhecida"][label] += 1
        rotations += int(result["transacao"].get("rotacoes") or 0)
        for entry in result["transacao"].get("diagnosticos") or []:
            diagnostics.update(entry.get("codes") or [])

    total = len(manifest["case_ids"])
    done = len(results)
    summary_obj = {
        "schema_version": SCHEMA_VERSION,
        "updated_at": utc_now(),
        "version": manifest["version"],
        "contract": manifest["contract"],
        "processed": done,
        "total": total,
        "remaining": total - done,
        "labels": {label: labels.get(label, 0) for label in LABELS},
        "transaction_status": dict(sorted(statuses.items(), key=lambda pair: str(pair[0]))),
        "rotations": rotations,
        "diagnostics": dict(sorted(diagnostics.items())),
    }
    if manifest.get("closed_at"):
        summary_obj.update(
            closed_at=manifest["closed_at"],
            closed_after=manifest.get("closed_after", done),
            close_reason=manifest.get("close_reason"),
        )
    write_json(Path(out) / "summary.json", summary_obj)

    impressions = []
    cases_log = []
    for result in results:
        impressions.append(json.dumps({
            "id": result["id"], "origem": result.get("origem"),
            "categoria": result.get("categoria"), **result["impressao"],
        }, ensure_ascii=False, sort_keys=True))
        cases_log.append(json.dumps(result, ensure_ascii=False, sort_keys=True))
    atomic_text(Path(out) / "impressions.jsonl", "\n".join(impressions) + ("\n" if impressions else ""))
    atomic_text(Path(out) / "cases.jsonl", "\n".join(cases_log) + ("\n" if cases_log else ""))

    lines = [
        "# Fase 2 — relatório cumulativo",
        "",
        f"Atualizado em `{summary_obj['updated_at']}`. IC `{manifest['version']}` no contrato `{manifest['contract']}`.",
        "",
        f"Progresso: **{done}/{total}** casos; **{labels.get('SATISFATORIO_AUTOMATICO', 0)}** satisfatórios na triagem automática estrita.",
        "",
        "## Como interpretar",
        "",
        "`SATISFATORIO_AUTOMATICO` exige FINALIZED/SUCCESS com MAJORITY_AGREE, Termo íntegro, painel completo, ao menos uma opção acionável, nenhuma opção retida e nenhuma fórmula cujo único envelope seja 0%–100%. `REVISAR_UTILIDADE` indica execução válida, mas utilidade ainda ampla ou dependente de diligência. A classificação não certifica acerto jurídico; os gabaritos não são enviados ao IC e o alinhamento semântico será revisto após a campanha.",
        "",
        "## Totais",
        "",
        "| Classificação | Casos |",
        "|---|---:|",
    ]
    if manifest.get("closed_at"):
        lines[6:6] = [
            f"Campanha encerrada após **{manifest.get('closed_after', done)}** casos: {manifest.get('close_reason', 'motivo não informado')}.",
            "",
        ]
    lines += [f"| {label} | {labels.get(label, 0)} |" for label in LABELS]
    lines += ["", f"Rotações totais: **{rotations}**.", "", "## Por origem", "", "| Origem | Processados | Satisfatórios | Revisar | Conteúdo | Técnico |", "|---|---:|---:|---:|---:|---:|"]
    for origin, counts in sorted(origins.items()):
        lines.append(f"| {origin} | {sum(counts.values())} | {counts['SATISFATORIO_AUTOMATICO']} | {counts['REVISAR_UTILIDADE']} | {counts['INSATISFATORIO_CONTEUDO']} | {counts['INSATISFATORIO_TECNICO']} |")
    lines += ["", "## Impressão por caso", "", "| Caso | Origem | Categoria | Transação | Impressão | Motivos | Termo |", "|---|---|---|---|---|---|---|"]
    for result in results:
        imp = result["impressao"]
        reasons = ", ".join(imp["motivos"]) or "—"
        term = f"[Termo](terms/{result['id']}.md)" if result.get("termo") else "—"
        lines.append(f"| {result['id']} | {result.get('origem', '—')} | {result.get('categoria', '—')} | {result['transacao'].get('status', '—')}/{result['transacao'].get('exec', '—')} | {imp['label']} | {reasons} | {term} |")
    if diagnostics:
        lines += ["", "## Diagnósticos seguros", ""]
        lines += [f"- `{code}`: {count}" for code, count in sorted(diagnostics.items())]
    lines += ["", "## Arquivos", "", "- `events.jsonl`: log operacional append-only.", "- `cases.jsonl`: registro consolidado de cada rodada concluída.", "- `impressions.jsonl`: impressão automática compacta por caso.", "- `receipts/`, `states/` e `terms/`: evidências locais sanitizadas.", ""]
    atomic_text(Path(out) / "report.md", "\n".join(lines))
    return summary_obj


class Phase2:
    def __init__(self, studio, out, poll=15, timeout=3600):
        self.s = studio
        self.out = Path(out)
        self.poll = poll
        self.timeout = timeout
        self.path = self.out / "phase2.json"
        self.m = read_json(self.path) if self.path.exists() else None
        if self.m and (self.m["account"].lower() != self.s.account.address.lower()
                       or self.m["chain_id"] != self.s.chain_id):
            raise CycleError("Conta/rede diferem da campanha registrada")

    def save(self):
        self.m["updated_at"] = utc_now()
        write_json(self.path, self.m)

    def initialize(self, dataset, source, contract, maximum, delay, selected=None):
        if self.m:
            raise CycleError("Campanha ja inicializada; use run/resume")
        ids = discover_cases(dataset, maximum, selected)
        code = Path(source).read_bytes()
        version = version_of(code)
        digest = sha(code)
        methods = self.s.client.get_contract_schema(contract).get("methods", {})
        if not {"analyze_case", "get_case", "get_termo_opcao", "get_version", "get_code_hash"} <= set(methods):
            raise CycleError("Contrato sem interface exigida para a Fase 2")
        if self.s.read(contract, "get_version") != version or self.s.read(contract, "get_code_hash") != digest:
            raise CycleError("Versao/hash remoto nao correspondem ao candidato congelado")
        snapshot = self.out / (version + ".py")
        snapshot.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if snapshot.exists() and snapshot.read_bytes() != code:
            raise CycleError("Snapshot imutavel ja existe com outro conteudo")
        if not snapshot.exists():
            with snapshot.open("xb") as handle:
                handle.write(code)
        dataset_abs = str(Path(dataset).resolve())
        self.m = {
            "schema_version": SCHEMA_VERSION,
            "phase": "phase2-multicase",
            "account": self.s.account.address,
            "chain_id": self.s.chain_id,
            "endpoint": self.s.endpoint,
            "contract": contract,
            "version": version,
            "sha256": digest,
            "snapshot": snapshot.name,
            "dataset": dataset_abs,
            "case_ids": ids,
            "delay_seconds": delay,
            "send_attempts": 0,
            "next_send_at": 0,
            "started_at": utc_now(),
            "cases": {cid: {"state": "queued", "send_attempts": 0} for cid in ids},
        }
        self.save()
        append_event(self.out, "campaign_initialized", total=len(ids), version=version)
        render_report(self.out, self.m)

    def verify_identity(self):
        snapshot = self.out / self.m["snapshot"]
        if not snapshot.is_file() or sha(snapshot.read_bytes()) != self.m["sha256"]:
            raise CycleError("Snapshot congelado ausente ou alterado")
        if self.s.read(self.m["contract"], "get_version") != self.m["version"]:
            raise CycleError("Versao remota mudou; campanha pausada")
        if self.s.read(self.m["contract"], "get_code_hash") != self.m["sha256"]:
            raise CycleError("Hash remoto mudou; campanha pausada")

    def wait_delay(self):
        while True:
            remaining = float(self.m.get("next_send_at") or 0) - time.time()
            if remaining <= 0:
                return
            time.sleep(min(remaining, 15))

    def submit(self, cid, row):
        if row["state"] != "queued" or row["send_attempts"]:
            raise CycleError("Caso ja teve tentativa de envio; retomar sem reenviar")
        self.wait_delay()
        row.update(state="sending", started_at=utc_now(), started_epoch=time.time(), send_attempts=1)
        self.m["send_attempts"] += 1
        self.save()
        append_event(self.out, "send_started", case_id=cid, attempt=self.m["send_attempts"])

        def before():
            row["broadcast_started"] = True
            self.save()

        def after(value):
            row["evm_hash"] = tx_hash(value)
            self.save()

        self.s.before_send, self.s.after_send = before, after
        try:
            result = self.s.client.write_contract(
                address=self.m["contract"], function_name="analyze_case",
                args=[str(int(cid))], account=self.s.account,
            )
            row["hash"] = tx_hash(result)
            row["state"] = "pending"
            self.save()
            append_event(self.out, "send_accepted", case_id=cid, tx=row["hash"])
        except BaseException as exc:
            row.update(state="uncertain", error_type=type(exc).__name__)
            self.save()
            append_event(self.out, "send_uncertain", case_id=cid, error_type=type(exc).__name__)
            raise
        finally:
            self.s.before_send = self.s.after_send = None

    def wait_transaction(self, cid, row):
        if not row.get("hash"):
            if not row.get("evm_hash"):
                raise CycleError("Envio incerto sem hash; nao repetir automaticamente")
            row["hash"] = self.s.recover_hash(row["evm_hash"])
            row["state"] = "pending"
            self.save()
            append_event(self.out, "hash_recovered", case_id=cid, tx=row["hash"])
        started = time.monotonic()
        last = row.get("last_status")
        while True:
            tx = self.s.receipt(row["hash"])
            if isinstance(tx, dict):
                receipt_rel = "receipts/" + cid + "-" + row["hash"][2:] + ".json"
                write_json(self.out / receipt_rel, tx)
                row["receipt"] = receipt_rel
                current = status_de(tx)
                if current != last:
                    row["last_status"] = current
                    self.save()
                    append_event(self.out, "status_changed", case_id=cid, status=current, execution=execution(tx))
                    last = current
                if current in FINAL:
                    row.update(
                        state="finalizing", terminal_at=utc_now(),
                        terminal_epoch=time.time(), tx_summary=summary(tx),
                        elapsed_seconds=round(time.time() - float(row.get("started_epoch") or time.time()), 2),
                    )
                    self.m["next_send_at"] = time.time() + float(self.m["delay_seconds"])
                    self.save()
                    append_event(self.out, "transaction_terminal", case_id=cid,
                                 status=current, execution=execution(tx))
                    return tx
            if time.monotonic() - started >= self.timeout:
                self.save()
                append_event(self.out, "wait_timeout", case_id=cid)
                raise CycleError("Timeout de observacao; campanha pausada sem novo envio")
            time.sleep(self.poll)

    def finalize(self, cid, row):
        result_path = self.out / "results" / (cid + ".json")
        if result_path.exists():
            row.update(state="done", result=str(result_path.relative_to(self.out)))
            self.save()
            render_report(self.out, self.m)
            return
        tx = read_json(self.out / row["receipt"])
        tx_summary = row.get("tx_summary") or summary(tx)
        case = load_case(self.m["dataset"], cid)
        result = {
            "id": cid,
            "origem": case.get("origem"),
            "categoria": case.get("categoria"),
            "version": self.m["version"],
            "transaction_hash": row["hash"],
            "elapsed_seconds": row.get("elapsed_seconds"),
            "transacao": tx_summary,
            "completed_at": row.get("terminal_at"),
            "benchmark_semantico": "PENDENTE_REVISAO_POSTERIOR",
        }
        if committed_success(tx):
            state = decode_state(self.s.read(self.m["contract"], "get_case"))
            term = self.s.read(self.m["contract"], "get_termo_opcao")
            if term != state.get("termo_opcao"):
                raise CycleError("Getters devolveram documentos diferentes")
            assessment = evaluate(state, self.m["version"], cid)
            state_rel = "states/" + cid + ".json"
            term_rel = "terms/" + cid + ".md"
            write_json(self.out / state_rel, state)
            atomic_text(self.out / term_rel, term)
            result.update(estado=state_rel, termo=term_rel, avaliacao=assessment,
                          impressao=classify_success(state, assessment))
        else:
            result.update(estado=None, termo=None, avaliacao=None,
                          impressao=classify_failure(tx_summary))
        write_json(result_path, result)
        row.update(state="done", result=str(result_path.relative_to(self.out)),
                   impression=result["impressao"]["label"])
        self.save()
        append_event(self.out, "case_completed", case_id=cid,
                     impression=result["impressao"]["label"])
        render_report(self.out, self.m)

    def run(self, stop_after=0):
        if not self.m:
            raise CycleError("Campanha inexistente; use init")
        if self.m.get("closed_at"):
            raise CycleError("Campanha encerrada: " + self.m.get("close_reason", "sem motivo registrado"))
        self.verify_identity()
        completed_this_run = 0
        for cid in self.m["case_ids"]:
            row = self.m["cases"][cid]
            if row["state"] == "done":
                continue
            if row["state"] == "queued":
                self.submit(cid, row)
            if row["state"] in {"sending", "uncertain", "pending"}:
                self.wait_transaction(cid, row)
            if row["state"] == "finalizing":
                self.finalize(cid, row)
                completed_this_run += 1
            if stop_after and completed_this_run >= stop_after:
                break
        if all(row["state"] == "done" for row in self.m["cases"].values()):
            self.m["completed_at"] = self.m.get("completed_at") or utc_now()
            self.save()
            append_event(self.out, "campaign_completed", total=len(self.m["case_ids"]))
        return render_report(self.out, self.m)


def local_status(out):
    out = Path(out)
    manifest = read_json(out / "phase2.json")
    counts = Counter(row["state"] for row in manifest["cases"].values())
    report = read_json(out / "summary.json") if (out / "summary.json").exists() else render_report(out, manifest)
    return {"states": dict(sorted(counts.items())), **report}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("init", "run", "resume", "status", "report", "close"))
    p.add_argument("--out", default="res_phase2_v17")
    p.add_argument("--key-file")
    p.add_argument("--dataset", default=".")
    p.add_argument("--source", default="ic_experimental.py")
    p.add_argument("--contract", default=DEFAULT_CONTRACT)
    p.add_argument("--max-cases", type=int)
    p.add_argument("--case-ids-file")
    p.add_argument("--delay", type=float, default=15)
    p.add_argument("--poll", type=float, default=15)
    p.add_argument("--timeout", type=float, default=3600)
    p.add_argument("--stop-after", type=int, default=0)
    p.add_argument("--reason", help="motivo obrigatorio para encerrar a campanha")
    p.add_argument("--execute", action="store_true")
    return p


def main():
    args = parser().parse_args()
    if args.action in {"status", "report", "close"}:
        manifest = read_json(Path(args.out) / "phase2.json")
        if args.action == "close":
            if not args.reason or not args.reason.strip():
                raise CycleError("close exige --reason")
            active = [cid for cid, row in manifest["cases"].items()
                      if row["state"] in {"sending", "uncertain", "pending", "finalizing"}]
            if active:
                raise CycleError("Nao encerrar com caso ativo: " + active[0])
            if not manifest.get("closed_at"):
                done = sum(row["state"] == "done" for row in manifest["cases"].values())
                manifest.update(closed_at=utc_now(), closed_after=done,
                                close_reason=args.reason.strip())
                write_json(Path(args.out) / "phase2.json", manifest)
                append_event(args.out, "campaign_closed", completed=done,
                             reason=args.reason.strip())
                render_report(args.out, manifest)
        value = local_status(args.out) if args.action == "status" else render_report(args.out, manifest)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return
    if not args.execute or not args.key_file:
        raise CycleError("init/run/resume exigem --execute e --key-file")
    if args.delay < 15:
        raise CycleError("Campanhas Studio exigem delay minimo de 15 segundos")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = (out / "phase2.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise CycleError("Outro processo da Fase 2 ja esta ativo") from exc
    studio = Studio(args.key_file)
    campaign = Phase2(studio, out, poll=args.poll, timeout=args.timeout)
    if args.action == "init":
        selected = None
        if args.case_ids_file:
            selected_obj = read_json(args.case_ids_file)
            selected = selected_obj.get("case_ids") if isinstance(selected_obj, dict) else selected_obj
            if not isinstance(selected, list) or not all(isinstance(cid, str) for cid in selected):
                raise CycleError("Arquivo de selecao deve ser array ou objeto com case_ids")
        maximum = args.max_cases if args.max_cases is not None else (len(selected) if selected else 500)
        if selected is None and maximum != 500:
            raise CycleError("Campanha parcial exige --case-ids-file explicito")
        if not 1 <= maximum <= 500:
            raise CycleError("Quantidade de casos deve ficar entre 1 e 500")
        campaign.initialize(args.dataset, args.source, args.contract, maximum, args.delay, selected)
        print(json.dumps(local_status(out), ensure_ascii=False, indent=2))
        return
    pid_path = out / "runner.pid"
    atomic_text(pid_path, str(os.getpid()) + "\n")
    try:
        result = campaign.run(stop_after=args.stop_after)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        if pid_path.exists() and pid_path.read_text().strip() == str(os.getpid()):
            pid_path.unlink()


if __name__ == "__main__":
    try:
        main()
    except CycleError as exc:
        print("PHASE2_ERROR:" + str(exc), file=os.sys.stderr)
        raise SystemExit(2)
    except BaseException as exc:
        # Somente o tipo: mensagens de SDK/RPC podem carregar node_config sensivel.
        print("PHASE2_UNEXPECTED:" + type(exc).__name__, file=os.sys.stderr)
        raise SystemExit(3)
