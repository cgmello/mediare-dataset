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

## Second run after the accessory-consolidation fix

`0023` again produced only `RP01` and reached 3–1 Agree. `0048` now produced
exactly `RP01` plus the affirmative restitution `CR01`, and the leader label
matched `APTO_INTEGRAL`; reviewers nevertheless split 2–2 (one defensive
omission objection and one option objection). The rerun cost 19 calls, 103,210
tokens and US$ 0.18535546944. The catalog regression is fixed, but reviewer
stability remains before the 20-sentinel gate and Studio promotion.

## Final reviewer-stability reruns

The v25 normalization was refined to treat defensive inexigibility and
compensation/abatement omissions as defense. The subsequent `0048` reruns
produced the following progression:

- `r3`: valid panel, 3–1 Agree; one defensive compensation omission remained;
- `r4`: valid panel, 3–1 Agree; the leader catalog was correct but one reviewer
  still objected to the defensive compensation;
- `r5`: valid panel, 3–1 Agree; the defensive `CR01` was removed, but the model
  reintroduced an inexigibility declaration as a CR;
- `r6`: valid panel, **4–0 Agree**; catalog contains only `RP01` and the
  affirmative restitution `CR01`, with all reviewers approving.

The final `r6` run cost 9 calls, 54,260 tokens and US$ 0.0878490891. Across all
six targeted v25 campaigns, the receipts total 77 HTTP calls, 482,144 tokens
and US$ 0.86815096731; the consolidated ledger reflects these exact totals.
