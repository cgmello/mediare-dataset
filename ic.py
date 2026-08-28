# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

# v5: principle sem a condicao de igualdade das listas "divergencias"
# (era a condicao mais fragil: binario ~50/50 derivado de sorteio de LLM)
import json

DATASET_BASE = ("https://raw.githubusercontent.com/cgmello/mediare-dataset/"
                "6bf13ae581afd08415c54d0d825543c21e34bff5/casos/")

# ---------------------------------------------------------------- regras (a)-(i)
# So entra aqui o que e assentado. Nada que uma lente devesse poder decidir.
REGRAS = (
    "REGRAS OBRIGATORIAS:\n"
    "(a) use exatamente as chaves de valor: principal, multa, danos_morais, outros.\n"
    "    'principal' = o pedido principal (reparo do bem, divida, valor do contrato).\n"
    "    'outros'    = demais rubricas pecuniarias (lucros cessantes, juros,\n"
    "                  despesas, restituicoes).\n"
    "    NUNCA some duas rubricas numa mesma chave. Se conceder lucros cessantes,\n"
    "    eles vao em 'outros', jamais somados dentro de 'principal'.\n"
    "(b) 'parcial_ambos' so quando requerente E requerido contribuiram para o dano.\n"
    "(c) 'responsavel' e a parte OBRIGADA a pagar, nao a parte que errou moralmente.\n"
    "(d) nao aplique reducao por equidade - isso e prerrogativa do mediador humano.\n"
    "(e) orcamentos de reparo SAO prova valida de dano material.\n"
    "(f) valores = total devido. Limite de apolice de seguro NAO altera o valor,\n"
    "    e materia de execucao. Nunca limite o valor ao saldo da apolice.\n"
    "(g) coerencia: se todas as rubricas sao 0, o resultado e 'improcedente'.\n"
    "(h) varios reus = 'requerido'. Solidariedade nao e culpa concorrente.\n"
    "(i) NAO faca contas de proporcao, media ou rateio. Informe o valor cheio\n"
    "    de cada rubrica que voce considera devida, e 0.0 para as negadas.\n"
)

# ---------------------------------------------------------------- as tres lentes
# Diferem em METODOLOGIA PROBATORIA, nao em qual lado defendem. Onde a lei nao da
# margem, convergem; onde ha discricionariedade real, divergem - e e isso que
# queremos capturar. O padrao para lucro cessante mora AQUI, nao nas REGRAS.
LENTES = [
    ("estrita",
     "Voce aplica o padrao probatorio ESTRITO: so concede rubrica que esteja "
     "documentalmente comprovada de forma direta e integral. Na duvida sobre a "
     "extensao do dano, nega a rubrica. Para lucro cessante ou perda de renda, "
     "exija prova do prejuizo LIQUIDO (extratos de receita, declaracoes fiscais, "
     "comprovantes de repasse); diaria bruta e tempo de imobilizacao nao bastam."),
    ("ampla",
     "Voce aplica o padrao probatorio AMPLO: concede a rubrica quando os documentos "
     "tornam o dano razoavelmente demonstrado, admitindo inferencia logica a partir "
     "do conjunto probatorio. Na duvida sobre a extensao, concede pelo valor pedido. "
     "Para lucro cessante ou perda de renda, basta a prova do periodo de "
     "imobilizacao e do valor contratual da diaria; o prejuizo liquido pode ser "
     "inferido do conjunto probatorio."),
    ("jurisprudencial",
     "Voce decide pelas presuncoes consolidadas na jurisprudencia brasileira "
     "(ex.: presuncao de culpa de quem colide na traseira, CTB art. 29 II; "
     "inversao do onus no CDC; boa-fe objetiva). Onde houver presuncao aplicavel, "
     "ela prevalece sobre a ausencia de prova direta."),
]

SCHEMA = (
    '{"responsavel": "requerente|requerido|ambos_culpa_concorrente|parcial_ambos", '
    '"resultado": "procedente|improcedente|parcialmente procedente", '
    '"valores": {"principal": 0.0, "multa": 0.0, "danos_morais": 0.0, "outros": 0.0}, '
    '"fundamentos": ["...", "..."]}'
)

RUBRICAS = ["principal", "multa", "outros"]   # danos_morais fica fora do EP


