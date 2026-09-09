# v20 holdout plan — cases 0051–0100

## Purpose

Evaluate the frozen `20.0.0-experimental` Intelligent Contract on an unseen
50-case segment before making any v21 change. The segment is intentionally
different from cases 0001–0050: it contains 21 renovation, 19 traffic, nine
consumer, and one neighborhood dispute.

## Frozen execution

- Contract: `0xCb46400C0bD70a694673ED28f6A9Adec6915aCae` (fresh bootstrap
  after the prior Studionet address expired).
- Source snapshot: `res_canary_v20/20.0.0-experimental.py`.
- Cases: the exact ordered list in `holdout_v20_0051_0100.json`.
- Calls: one serial `analyze_case` submission per case.
- Delay: at least 15 seconds after every terminal transaction.
- Output: `res_holdout_v20_0051_0100/`.
- No upgrade, prompt change, retry of a submitted case, or use of benchmark
  answers inside the IC is allowed during the campaign.

## Evaluation dimensions

Report protocol consensus, technical failures, rotations, panel integrity,
operational usefulness, retained options, formula use, and a manual review of
materially risky or surprising outputs. This holdout becomes development data
after the report; cases 0101–0150 remain untouched for a future v21 validation.
