# Mediare Dataset

Benchmark of Brazilian extrajudicial mediation cases for evaluating AI committees.
Total: **500 cases** (6 gold, 175 derived
from public court decisions (TJSP/Brazil), 319 synthetic).

- `casos/NNNN.json` - input documents from both parties (what the model/contract reads)
- `gabaritos/NNNN.json` - expected outcome + equivalence criteria (evaluation ground truth)
- `manifest.json` - index with category, origin, TJSP case number and SHA-256 of each case

All content is in Brazilian Portuguese, the language of the underlying disputes.

## Usage with Intelligent Contracts (GenLayer)

Pass the contract a URL pinned to a commit (immutable - never use `main`):

    https://raw.githubusercontent.com/cgmello/mediare-dataset/<COMMIT_SHA>/casos/0001.json

Verify integrity by comparing the content's SHA-256 against `manifest.json`.

## Notes

- "real" cases were reconstructed from public court decisions (CJPG/TJSP), with
  party names pseudonymized (LGPD compliance). "sintetico" cases contain no real data.
- Gold cases were manually curated; real cases were generated via LLM and should be
  sample-reviewed before use as evaluation ground truth.
- For honest evaluation of web-browsing models, consider keeping `gabaritos/`
  in a private repository during test runs.
