# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

# v8: (j) coerencia responsavel x valores — reparticao tem de chegar ao
#     numero, nao so ao texto; e a lente estrita nao zera rubrica quando a
#     duvida e de extensao, so quando falta o dano ou o nexo.
# v7: principle trata parcial_ambos == ambos_culpa_concorrente. Medido no
#     caso 0005 (tx 0x62b24377, UNDETERMINED apos 3 rotacoes): os 4 lideres
#     concordavam no merito e discordavam so do rotulo da mesma categoria.
# v6: (1) regra (d) permite rateio comprovado (culpa concorrente e merito,
#         nao equidade); (2) _moda nunca devolve "divergente" - desempate
#         deterministico por lente, empate vai para o campo informativo.
# v5: principle sem a condicao de igualdade das listas "divergencias".
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
    "(d) NAO reduza valores por equidade, simpatia ou razoabilidade arbitraria.\n"
    "    MAS, quando os documentos comprovarem culpa concorrente ou\n"
    "    responsabilidade repartida, informe o valor QUE CABE A PARTE\n"
    "    RESPONSAVEL, nao o custo integral (ex.: se a reparticao apurada\n"
    "    e 50/50 sobre um custo de 100, o valor devido e 50).\n"
    "    Rateio apurado nos documentos e materia de MERITO, nao equidade.\n"
    "(e) orcamentos de reparo SAO prova valida de dano material.\n"
    "(f) valores = total devido. Limite de apolice de seguro NAO altera o valor,\n"
    "    e materia de execucao. Nunca limite o valor ao saldo da apolice.\n"
    "(g) coerencia: se todas as rubricas sao 0, o resultado e 'improcedente'.\n"
    "(h) varios reus = 'requerido'. Solidariedade nao e culpa concorrente.\n"
    "(i) NAO invente proporcoes nem faca media entre cenarios possiveis.\n"
    "    Informe o valor de cada rubrica que voce considera devida e 0.0\n"
    "    para as negadas.\n"
    "(j) COERENCIA entre 'responsavel' e 'valores': se 'responsavel' for\n"
    "    'parcial_ambos' ou 'ambos_culpa_concorrente', os valores DEVEM\n"
    "    refletir a reparticao — informe a parcela que cabe a parte\n"
    "    responsavel, nunca o custo integral. Se os documentos comprovarem\n"
    "    a reparticao mas nao permitirem apurar a proporcao exata, use 50/50.\n"
    "    Concluir 'responsabilidade repartida' e reportar o valor integral e\n"
    "    contradicao: o painel sera considerado incoerente.\n"
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
     "comprovantes de repasse); diaria bruta e tempo de imobilizacao nao bastam. "
     "ATENCAO: seu rigor incide sobre a EXTENSAO do dano, nao sobre a "
     "EXISTENCIA da obrigacao. Se o dano esta comprovado e a duvida e apenas "
     "sobre quanto cabe a cada parte, NAO zere a rubrica: conceda a parcela "
     "que o lastro documental sustenta. Zerar so quando faltar prova do "
     "proprio dano ou do nexo causal."),
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


# ordem de prioridade para desempate; a lente jurisprudencial tem a palavra
# final porque decide por presuncoes assentadas, nao por leitura de prova.
DESEMPATE = ["jurisprudencial", "estrita", "ampla"]


def _reparar_json(s: str) -> str:
    """Conserta os dois defeitos que o modelo comete dentro de strings JSON:
    aspas nao escapadas e quebras de linha cruas. Uma aspa so fecha a string
    se o proximo caractere nao-espaco for , : } ou ] - caso contrario e aspa
    interna e vira \\". Nao inventa estrutura: se a resposta estiver mesmo
    quebrada, o parse falha depois e a lente e descartada."""
    fora = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}
    out = []
    dentro = False
    esc = False
    n = len(s)
    for k in range(n):
        ch = s[k]
        if esc:
            out.append(ch); esc = False; continue
        if ch == "\\":
            out.append(ch); esc = True; continue
        if ch == '"':
            if not dentro:
                dentro = True; out.append(ch); continue
            j = k + 1
            while j < n and s[j] in " \t\r\n":
                j += 1
            if j >= n or s[j] in ",:}]":
                dentro = False; out.append(ch)
            else:
                out.append('\\"')
            continue
        if dentro and ch in fora:
            out.append(fora[ch]); continue
        out.append(ch)
    return "".join(out)


