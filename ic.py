# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

DATASET_BASE = (
    "https://raw.githubusercontent.com/cgmello/mediare-dataset/"
    "6bf13ae581afd08415c54d0d825543c21e34bff5/casos/"
)


class MediareCommittee(gl.Contract):
    """
    Mediare - AI committee for extrajudicial mediation.
    analyze_case(case_id):
      reads DATASET_BASE + case_id + ".json"
      round 1 -> structured opinion (comparative equivalence principle)
      round 2 -> settlement draft   (non-comparative equivalence principle)
    If the human mediator wants changes, the platform publishes a new immutable
    snapshot of the case (e.g. id "0002-v2") and calls again with the new id.
    """

    case_id: str
    case_url: str
    status: str
    parecer: str
    termo: str

    def __init__(self):
        self.case_id = ""
        self.case_url = ""
        self.status = "vazio"
        self.parecer = ""
        self.termo = ""

    @gl.public.write
    def analyze_case(self, case_id: str):
        case_url = DATASET_BASE + case_id.zfill(4) + ".json"

        # ---------- ROUND 1: structured opinion (comparative EP) ----------
        def leader_analysis() -> str:
            raw_case = gl.nondet.web.get(case_url).body.decode("utf-8")
            docs = json.loads(raw_case)["documentos"]
            pet = docs["peticao_requerente"]
            doc_req = docs["documentos_requerente"]
            resp = docs["resposta_requerido"]
            doc_res = docs["documentos_requerido"]
            prompt = (
                "Voce e um analista juridico de uma camara de mediacao "
                "extrajudicial brasileira. Analise os documentos das DUAS partes "
                "e produza um parecer imparcial.\n\n"
                "PETICAO DO REQUERENTE:\n" + pet + "\n\n"
                "DOCUMENTOS DO REQUERENTE:\n" + doc_req + "\n\n"
                "RESPOSTA DO REQUERIDO:\n" + resp + "\n\n"
                "DOCUMENTOS DO REQUERIDO:\n" + doc_res + "\n\n"
                "Responda APENAS com um JSON valido, sem texto adicional, "
                "neste formato exato:\n"
                '{"responsavel": "requerente" | "requerido" | '
                '"ambos_culpa_concorrente" | "parcial_ambos",\n'
                ' "resultado": "procedente" | "improcedente" | '
                '"parcialmente procedente",\n'
                ' "valores": {"principal": <numero>, "multa": <numero>, '
                '"danos_morais": <numero>, "outros": <numero>},\n'
                ' "fundamentos": ["<3 a 6 fundamentos objetivos e curtos>"],\n'
                ' "confianca": <0.0 a 1.0>}\n'
                "Regras de classificacao: "
                "(a) em 'valores', use SOMENTE as chaves principal, multa, "
                "danos_morais e outros, com 0.0 quando a rubrica for negada ou "
                "nao se aplicar; some na mesma chave rubricas da mesma natureza; "
                "nao inclua correcao monetaria ou juros. "
                "(b) use 'parcial_ambos' ou 'ambos_culpa_concorrente' SOMENTE "
                "quando as DUAS partes tiverem contribuido causalmente para o "
                "dano; rejeitar apenas parte dos pedidos NAO torna o caso "
                "'parcial_ambos' - nesse caso o responsavel e a parte perdedora "
                "e o resultado e 'parcialmente procedente'. "
                "(c) 'responsavel' significa a parte que fica OBRIGADA a pagar "
                "ou fazer algo em favor da outra (a parte perdedora). Se o "
                "requerido deve pagar ao requerente, responsavel = 'requerido'. "
                "(d) aplique os valores conforme o contrato e as provas dos "
                "documentos; NAO reduza nem module valores por equidade, "
                "razoabilidade ou boa-fe - ajustes de equidade sao prerrogativa "
                "exclusiva do mediador humano, fora deste parecer. "
                "(e) padroes de prova: orcamentos de reparo SAO prova valida de "
                "danos materiais - adote o menor orcamento apresentado; nao "
                "exija comprovante de desembolso previo. Ja lucros cessantes e "
                "perdas projetadas exigem comprovacao documental do prejuizo "
                "liquido efetivo; sem essa prova, atribua 0.0 a essa parcela. "
                "(f) os 'valores' representam o TOTAL devido ao requerente por "
                "rubrica, conforme o merito. Limites de apolice de seguro, "
                "franquias e divisao de pagamento entre requeridos sao questoes "
                "de execucao e NAO alteram os valores do parecer. Em 'principal', "
                "informe a soma dos danos materiais e lucros cessantes "
                "concedidos, sem somar nem subtrair coberturas de seguro. "
                "(g) coerencia: se TODOS os valores forem 0.0 e nao houver "
                "obrigacao de fazer, entao resultado = 'improcedente' e "
                "responsavel = 'requerente'. Se houver culpa concorrente com "
                "reparticao de valores, use responsavel = "
                "'ambos_culpa_concorrente' e informe em 'principal' apenas a "
                "quota devida ao requerente. "
                "Use apenas fatos presentes nos documentos. "
                "Nao invente valores nem fatos."
            )
            answer = gl.nondet.exec_prompt(prompt)
            answer = answer.replace("```json", "").replace("```", "").strip()
            start = answer.find("{")
            end = answer.rfind("}")
            opinion = json.loads(answer[start:end + 1])
            return json.dumps(opinion, sort_keys=True, ensure_ascii=False)

        parecer = gl.eq_principle.prompt_comparative(
            leader_analysis,
            principle=(
                "The output is a JSON legal opinion. Two outputs are EQUIVALENT "
                "if ALL of the following hold: "
                "1) 'responsavel' is exactly the same; "
                "2) 'resultado': 'procedente' and 'parcialmente procedente' "
                "count as equivalent to each other; 'improcedente' only matches "
                "'improcedente'; "
                "3) in 'valores', for the keys 'principal', 'multa' and "
                "'outros': values within plus/minus 15% of each other, and a "
                "value of 0 in one must be 0 in the other; "
                "4) 'danos_morais' is a matter of judicial discretion and may "
                "differ freely - ignore it; "
                "5) at least 2 of the 'fundamentos' are semantically "
                "equivalent; "
                "6) ignore 'confianca'."
            ),
        )

        # ---------- ROUND 2: settlement draft (non-comparative EP) ----------
        def get_context() -> str:
            raw_case = gl.nondet.web.get(case_url).body.decode("utf-8")
            return ("DOCUMENTOS DO CASO (JSON):\n" + raw_case
                    + "\n\nPARECER DO COMITE (JSON):\n" + parecer)

        termo = gl.eq_principle.prompt_non_comparative(
            get_context,
            task=(
                "Redija, em portugues formal e neutro, o TERMO DE ACORDO "
                "EXTRAJUDICIAL deste caso de mediacao, com: qualificacao das "
                "partes (pseudonimizadas), resumo do conflito, obrigacoes de "
                "cada parte com valores e prazos, clausula de quitacao, "
                "clausula de confidencialidade e clausula declarando o termo "
                "titulo executivo extrajudicial (CPC, art. 784, III)."
            ),
            criteria=(
                "The draft is VALID only if ALL hold: "
                "1) it addresses the claims of BOTH parties; "
                "2) it cites only facts present in the case documents; "
                "3) it does not contradict the committee opinion - the obligated "
                "party matches 'responsavel' and every amount matches 'valores'; "
                "4) obligations are concrete (who pays what, how much, by when); "
                "5) it is written in formal, neutral Brazilian Portuguese; "
                "6) it contains no personal data beyond pseudonymized initials."
            ),
        )

        self.case_id = case_id
        self.case_url = case_url
        self.parecer = parecer
        self.termo = termo
        self.status = "concluido"

    @gl.public.view
    def get_case(self) -> str:
        result = {
            "case_id": self.case_id,
            "case_url": self.case_url,
            "status": self.status,
            "parecer": json.loads(self.parecer) if self.parecer else None,
            "termo": self.termo if self.termo else None,
        }
        return json.dumps(result, ensure_ascii=False)
