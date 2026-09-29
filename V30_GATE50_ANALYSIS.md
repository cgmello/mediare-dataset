# v30 OpenRouter gate — paired analysis against v28

This report compares the same 50 paired cases. The v28 baseline is the accepted Studio
panel; v30 is an off-chain five-model OpenRouter simulation and is not protocol
consensus. Ground truth is used only for post-run evaluation.

## Executive result

- Local majority: **39/50**
- Structurally valid leader panels: **50/50**
- Operationally useful leader outputs: **28/50**
- Requests left unresolved: **98 in v28 → 56 in v30**
- Agreement with the independent abstention audit: **52/98 (53.1%)**
- Catalog ID sets unchanged: **42/50 cases**
- Exact-outcome resolved/correct: v28 **10/8**, v30 **19/13**
- Binary-relief resolved/correct: v28 **14/14**, v30 **28/27**

## Balanced groups

| Group | Cases | Agree | Valid | Useful | Unresolved v28 → v29 | Audit matches |
|---|---:|---:|---:|---:|---:|---:|
| avoidable_abstention | 25 | 20 | 25 | 14 | 65 → 26 | 25/65 |
| indispensable_abstention_control | 15 | 11 | 15 | 10 | 33 → 28 | 27/33 |
| fully_resolved_control | 10 | 8 | 10 | 4 | 0 → 2 | 0/0 |

## Invalid leader panels

- None.

## Audit mismatches requiring qualitative review

| Case | Request | Audit sufficiency | Expected | v30 observed |
|---:|---|---|---|---|
| 0004 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0004 | RP02 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0014 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0014 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0014 | RP04 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0014 | CR02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0014 | CR03 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0014 | CR05 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0017 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0017 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0017 | CR01 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0017 | CR04 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0021 | CR01 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0021 | CR02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0021 | CR03 | util_mas_nao_indispensavel | `conceder` | `pedido_ausente` |
| 0033 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0048 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0048 | CR01 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0048 | CR02 | util_mas_nao_indispensavel | `negar` | `pedido_ausente` |
| 0050 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0050 | RP03 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0050 | RP05 | util_mas_nao_indispensavel | `conceder` | `negar` |
| 0088 | CR01 | suficiente_para_direcao | `negar` | `conceder` |
| 0088 | CR02 | suficiente_para_direcao | `negar` | `necessita_informacao` |
| 0123 | RP01 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0123 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0123 | RP03 | suficiente_para_direcao | `conceder` | `pedido_ausente` |
| 0163 | RP01 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0163 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0163 | RP03 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0173 | RP04 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0173 | CR01 | suficiente_para_direcao | `fora_de_escopo` | `conceder` |
| 0199 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0238 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0298 | RP02 | suficiente_para_direcao | `negar` | `necessita_informacao` |
| 0370 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0397 | RP01 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0430 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0435 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0460 | RP02 | suficiente_para_direcao | `negar` | `conceder` |
| 0003 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0007 | RP03 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0079 | RP02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0118 | RP02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0145 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0145 | RP03 | indispensavel_ausente | `necessita_informacao` | `conceder` |

## Every case

| Case | Group | Vote | Valid | Useful | Unresolved v28 → v30 | Exact outcome v28 → v30 |
|---:|---|---|---|---|---:|---|
| 0004 | avoidable_abstention | AGREE | yes | yes | 2 → 2 | — → — |
| 0014 | avoidable_abstention | AGREE | yes | yes | 8 → 5 | — → — |
| 0017 | avoidable_abstention | DISAGREE | yes | yes | 4 → 2 | — → — |
| 0021 | avoidable_abstention | DISAGREE | yes | yes | 6 → 0 | — → procedente |
| 0030 | avoidable_abstention | AGREE | yes | no | 2 → 0 | — → procedente |
| 0033 | avoidable_abstention | AGREE | yes | no | 1 → 1 | — → — |
| 0046 | avoidable_abstention | AGREE | yes | yes | 4 → 0 | — → procedente |
| 0048 | avoidable_abstention | AGREE | yes | yes | 3 → 2 | — → — |
| 0050 | avoidable_abstention | DISAGREE | yes | yes | 4 → 4 | — → — |
| 0078 | avoidable_abstention | AGREE | yes | yes | 3 → 0 | — → procedente |
| 0088 | avoidable_abstention | AGREE | yes | yes | 2 → 1 | procedente → procedente |
| 0123 | avoidable_abstention | AGREE | yes | no | 3 → 0 | — → procedente |
| 0163 | avoidable_abstention | AGREE | yes | yes | 3 → 0 | — → procedente |
| 0173 | avoidable_abstention | DISAGREE | yes | yes | 5 → 1 | — → — |
| 0199 | avoidable_abstention | AGREE | yes | no | 1 → 1 | — → — |
| 0213 | avoidable_abstention | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0238 | avoidable_abstention | AGREE | yes | yes | 1 → 1 | — → — |
| 0298 | avoidable_abstention | AGREE | yes | no | 1 → 1 | — → — |
| 0326 | avoidable_abstention | AGREE | yes | no | 1 → 0 | — → procedente |
| 0370 | avoidable_abstention | AGREE | yes | no | 2 → 1 | — → — |
| 0397 | avoidable_abstention | AGREE | yes | yes | 2 → 1 | — → — |
| 0430 | avoidable_abstention | AGREE | yes | no | 1 → 1 | — → — |
| 0435 | avoidable_abstention | AGREE | yes | no | 2 → 1 | — → — |
| 0460 | avoidable_abstention | AGREE | yes | no | 2 → 0 | — → procedente |
| 0476 | avoidable_abstention | DISAGREE | yes | no | 1 → 1 | — → procedente |
| 0003 | indispensable_abstention_control | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0007 | indispensable_abstention_control | AGREE | yes | yes | 1 → 1 | — → — |
| 0057 | indispensable_abstention_control | AGREE | yes | yes | 4 → 4 | — → — |
| 0079 | indispensable_abstention_control | AGREE | yes | yes | 2 → 1 | — → — |
| 0081 | indispensable_abstention_control | DISAGREE | yes | yes | 3 → 3 | — → — |
| 0083 | indispensable_abstention_control | DISAGREE | yes | yes | 6 → 6 | — → — |
| 0092 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0100 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0106 | indispensable_abstention_control | AGREE | yes | yes | 3 → 3 | — → — |
| 0118 | indispensable_abstention_control | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0134 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0142 | indispensable_abstention_control | DISAGREE | yes | no | 2 → 2 | — → — |
| 0145 | indispensable_abstention_control | DISAGREE | yes | yes | 3 → 1 | — → — |
| 0164 | indispensable_abstention_control | AGREE | yes | yes | 3 → 3 | — → — |
| 0207 | indispensable_abstention_control | AGREE | yes | no | 1 → 1 | — → — |
| 0037 | fully_resolved_control | DISAGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0054 | fully_resolved_control | AGREE | yes | no | 0 → 1 | parcialmente procedente → — |
| 0147 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0209 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0243 | fully_resolved_control | DISAGREE | yes | no | 0 → 0 | procedente → procedente |
| 0310 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0343 | fully_resolved_control | AGREE | yes | yes | 0 → 1 | improcedente → — |
| 0346 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0482 | fully_resolved_control | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0486 | fully_resolved_control | AGREE | yes | no | 0 → 0 | procedente → procedente |
