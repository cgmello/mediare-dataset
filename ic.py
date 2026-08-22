# { "Depends": "py-genlayer:test" }

from genlayer import *
import json


class MediareCommittee(gl.Contract):
    """
    Mediare - AI committee for extrajudicial mediation.
    One call: analyze_case(case_url) -> structured opinion (comparative EP)
                                     -> settlement draft   (non-comparative EP)
    If the human mediator wants changes, the platform publishes a new immutable
    snapshot of the case (v2, with the extra documents) and calls again.
    """

    case_id: str
    case_url: str
    status: str      # vazio | concluido
    parecer: str     # canonical JSON opinion
    termo: str       # settlement terms draft

    def __init__(self):
        self.case_id = ""
        self.case_url = ""
        self.status = "vazio"
        self.parecer = ""
        self.termo = ""

    @gl.public.write
    def analyze_case(self, case_id: str, case_url: str) -> None:
        # ---------- ROUND 1: structured opinion (comparative EP) ----------
        def leader_analysis() -> str:
            raw_case = gl.nondet.web.get(case_url).body.decode("utf-8")
            docs = json.loads(raw_case)["documentos"]
            prompt = f"""Você é um analista jurídico de uma câmara de mediação extrajudicial brasileira.
Analise os documentos das DUAS partes e produza um parecer imparcial.

PETIÇÃO DO REQUERENTE:
{docs["peticao_requerente"]}

DOCUMENTOS DO REQUERENTE:
{docs["documentos_requerente"]}

RESPOSTA DO REQUERIDO:
{docs["resposta_requerido"]}

DOCUMENTOS DO REQUERIDO:
{docs["documentos_requerido"]}

Responda APENAS com um JSON válido, sem texto adicional, neste formato exato:
{{
  "responsavel": "requerente" | "requerido" | "ambos_culpa_concorrente" | "parcial_ambos",
  "resultado": "procedente" | "improcedente" | "parcialmente procedente",
  "valores": {{ "<rubrica>": <numero, 0.0 quando negada> }},
  "fundamentos": [ "<3 a 6 fundamentos objetivos e curtos>" ],
  "confianca": <0.0 a 1.0>
}}
Use apenas fatos presentes nos documentos. Não invente valores nem fatos."""
            answer = gl.nondet.exec_prompt(prompt)
            answer = answer.replace("```json", "").replace("```", "").strip()
            start, end = answer.find("{"), answer.rfind("}")
            opinion = json.loads(answer[start:end + 1])
            return json.dumps(opinion, sort_keys=True, ensure_ascii=False)

        parecer = gl.eq_principle.prompt_comparative(
            leader_analysis,
            principle="""
The output is a JSON legal opinion. Two outputs are EQUIVALENT only if ALL hold:
1. 'responsavel' is exactly the same;
2. 'resultado' is exactly the same;
3. for each key in 'valores': values are within +/-15% of each other, and a value
   of 0 in one must be 0 in the other;
4. at least 2 of the 'fundamentos' are semantically equivalent (same legal ground
   expressed in different words counts as equivalent);
5. ignore 'confianca'.
""",
        )

        # ---------- ROUND 2: settlement draft (non-comparative EP) ----------
        def get_context() -> str:
            raw_case = gl.nondet.web.get(case_url).body.decode("utf-8")
            return ("DOCUMENTOS DO CASO (JSON):\n" + raw_case
                    + "\n\nPARECER DO COMITÊ (JSON):\n" + parecer)

        termo = gl.eq_principle.prompt_non_comparative(
            get_context,
            task=(
                "Redija, em português formal e neutro, o TERMO DE ACORDO EXTRAJUDICIAL "
                "deste caso de mediação, com: qualificação das partes (pseudonimizadas), "
                "resumo do conflito, obrigações de cada parte com valores e prazos, "
                "cláusula de quitação e cláusula de confidencialidade."
            ),
            criteria="""
The draft is VALID only if ALL of the following hold:
1. It addresses the claims of BOTH parties (requerente and requerido);
2. It cites only facts present in the case documents - no invented facts;
3. It does not contradict the committee opinion: the obligated party matches
   'responsavel' and every amount matches the 'valores' of the opinion;
4. Obligations are concrete (who pays what, how much, by when);
5. It is written in formal, neutral Brazilian Portuguese;
6. It contains no personal data beyond the pseudonymized initials.
""",
        )

        self.case_id = case_id
        self.case_url = case_url
        self.parecer = parecer
        self.termo = termo
        self.status = "concluido"

    @gl.public.view
    def get_case(self) -> str:
        return json.dumps({
            "case_id": self.case_id,
            "case_url": self.case_url,
            "status": self.status,
            "parecer": json.loads(self.parecer) if self.parecer else None,
            "termo": self.termo or None,
        }, ensure_ascii=False)
