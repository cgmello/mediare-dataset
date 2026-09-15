# v25 — targeted validation of cases 0023 and 0048

The v25 candidate was run with the same five-model rotation and frozen case
selection used for the v24 targeted comparison.

| Case | Result | Assessment |
|---|---|---|
| 0023 | `LOCAL_MAJORITY_AGREE`; 10 calls, 46,028 tokens, US$ 0.092555 | The defensive-CR regression is fixed. The catalog contains only `RP01`; three reviewers approved it. One reviewer raised a value-anchoring objection, so the result remains useful but merits later review. |
| 0048 | `LOCAL_MAJORITY_DISAGREE`; 13 calls, 108,271 tokens, US$ 0.215530 | `CR01` restitution is preserved, but the leader split the same debt into `RP01` and `RP02` (principal plus accessories). Three reviewers correctly flagged `GRANULARIDADE`; Mistral also returned a malformed compact review. |

## Gate decision

The v25 correction is effective for `0023`, but the candidate is not ready for
Studio promotion. Before promotion, v25 needs one more bounded correction for
the accessory-consolidation rule in `0048` and a technical handling path for a
malformed compact reviewer response.

## Cost

This targeted run added 23 HTTP calls, 154,299 tokens and US$ 0.30808477098 to
the OpenRouter budget. The consolidated ledger includes the receipts under v25.