def _json_do_modelo(bruto: str):
    """Extrai UM objeto JSON da resposta. Devolve None se nao der.

    json.loads(bruto[primeiro'{':ultimo'}']) - o que estava aqui antes -
    quebra quando o modelo escreve qualquer coisa depois do objeto ou uma
    aspa dentro de um fundamento. Duas transacoes do lote v8 morreram assim
    (exit_code 1), e um crash vira consenso sobre nada: os validadores
    reproduzem o mesmo erro e a rede ACEITA a falha.
    """
    b = bruto.strip()
    if "```" in b:
        partes = [p for p in b.split("```") if "{" in p]
        if partes:
            b = max(partes, key=len).lstrip()
            if b.startswith("json"):
                b = b[4:]
    i = b.find("{")
    if i < 0:
        return None
    b = b[i:]
    dec = json.JSONDecoder()
    for tentativa in (b, _reparar_json(b)):
        try:
            obj, _fim = dec.raw_decode(tentativa)   # UM objeto, ignora o resto
            if isinstance(obj, dict):
                return obj
        except ValueError:
            continue
    return None


def _num(x) -> float:
    """Converte para float sem nunca estourar. O modelo as vezes manda numero
    como string, com R$, ponto de milhar e virgula decimal ("R$ 1.234,56").
    float() nesses casos levanta ValueError - e ValueError dentro do painel
    derruba a transacao inteira."""
    if isinstance(x, (int, float)):
        return float(x)
    if not isinstance(x, str):
        return 0.0
    t = x.strip().replace("R$", "").replace(" ", "").replace("\u00a0", "")
    if not t:
        return 0.0
    if "," in t:                       # formato brasileiro: 1.234,56
        t = t.replace(".", "").replace(",", ".")
    t = "".join(c for c in t if c in "0123456789.-")
    try:
        return float(t)
    except ValueError:
        return 0.0


def _tese_valida(t) -> bool:
    return (isinstance(t, dict) and isinstance(t.get("valores"), dict)
            and t.get("responsavel") is not None
            and t.get("resultado") is not None)


def _moda(teses: list, campo: str):
    """Moda deterministica -> (valor, houve_empate).

    NUNCA devolve 'divergente': esse valor era rejeicao automatica no EP,
    porque nenhum validador o reproduz de forma estavel. No empate, vence a
    lente de maior prioridade entre as empatadas; o empate vai para o campo
    'empates', informativo para o mediador e ignorado pelo principle.
    """
    cont = {}
    for t in teses:
        v = t[campo]
        cont[v] = cont.get(v, 0) + 1
    topo = max(cont.values())
    vencedores = [k for k, v in cont.items() if v == topo]
    if len(vencedores) == 1:
        return vencedores[0], False
    for lente in DESEMPATE:
        for t in teses:
            if t["lente"] == lente and t[campo] in vencedores:
                return t[campo], True
    return sorted(vencedores)[0], True


def _prompt_lente(lente: str, corpo: str) -> str:
    return ("Voce e um mediador extrajudicial brasileiro (Lei 13.140/2015).\n"
            + lente + "\n\n" + REGRAS
            + "\nResponda SOMENTE com este JSON, sem markdown:\n" + SCHEMA
            + "\n\nDOCUMENTOS DO CASO:\n" + corpo)


def _tese_de(pedir, nome: str, lente: str, corpo: str, tentativas: int = 2):
    """Uma tese, ou None se o modelo nao produzir JSON utilizavel.

    `pedir(prompt) -> str` e injetado: o contrato passa gl.nondet.exec_prompt e
    o harness passa a chamada da API. Assim os dois percorrem EXATAMENTE o
    mesmo caminho de prompt, parse e normalizacao.

    Foi a divergencia entre esses dois caminhos que deixou o bug do parser
    passar despercebido: o harness tinha extrair_json com raw_decode, o
    contrato tinha json.loads de uma fatia. Off-chain limpo, on-chain
    exit_code 1 - e crash de contrato vira consenso por maioria.
    """
    p = _prompt_lente(lente, corpo)
    for _ in range(tentativas):          # o bloco e nao deterministico mesmo:
        cand = _json_do_modelo(pedir(p))  # re-perguntar costuma resolver
        if _tese_valida(cand):
            cand["lente"] = nome
            cand["valores"] = {k: round(_num(cand["valores"].get(k, 0.0)), 2)
                               for k in ["principal", "multa", "danos_morais",
                                         "outros"]}
            return cand
    return None


