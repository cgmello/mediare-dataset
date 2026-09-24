# v29 OpenRouter gate — paired analysis against v28

This report compares the same 50 cases. The v28 baseline is the accepted Studio
panel; v29 is an off-chain five-model OpenRouter simulation and is not protocol
consensus. Ground truth is used only for post-run evaluation.

## Executive result

- Local majority: **39/50**
- Structurally valid leader panels: **47/50**
- Operationally useful leader outputs: **23/50**
- Requests left unresolved: **98 in v28 → 27 in v29**
- Agreement with the independent abstention audit: **48/98 (49.0%)**
- Catalog ID sets unchanged: **39/50 cases**
- Exact-outcome resolved/correct: v28 **10/8**, v29 **32/18**
- Binary-relief resolved/correct: v28 **14/14**, v29 **33/29**

## Balanced groups

| Group | Cases | Agree | Valid | Useful | Unresolved v28 → v29 | Audit matches |
|---|---:|---:|---:|---:|---:|---:|
| avoidable_abstention | 25 | 19 | 22 | 10 | 65 → 7 | 29/65 |
| indispensable_abstention_control | 15 | 12 | 15 | 9 | 33 → 20 | 19/33 |
| fully_resolved_control | 10 | 8 | 10 | 4 | 0 → 0 | 0/0 |

## Invalid leader panels

- `0017`: `LLM_INVALID_PANEL:lente=probatoria:1=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES;2=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES;3=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES`
- `0088`: `LLM_INVALID_PANEL:lente=auditora:1=CR01.auditoria:MOTIVO_OBRIGATORIO;2=CR02.auditoria:DUPLA_CONTAGEM_EXIGE_CONFLITO_IDENTIFICADO;3=CR02.auditoria:DUPLA_CONTAGEM_EXIGE_CONFLITO_IDENTIFICADO`
- `0199`: `LLM_INVALID_PANEL:lente=probatoria:1=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES;2=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES;3=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES`

## Audit mismatches requiring qualitative review

| Case | Request | Audit sufficiency | Expected | v29 observed |
|---:|---|---|---|---|
| 0004 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0014 | RP01 | util_mas_nao_indispensavel | `conceder` | `negar` |
| 0014 | RP02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0014 | RP03 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0014 | RP04 | util_mas_nao_indispensavel | `conceder` | `negar` |
| 0014 | CR01 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0014 | CR02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0014 | CR05 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0017 | RP01 | util_mas_nao_indispensavel | `conceder` | `pedido_ausente` |
| 0017 | RP02 | util_mas_nao_indispensavel | `negar` | `pedido_ausente` |
| 0017 | CR01 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0017 | CR04 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0021 | CR01 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0021 | CR02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0021 | CR03 | util_mas_nao_indispensavel | `conceder` | `pedido_ausente` |
| 0033 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0048 | RP01 | util_mas_nao_indispensavel | `conceder` | `pedido_ausente` |
| 0048 | CR01 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0048 | CR02 | util_mas_nao_indispensavel | `negar` | `pedido_ausente` |
| 0050 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0050 | RP03 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0050 | RP05 | util_mas_nao_indispensavel | `conceder` | `negar` |
| 0088 | CR01 | suficiente_para_direcao | `negar` | `pedido_ausente` |
| 0088 | CR02 | suficiente_para_direcao | `negar` | `pedido_ausente` |
| 0123 | RP01 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0123 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0123 | RP03 | suficiente_para_direcao | `conceder` | `pedido_ausente` |
| 0163 | RP01 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0163 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0163 | RP03 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0173 | RP04 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0173 | CR01 | suficiente_para_direcao | `fora_de_escopo` | `negar` |
| 0199 | RP01 | util_mas_nao_indispensavel | `conceder` | `pedido_ausente` |
| 0370 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0397 | RP01 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0460 | RP02 | suficiente_para_direcao | `negar` | `necessita_informacao` |
| 0003 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0007 | RP03 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0079 | RP02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0081 | RP01 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0081 | RP02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0081 | RP03 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0092 | RP01 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0118 | RP02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0142 | RP01 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0142 | RP02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0145 | RP01 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0164 | RP01 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0164 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0164 | RP03 | indispensavel_ausente | `necessita_informacao` | `conceder` |

