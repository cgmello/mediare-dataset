# v29 corrected gate — paired decision

## Decision

The corrected v29 completed the same 50-case OpenRouter gate, but **should not
yet be promoted to Studio**. It successfully restored the material-evidence
barrier, preserving 30/33 indispensable abstentions, but moved too far toward
conservatism and introduced new abstentions in six of the ten controls that v28
had already resolved.

## Paired comparison

| Metric | v28 Studio baseline | v29 first gate | v29 corrected gate |
|---|---:|---:|---:|
| Unresolved requests | 98 | 27 | 75 |
| Indispensable controls preserved | 33 baseline abstentions | 19/33 | 30/33 |
| Previously resolved controls with new abstention | 0/10 | 0/10 | 6/10 |
| Exact outcome resolved / correct | 10 / 8 | 32 / 18 | 12 / 8 |
| Binary relief resolved / correct | 14 / 14 | 33 / 29 | 19 / 18 |
| Local majority | Studio protocol baseline | 39/50 | 36/50 |
| Valid leader panels | 50 accepted Studio panels | 47/50 | 48/50 |
| Operationally useful leader outputs | not directly comparable | 23/50 | 25/50 |

The corrected gate improved conditional precision over the first gate: exact
accuracy rose from 56.3% to 66.7%, and binary-relief accuracy rose from 87.9%
to 94.7%. However, the exact-coverage gain over v28 nearly disappeared, and the
new abstentions in resolved controls violate the no-regression requirement.

## Remaining technical failures

- `0017`: the probative lens repeated an incoherent combination of monetary
  decision, value, parties and sources despite directed repair guidance.
- `0346`: the probative lens returned an invalid gap schema three times.

The former audit failure in `0088` and the former coherence failure in `0199`
were recovered, but `0017` remained and `0346` became a new structural failure.

## Substantive residuals

- Only three of the 33 indispensable controls were not preserved, a major
  improvement over the first gate.
- Six resolved-control cases gained at least one unnecessary abstention:
  `0037`, `0054`, `0243`, `0343`, `0482` and `0486`.
- The only binary-relief error among resolved corrected panels was `0163`, where
  v29 granted some relief while the stored reference denies all relief.
- Aggregate exact errors were `0123`, `0163`, `0326` and `0476`. Because the
  stored outcome is aggregate, these identify review targets rather than a
  complete legal-merits judgment.

## Recommended next calibration

Do not simply weaken the material gate globally. Limit it to a positive trigger:
the model must identify the specific omitted fact, its source or expected
document, and explain how opposite answers would reverse the decision. If it
cannot state both branches, the gap is only useful and must not block direction.
Conversely, keep the gate mandatory for authenticity/validity, causal attribution
and existence of the obligation when that two-branch explanation is concrete.

The next gate should again use these same 50 cases and require simultaneously:

1. at least 30/33 indispensable controls preserved;
2. no new abstention in the ten fully resolved controls;
3. no invalid leader panel;
4. binary-relief accuracy at or above the corrected gate;
5. materially more exact-outcome coverage than v28.

Detailed case data are in `V29_GATE50_R2_ANALYSIS.md` and JSON counterpart.