def _moda(vals: list) -> str:
    """Moda deterministica. Empate -> 'divergente'."""
    cont = {}
    for v in vals:
        cont[v] = cont.get(v, 0) + 1
    topo = max(cont.values())
    vencedores = sorted([k for k, v in cont.items() if v == topo])
    return vencedores[0] if len(vencedores) == 1 else "divergente"


def _consolidar(teses: list) -> dict:
    """TODA a agregacao e feita aqui, em Python. Nenhum LLM faz conta.

    A divergencia e medida pelo TOTAL, nao por rubrica: duas lentes que chegam
    ao mesmo montante discordando so de onde lancar cada parcela concordam.
    """
    faixas = {}
    for r in RUBRICAS:
        vs = [round(float(t["valores"].get(r, 0.0)), 2) for t in teses]
        faixas[r] = [min(vs), max(vs)]

    totais = [round(sum(float(t["valores"].get(r, 0.0)) for r in RUBRICAS), 2)
              for t in teses]
    lo, hi = min(totais), max(totais)

    divergencias = []
    if hi - lo > 0.01:
        divergencias.append("total")
    resp = _moda([t["responsavel"] for t in teses])
    resu = _moda([t["resultado"] for t in teses])
    if resp == "divergente":
        divergencias.append("responsavel")
    divergencias = sorted(set(divergencias))

    return {
        "responsavel_majoritario": resp,
        "resultado_majoritario": resu,
        "faixa_total": [lo, hi],
        "totais_por_lente": {t["lente"]: tot for t, tot in zip(teses, totais)},
        "faixas_por_rubrica": faixas,      # informativo; NAO gera divergencia
        "divergencias": divergencias,
        "unanime": len(divergencias) == 0,
        "n_teses": len(teses),
    }


