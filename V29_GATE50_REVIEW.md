# v29 gate review — promotion decision

## Decision

**Do not promote the current v29 candidate to Studio.** The new rule achieved
its intended coverage gain, but it is too aggressive: it often replaced a
justified request for information with a definitive grant or denial. The next
iteration should keep the separation between merits direction and amount while
restoring a material-evidence gate for causation, contract validity, fault and
authenticity.

This conclusion is based on the paired 50-case gate. The v28 baseline is the
accepted Studio panel; v29 is an off-chain five-model OpenRouter simulation, not
GenLayer protocol consensus. The ground truth is an aggregate judicial outcome
and is used only as post-run evidence, not as an instruction to the IC.

## What improved

- Unresolved requests fell from **98 in v28 to 27 in v29**.
- Exact three-way outcome coverage increased from **10/50 to 32/50**.
- Binary-relief coverage increased from **14/50 to 33/50**.
- All ten fully resolved controls remained resolved; their aggregate exact
  outcome was preserved in all ten cases.
- The campaign completed all 50 cases with **39 local majorities**, **47 valid
  leader panels**, 445 calls, 2,668,949 tokens and a cost of **US$5.7921103**.

## Why the current candidate is not safe to promote

- Agreement with the independent request-level abstention audit was only
  **48/98 (49.0%)**.
- In the 15 controls selected because decisive information was truly absent,
  v29 preserved only **19/33** audited abstentions. It prematurely decided the
  other requests or changed their catalogue identity.
- Conditional exact-outcome accuracy moved from **8/10 (80%)** in v28 to
  **18/32 (56.3%)** in v29. Coverage improved, but precision deteriorated.
- Binary-relief accuracy moved from **14/14 (100%)** to **29/33 (87.9%)**.
- Four candidate conclusions reversed the binary result against the stored
  reference: `0014`, `0163`, `0092` and `0142`. The first two also have direct
  support in the independent audit for treating the v29 direction as unsafe.
- Catalogue IDs changed in 11/50 cases, which makes part of the request-level
  comparison impossible and reveals instability unrelated to the new
  abstention rule.

## The 11 local disagreements

| Case | Finding | Assessment |
|---:|---|---|
| 0014 | Two reviewers rejected defensive `CR05`; v29 also converted eight unresolved items into definitive conclusions and reached `improcedente` where the reference is `procedente`. | Real catalogue defect and substantive overcorrection. |
| 0017 | Leader failed validation three times on coherence among decision, value, parties and sources for `RP01`. | Technical generation/normalization failure. |
| 0088 | Leader failed audit validation: missing mandatory reason and double-counting without an identified conflict. | Technical audit-panel failure. |
| 0163 | One reviewer misdescribed two existing requests as omissions, but v29 granted all three claims while both the independent audit and reference support denial. | Reviewer rationale is noisy; substantive regression is real. |
| 0199 | Same repeated coherence failure as `0017`. | Technical generation/normalization failure. |
| 0476 | Reviewers identified defensive retention/damages as an autonomous `CR`; v29 resolved the formerly open item without stable catalogue agreement. | Real RP/CR catalogue regression. |
| 0083 | Three reviewers identified `RP07` as an acknowledgement/limitation, not an autonomous request. | Real catalogue excess; previously identified RP/CR semantics apply. |
| 0142 | One reviewer found duplicated remedies and another rejected the conclusions; v29 denied claims whose material basis remained unresolved and reversed binary relief. | Material overcorrection plus possible granularity issue. |
| 0145 | Reviewers found omitted subsidiary excess-of-execution relief; requests for suspensive procedural effect should remain outside the bilateral catalogue. | One real omission mixed with reviewer overreach. |
| 0209 | Catalogue and aggregate outcome were preserved; disagreement concerned sources/conclusion. | Reviewer variability or request-level support issue, not demonstrated aggregate regression. |
| 0243 | Catalogue split principal, penalty and interest while one reviewer preferred aggregation; aggregate outcome was preserved. | Mostly granularity policy variation, not demonstrated substantive regression. |

## The three invalid panels

- `0017` and `0199`: the probative lens repeatedly produced an internally
  incoherent combination of decision, value, parties and cited sources.
- `0088`: the auditing lens omitted a mandatory explanation and asserted
  double-counting without naming the conflicting request.

These are deterministic validation failures and should be fixed separately
from the merits threshold. They do not justify weakening the validator.

## Recommended correction before another gate

1. Keep `valor_centavos=null` for a directional monetary grant only when
   responsibility is already supported and the sole open issue is amount or
   proportion.
2. Require `necessita_informacao` when the missing fact concerns causation,
   authenticity/validity, fault attribution, contractual incidence or the
   existence of the underlying obligation and could reverse the result.
3. Permit denial for lack of minimum constitutive support only when the absence
   itself is established by the summarized record; do not turn a genuinely
   disputed evidentiary gap into an automatic denial.
4. Reassert catalogue rules: acknowledgements and defensive set-off/retention
   are not autonomous requests; a counter-request exists only when the
   respondent asks for an independent benefit against the claimant.
5. Add generation guidance for null-value directional decisions and auditing
   conflicts, while preserving the current fail-closed validators.
6. Rerun the same 50-case gate. Promotion requires materially better audit
   agreement, preservation of the 33 indispensable controls, no loss on the ten
   resolved controls, and elimination of the three invalid panels.

Detailed reproducible metrics and every case are in
`V29_GATE50_ANALYSIS.md` and `V29_GATE50_ANALYSIS.json`.