## Every case

| Case | Group | Vote | Valid | Useful | Unresolved v28 → v29 | Exact outcome v28 → v29 |
|---:|---|---|---|---|---:|---|
| 0004 | avoidable_abstention | AGREE | yes | yes | 2 → 0 | — → procedente |
| 0014 | avoidable_abstention | DISAGREE | yes | no | 8 → 0 | — → improcedente |
| 0017 | avoidable_abstention | DISAGREE | no | no | 4 → 0 | — → — |
| 0021 | avoidable_abstention | AGREE | yes | yes | 6 → 0 | — → procedente |
| 0030 | avoidable_abstention | AGREE | yes | no | 2 → 0 | — → procedente |
| 0033 | avoidable_abstention | AGREE | yes | no | 1 → 1 | — → — |
| 0046 | avoidable_abstention | AGREE | yes | yes | 4 → 0 | — → procedente |
| 0048 | avoidable_abstention | AGREE | yes | no | 3 → 1 | — → — |
| 0050 | avoidable_abstention | AGREE | yes | no | 4 → 3 | — → — |
| 0078 | avoidable_abstention | AGREE | yes | yes | 3 → 0 | — → procedente |
| 0088 | avoidable_abstention | DISAGREE | no | no | 2 → 0 | procedente → — |
| 0123 | avoidable_abstention | AGREE | yes | no | 3 → 0 | — → procedente |
| 0163 | avoidable_abstention | DISAGREE | yes | yes | 3 → 0 | — → procedente |
| 0173 | avoidable_abstention | AGREE | yes | yes | 5 → 0 | — → parcialmente procedente |
| 0199 | avoidable_abstention | DISAGREE | no | no | 1 → 0 | — → — |
| 0213 | avoidable_abstention | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0238 | avoidable_abstention | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0298 | avoidable_abstention | AGREE | yes | no | 1 → 0 | — → parcialmente procedente |
| 0326 | avoidable_abstention | AGREE | yes | no | 1 → 0 | — → procedente |
| 0370 | avoidable_abstention | AGREE | yes | no | 2 → 1 | — → — |
| 0397 | avoidable_abstention | AGREE | yes | yes | 2 → 0 | — → procedente |
| 0430 | avoidable_abstention | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0435 | avoidable_abstention | AGREE | yes | no | 2 → 0 | — → parcialmente procedente |
| 0460 | avoidable_abstention | AGREE | yes | no | 2 → 1 | — → — |
| 0476 | avoidable_abstention | DISAGREE | yes | no | 1 → 0 | — → procedente |
| 0003 | indispensable_abstention_control | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0007 | indispensable_abstention_control | AGREE | yes | yes | 1 → 0 | — → parcialmente procedente |
| 0057 | indispensable_abstention_control | AGREE | yes | yes | 4 → 4 | — → — |
| 0079 | indispensable_abstention_control | AGREE | yes | yes | 2 → 1 | — → — |
| 0081 | indispensable_abstention_control | AGREE | yes | yes | 3 → 0 | — → improcedente |
| 0083 | indispensable_abstention_control | DISAGREE | yes | yes | 6 → 7 | — → — |
| 0092 | indispensable_abstention_control | AGREE | yes | no | 1 → 0 | — → improcedente |
| 0100 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0106 | indispensable_abstention_control | AGREE | yes | yes | 3 → 3 | — → — |
| 0118 | indispensable_abstention_control | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0134 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0142 | indispensable_abstention_control | DISAGREE | yes | no | 2 → 0 | — → improcedente |
| 0145 | indispensable_abstention_control | DISAGREE | yes | no | 3 → 2 | — → — |
| 0164 | indispensable_abstention_control | AGREE | yes | yes | 3 → 0 | — → procedente |
| 0207 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0037 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0054 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | parcialmente procedente → parcialmente procedente |
| 0147 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0209 | fully_resolved_control | DISAGREE | yes | no | 0 → 0 | procedente → procedente |
| 0243 | fully_resolved_control | DISAGREE | yes | no | 0 → 0 | procedente → procedente |
| 0310 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0343 | fully_resolved_control | AGREE | yes | no | 0 → 0 | improcedente → improcedente |
| 0346 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0482 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0486 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