class MediareCommittee(gl.Contract):
    case_id: str
    case_url: str
    status: str
    parecer: str      # painel completo (teses + consolidado)
    termo: str        # termo de acordo OU pauta de mediacao
    unanime: bool

    def __init__(self):
        self.case_id = ""
        self.case_url = ""
        self.status = "vazio"
        self.parecer = ""
        self.termo = ""
        self.unanime = False

    @gl.public.write
    def analyze_case(self, case_id: str):
        case_url = DATASET_BASE + case_id.zfill(4) + ".json"

        # ---------------- BLOCO 0: painel de teses -------------------------
        def painel() -> str:
            raw = gl.nondet.web.get(case_url).body.decode("utf-8")
            docs = json.loads(raw)["documentos"]
            corpo = json.dumps(docs, sort_keys=True, ensure_ascii=False)

            teses = []
            for nome, lente in LENTES:
                p = ("Voce e um mediador extrajudicial brasileiro (Lei 13.140/2015).\n"
                     + lente + "\n\n" + REGRAS
                     + "\nResponda SOMENTE com este JSON, sem markdown:\n" + SCHEMA
                     + "\n\nDOCUMENTOS DO CASO:\n" + corpo)
                bruto = gl.nondet.exec_prompt(p).strip()
                if bruto.startswith("```"):
                    bruto = bruto.split("```")[1]
                    if bruto.startswith("json"):
                        bruto = bruto[4:]
                ini, fim = bruto.find("{"), bruto.rfind("}")
                t = json.loads(bruto[ini:fim + 1])
                t["lente"] = nome
                t["valores"] = {k: round(float(t["valores"].get(k, 0.0)), 2)
                                for k in ["principal", "multa", "danos_morais", "outros"]}
                teses.append(t)

            teses.sort(key=lambda t: t["lente"])          # ordem estavel
            return json.dumps({"teses": teses, "consolidado": _consolidar(teses)},
                              sort_keys=True, ensure_ascii=False)

        parecer = gl.eq_principle.prompt_comparative(
            painel,
            principle=(
                "Compare os dois PAINEIS olhando SOMENTE o campo 'consolidado'. "
                "Considere equivalentes se TODAS estas condicoes valerem: "
                "(1) 'responsavel_majoritario' identico; "
                "(2) 'resultado_majoritario' identico, tratando 'procedente' e "
                "'parcialmente procedente' como equivalentes; "
                "(3) os dois intervalos 'faixa_total' SE SOBREPOEM (basta "
                "interseccao nao vazia, nao precisam coincidir); uma faixa [0,0] "
                "so equivale a outra [0,0]. "
                "IGNORE completamente: o array 'teses', o campo "
                "'faixas_por_rubrica', o campo 'totais_por_lente', a lista "
                "'divergencias', o campo 'unanime', a rubrica danos_morais, "
                "a redacao dos fundamentos e a ordem de qualquer lista. "
                "Em particular: um painel unanime e um painel divergente podem "
                "ser equivalentes, desde que as tres condicoes acima valham. "
                "Diferenca sobre EM QUAL RUBRICA um valor foi lancado nao "
                "e divergencia, desde que o total bata. "
                "Dois paineis cujas faixas compartilham valores descrevem a "
                "mesma disputa - e esse o objetivo."
            ),
        )

        painel_obj = json.loads(parecer)
        cons = painel_obj["consolidado"]
        unanime = bool(cons["unanime"])

        # ---------------- BLOCO 1: termo OU pauta --------------------------
        def contexto() -> str:
            raw = gl.nondet.web.get(case_url).body.decode("utf-8")
            return ("DOCUMENTOS DO CASO (JSON):\n" + raw
                    + "\n\nPAINEL DO COMITE (JSON):\n" + parecer)

        if unanime:
            tarefa = (
                "As tres lentes do comite convergiram. Redija o TERMO DE ACORDO "
                "EXTRAJUDICIAL em portugues. O valor devido e o de 'faixa_total'. "
                "Secoes obrigatorias, nesta ordem: 1 Qualificacao das partes "
                "(pseudonimizada); 2 Resumo do conflito; 3 Obrigacoes das partes "
                "com valores e prazos; 4 Quitacao; 5 Confidencialidade; "
                "6 Titulo executivo extrajudicial (CPC art. 784, III); "
                "7 Assinaturas. Responda so o documento, sem comentarios."
            )
            criterios = (
                "Aprove se o texto: contem as 7 secoes na ordem; usa como valor "
                "devido o montante de 'faixa_total'; cita o art. 784, III do CPC; "
                "nao inventa nome real de pessoa ou empresa. NAO avalie estilo, "
                "extensao ou elegancia da redacao."
            )
        else:
            tarefa = (
                "As tres lentes do comite DIVERGIRAM. NAO redija termo de acordo. "
                "Redija uma PAUTA DE MEDIACAO em portugues para o mediador humano, "
                "com: 1 Resumo do conflito; 2 O que ja esta pacificado entre as "
                "tres lentes; 3 Cada ponto listado em 'divergencias', usando "
                "'faixa_total' e 'totais_por_lente' para mostrar quanto cada lente "
                "arbitrou no total e por que; 4 A pergunta objetiva que o mediador "
                "precisa decidir em cada ponto. "
                "IMPORTANTE: compare as lentes SEMPRE pelo total. Se duas lentes "
                "chegaram ao mesmo total lancando as parcelas em rubricas "
                "diferentes, elas CONCORDAM - nao apresente isso como divergencia "
                "nem faca pergunta ao mediador sobre em qual rubrica lancar valor. "
                "Responda so o documento, sem comentarios."
            )
            criterios = (
                "Aprove se o texto: NAO contem clausula de quitacao nem valor "
                "unico fechado; cobre todos os itens de 'divergencias'; mostra "
                "para cada um o intervalo de totais e os argumentos opostos; "
                "termina com perguntas objetivas ao mediador; e NAO pergunta ao "
                "mediador em qual rubrica lancar um valor. NAO avalie estilo."
            )

        termo = gl.eq_principle.prompt_non_comparative(
            contexto, task=tarefa, criteria=criterios)

        t = termo.strip()
        if t.startswith("{"):
            try:
                termo = list(json.loads(t).values())[0]
            except Exception:
                pass

        self.case_id = case_id
        self.case_url = case_url
        self.parecer = parecer
        self.termo = termo
        self.unanime = unanime
        self.status = "concluido" if unanime else "divergente"

    @gl.public.view
    def get_case(self) -> str:
        return json.dumps({
            "case_id": self.case_id,
            "case_url": self.case_url,
            "status": self.status,
            "unanime": self.unanime,
            "parecer": self.parecer,
            "termo": self.termo,
        }, ensure_ascii=False)
