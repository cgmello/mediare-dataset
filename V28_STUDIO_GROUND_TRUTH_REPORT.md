# v28 Studio — comparison with dataset ground truth

This evaluation separates **protocol consensus**, **coverage**, and **accuracy**.
The IC is designed to prepare mediation options, while the stored ground truth is
an aggregate court outcome, so direct comparison is necessarily conservative.

## Results

| Metric | Result |
|---|---:|
| Studio protocol consensus | 98/100 (98.0%) |
| Exact three-way outcome coverage | 11/97 (11.3%) |
| Exact outcome accuracy when resolved | 9/11 (81.8%) |
| Binary relief coverage | 24/98 (24.5%) |
| Binary relief accuracy when resolved | 24/24 (100.0%) |
| Quantified-value coverage | 3/54 (5.6%) |
| Quantified-value accuracy when resolved | 3/3 (100.0%) |

The principal finding is that v28 is **accurate when it reaches a substantive
conclusion, but abstains frequently**. Its 98% consensus rate mainly shows that
validators agree on the panel, including panels that request more information;
it is not a 98% legal-accuracy rate.

## Exact-outcome errors

- `0054`: expected **procedente**, IC concluded **parcialmente procedente**.
- `0482`: expected **parcialmente procedente**, IC concluded **procedente**.

## Protocol-undetermined cases

`0052`, `0137`

## Method

- Exact outcome: all claimant requests (`RP`) favorable = granted; all contrary
  = dismissed; a favorable/contrary mix = partially granted. Any `sem_maioria`
  produces an abstention.
- Binary relief: at least one favorable `RP` means some relief; all contrary
  means no relief. All other structures are abstentions.
- Monetary comparison is limited to references accepted by `gold.py` and IC
  panels whose favorable requests are all quantified. Abstentions are reported
  as missing coverage, not silently counted as correct.
