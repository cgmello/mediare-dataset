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

For versioned SDK tests, upgrades and resumable runs on Studio, see
[STUDIO_CYCLE.md](STUDIO_CYCLE.md) (Portuguese).
Milestones, failed experiments and report notes: [CHANGELOG.md](CHANGELOG.md).

### Termos para o mediador (off-chain)

`termo_mediador.py` recebe a resposta JSON de `get_case` e gera um documento
objetivo para cada combinação válida que contenha ao menos uma opção aceita entre
as opções que o IC aprovou. A combinação que rejeita todas as opções não produz
Termo. Opções marcadas como não cumulativas nunca aparecem aceitas juntas; opções
retidas são explicadas na identificação dos pedidos e não viram alternativas. O
texto fixo é produzido em português com acentuação e as faixas numéricas são
preservadas.

Gerar Markdown a partir de um arquivo:

    python3 termo_mediador.py get-case.json -o termos-0005.md

Gerar JSON estruturado por pipe:

    cat get-case.json | python3 termo_mediador.py - --format json -o termos-0005.json

Gerar HTML autocontido, pronto para navegador ou impressão em PDF:

    python3 termo_mediador.py get-case.json --format html -o termos.html

O limite padrão é 256 combinações. Se o painel exceder esse valor, o script falha
sem gerar uma lista parcial; o limite só pode ser ampliado explicitamente com
`--max-combinations`.

## Notes

- "real" cases were reconstructed from public court decisions (CJPG/TJSP), with
  party names pseudonymized (LGPD compliance). "sintetico" cases contain no real data.
- Gold cases were manually curated; real cases were generated via LLM and should be
  sample-reviewed before use as evaluation ground truth.
- For honest evaluation of web-browsing models, consider keeping `gabaritos/`
  in a private repository during test runs.
