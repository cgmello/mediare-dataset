# v30-r3 OpenRouter gate — paired analysis against v28

This report compares the same 12 targeted cases. The v28 baseline is the accepted Studio
panel; v30-r3 is an off-chain five-model OpenRouter simulation and is not protocol
consensus. Ground truth is used only for post-run evaluation.

## Executive result

- Local majority: **11/12**
- Structurally valid leader panels: **12/12**
- Operationally useful leader outputs: **6/12**
- Requests left unresolved: **11 in v28 → 11 in v30-r3**
- Agreement with the independent abstention audit: **2/11 (18.2%)**
- Catalog ID sets unchanged: **11/12 cases**
- Exact-outcome resolved/correct: v28 **7/5**, v30-r3 **6/5**
- Binary-relief resolved/correct: v28 **8/8**, v30-r3 **7/7**

## Balanced groups

| Group | Cases | Agree | Valid | Useful | Unresolved v28 → v29 | Audit matches |
|---|---:|---:|---:|---:|---:|---:|
| indispensable_residuals | 3 | 2 | 3 | 2 | 4 → 1 | 1/4 |
| technical_failures | 2 | 2 | 2 | 1 | 4 → 5 | 1/4 |
| resolved_control_regressions | 6 | 6 | 6 | 2 | 0 → 2 | 0/0 |
| binary_residual | 1 | 1 | 1 | 1 | 3 → 3 | 0/3 |

## Invalid leader panels

- None.

## Audit mismatches requiring qualitative review

| Case | Request | Audit sufficiency | Expected | v30-r3 observed |
|---:|---|---|---|---|
| 0003 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0079 | RP02 | indispensavel_ausente | `necessita_informacao` | `pedido_ausente` |
| 0118 | RP02 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0017 | RP01 | util_mas_nao_indispensavel | `conceder` | `necessita_informacao` |
| 0017 | RP02 | util_mas_nao_indispensavel | `negar` | `conceder` |
| 0017 | CR01 | indispensavel_ausente | `necessita_informacao` | `conceder` |
| 0163 | RP01 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0163 | RP02 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |
| 0163 | RP03 | util_mas_nao_indispensavel | `negar` | `necessita_informacao` |

## Every case

| Case | Group | Vote | Valid | Useful | Unresolved v28 → v30-r3 | Exact outcome v28 → v30-r3 |
|---:|---|---|---|---|---:|---|
| 0003 | indispensable_residuals | DISAGREE | yes | yes | 1 → 0 | — → procedente |
| 0079 | indispensable_residuals | AGREE | yes | no | 2 → 1 | — → — |
| 0118 | indispensable_residuals | AGREE | yes | yes | 1 → 0 | — → procedente |
| 0017 | technical_failures | AGREE | yes | yes | 4 → 5 | — → — |
| 0346 | technical_failures | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0037 | resolved_control_regressions | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0054 | resolved_control_regressions | AGREE | yes | no | 0 → 1 | parcialmente procedente → — |
| 0243 | resolved_control_regressions | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0343 | resolved_control_regressions | AGREE | yes | no | 0 → 1 | improcedente → — |
| 0482 | resolved_control_regressions | AGREE | yes | yes | 0 → 0 | procedente → procedente |
| 0486 | resolved_control_regressions | AGREE | yes | no | 0 → 0 | procedente → procedente |
| 0163 | binary_residual | AGREE | yes | yes | 3 → 3 | — → — |
