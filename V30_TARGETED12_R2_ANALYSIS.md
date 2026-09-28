# v30-r2 OpenRouter gate — paired analysis against v28

This report compares the same 12 targeted cases. The v28 baseline is the accepted Studio
panel; v30-r2 is an off-chain five-model OpenRouter simulation and is not protocol
consensus. Ground truth is used only for post-run evaluation.

## Executive result

- Local majority: **6/12**
- Structurally valid leader panels: **11/12**
- Operationally useful leader outputs: **5/12**
- Requests left unresolved: **11 in v28 → 7 in v30-r2**
- Agreement with the independent abstention audit: **3/11 (27.3%)**
- Catalog ID sets unchanged: **8/12 cases**
- Exact-outcome resolved/correct: v28 **7/5**, v30-r2 **6/4**
- Binary-relief resolved/correct: v28 **8/8**, v30-r2 **8/8**

## Balanced groups

| Group | Cases | Agree | Valid | Useful | Unresolved v28 → v29 | Audit matches |
|---|---:|---:|---:|---:|---:|---:|
| indispensable_residuals | 3 | 1 | 3 | 2 | 4 → 0 | 0/4 |
| technical_failures | 2 | 1 | 2 | 1 | 4 → 4 | 0/4 |
| resolved_control_regressions | 6 | 3 | 5 | 1 | 0 → 3 | 0/0 |
| binary_residual | 1 | 1 | 1 | 1 | 3 → 0 | 3/3 |

## Invalid leader panels

- `0037`: `LLM_INVALID_PANEL:lente=probatoria:1=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES;2=RP01.valor_centavos:CONCESSAO_NAO_MONETARIA_EXIGE_ZERO;3=RP01.COERENCIA_DECISAO_VALOR_PARTES_FONTES`

## Audit mismatches requiring qualitative review

| Case | Request | Audit sufficiency | Expected | v30-r2 observed |
|---:|---|---|---|---|
| 0003 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0079 | RP01 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0079 | RP02 | indispensavel_ausente | `necessita_informacao` | `negar` |
| 0118 | RP02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0017 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0017 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0017 | CR01 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0017 | CR04 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |

## Every case

| Case | Group | Vote | Valid | Useful | Unresolved v28 → v30-r2 | Exact outcome v28 → v30-r2 |
|---:|---|---|---|---|---:|---|
| 0003 | indispensable_residuals | DISAGREE | yes | yes | 1 → 0 | — → procedente |
| 0079 | indispensable_residuals | AGREE | yes | no | 2 → 0 | — → parcialmente procedente |
| 0118 | indispensable_residuals | DISAGREE | yes | yes | 1 → 0 | — → procedente |
| 0017 | technical_failures | DISAGREE | yes | yes | 4 → 4 | — → — |
| 0346 | technical_failures | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0037 | resolved_control_regressions | DISAGREE | no | no | 0 → 0 | procedente → — |
| 0054 | resolved_control_regressions | AGREE | yes | no | 0 → 1 | parcialmente procedente → — |
| 0243 | resolved_control_regressions | DISAGREE | yes | no | 0 → 0 | procedente → procedente |
| 0343 | resolved_control_regressions | AGREE | yes | no | 0 → 1 | improcedente → — |
| 0482 | resolved_control_regressions | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0486 | resolved_control_regressions | DISAGREE | yes | no | 0 → 1 | procedente → — |
| 0163 | binary_residual | AGREE | yes | yes | 3 → 0 | — → improcedente |