def _painel_de(pedir, corpo: str) -> dict:
    """Painel completo: as tres lentes, as perdidas descartadas."""
    teses = []
    for nome, lente in LENTES:
        t = _tese_de(pedir, nome, lente, corpo)
        if t is not None:
            teses.append(t)
    teses.sort(key=lambda t: t["lente"])              # ordem estavel
    if not teses:
        # nenhuma lente respondeu JSON utilizavel. Painel vazio EXPLICITO em
        # vez de excecao: crash e reproduzido por todos os nos, aceito por
        # maioria, e vira "consenso" sobre nada.
        return {"teses": [], "consolidado": None,
                "erro": "nenhuma lente produziu JSON valido"}
    return {"teses": teses, "consolidado": _consolidar(teses)}


def _consolidar(teses: list) -> dict:
    """TODA a agregacao e feita aqui, em Python. Nenhum LLM faz conta.

    A divergencia e medida pelo TOTAL, nao por rubrica: duas lentes que chegam
    ao mesmo montante discordando so de onde lancar cada parcela concordam.
    """
    faixas = {}
    for r in RUBRICAS:
        vs = [round(_num(t["valores"].get(r, 0.0)), 2) for t in teses]
        faixas[r] = [min(vs), max(vs)]

    totais = [round(sum(_num(t["valores"].get(r, 0.0)) for r in RUBRICAS), 2)
              for t in teses]
    lo, hi = min(totais), max(totais)

    divergencias = []
    if hi - lo > 0.01:
        divergencias.append("total")
    resp, resp_empate = _moda(teses, "responsavel")
    resu, resu_empate = _moda(teses, "resultado")
    # discordancia sobre QUEM paga e divergencia de merito: vai para a pauta.
    if len(set(t["responsavel"] for t in teses)) > 1:
        divergencias.append("responsavel")
    divergencias = sorted(set(divergencias))
    empates = sorted([c for c, e in (("responsavel", resp_empate),
                                     ("resultado", resu_empate)) if e])

    return {
        "responsavel_majoritario": resp,
        "resultado_majoritario": resu,
        "faixa_total": [lo, hi],
        "totais_por_lente": {t["lente"]: tot for t, tot in zip(teses, totais)},
        "faixas_por_rubrica": faixas,      # informativo; NAO gera divergencia
        "responsavel_por_lente": {t["lente"]: t["responsavel"] for t in teses},
        "empates": empates,          # informativo; o principle ignora
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

            painel_obj = _painel_de(gl.nondet.exec_prompt, corpo)
            return json.dumps(painel_obj, sort_keys=True, ensure_ascii=False)

        parecer = gl.eq_principle.prompt_comparative(
            painel,
            principle=(
                "Compare os dois PAINEIS olhando SOMENTE o campo 'consolidado'. "
                "Considere equivalentes se TODAS estas condicoes valerem: "
                "(1) 'responsavel_majoritario' identico, tratando "
                "'parcial_ambos' e 'ambos_culpa_concorrente' como EQUIVALENTES "
                "(os dois significam responsabilidade repartida entre as partes); "
                "(2) 'resultado_majoritario' identico, tratando 'procedente' e "
                "'parcialmente procedente' como equivalentes; "
                "(3) os dois intervalos 'faixa_total' SE SOBREPOEM (basta "
                "interseccao nao vazia, nao precisam coincidir); uma faixa [0,0] "
                "so equivale a outra [0,0]. "
                "IGNORE completamente: o array 'teses', o campo "
                "'faixas_por_rubrica', o campo 'totais_por_lente', a lista "
                "'divergencias', o campo 'unanime', o campo 'empates', o campo "
                "'responsavel_por_lente', a rubrica danos_morais, "
                "a redacao dos fundamentos e a ordem de qualquer lista. "
                "Em particular: um painel unanime e um painel divergente podem "
                "ser equivalentes, desde que as tres condicoes acima valham. "
                "Diferenca sobre EM QUAL RUBRICA um valor foi lancado nao "
                "e divergencia, desde que o total bata. "
                "Dois paineis cujas faixas compartilham valores descrevem a "
                "mesma disputa - e esse o objetivo. "
                "EXCECAO: se em QUALQUER um dos dois paineis o campo "
                "'consolidado' for null, os paineis NAO sao equivalentes - "
                "um painel sem consolidado nao pode virar pauta."
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
