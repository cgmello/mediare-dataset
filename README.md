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

### Termo Final de Mediação (off-chain)

Depois que todas as partes escolherem um Termo de Opção, `termo_acordo.py` gera
o acordo final. Ele exige aceite unânime, qualificação das partes, dados do
mediador, resumo do conflito, pagamento e assinatura. Para fórmula, o percentual
deve estar fechado; para faixa, deve ser escolhido um valor exato dentro dela.

Copie `dados_acordo.exemplo.json`, preencha-o localmente com os dados reais e não
versione o arquivo preenchido. Para o caso com uma única fórmula:

    python3 termo_acordo.py get-case.json \
      --dados dados-acordo-0005.json \
      --termo TO-001 \
      --percentual RP01=60 \
      --format html \
      -o acordo-0005.html

Se houver somente uma fórmula em todo o painel, `--percentual 60` também é aceito.
Opções do tipo faixa usam, por exemplo, `--valor RP01=38.840,93`. As saídas podem
ser `markdown`, `json` ou `html`; nenhum documento é gravado quando a validação
falha. Critérios formais, fontes oficiais e limites do modelo estão em
[docs/TERMO_ACORDO_FORMAL.md](docs/TERMO_ACORDO_FORMAL.md).

Para apenas visualizar o resultado sem preencher dados pessoais, use o próprio
modelo com `--rascunho`:

    python3 termo_acordo.py get-case.json \
      --dados dados_acordo.exemplo.json \
      --termo TO-001 \
      --percentual RP01=60 \
      --rascunho \
      --format html \
      -o acordo-0005.html

Nesse modo, identidades e endereços são substituídos por personagens e números
inequivocamente fictícios. O HTML recebe marcação visual de simulação, o texto
declara que não possui validade e todos os campos de assinatura são suprimidos.
No modo final, os blocos de assinatura repetem o CPF ou CNPJ de cada parte para
facilitar sua identificação e conferência no momento da assinatura.

### Avaliação local via OpenRouter

`openrouter_runner.py` executa um snapshot congelado do IC com cinco modelos,
preserva respostas intermediárias, votos, tokens, latência e custos e permite
retomada sem cobrar novamente chamadas já concluídas. O quórum local é apenas um
instrumento analítico: ele não reproduz nem substitui o consenso do Studio.

A chave pode ser fornecida pelo ambiente ou por arquivo local ignorado pelo Git:

    chmod 600 .openrouter.key
    python3 openrouter_runner.py init --max-cost 10
    python3 openrouter_runner.py run \
      --api-key-file .openrouter.key \
      --case-limit 10

O primeiro comando congela 50 casos e a configuração. `--case-limit 10` processa
somente dez casos novos; uma execução posterior com `resume` continua no caso 11
sem repetir as chamadas anteriores. O limite de US$ 10 é persistente e independente
do limite nominal da chave. O relatório único para o investidor é atualizado em
`OPENROUTER_V20_INVESTOR_REPORT.html`.

Cada caso possui cinco papéis de modelo (um líder e quatro revisores), mas o líder
executa catálogo e lentes em requisições separadas. Assim, dez casos correspondem
a 50 avaliações de papéis e normalmente a pelo menos 80 chamadas HTTP reais.

A v22 híbrida está em `ic_v22.py`. Sua ordem de casos coloca 20 sentinelas antes
dos outros 30, permitindo um checkpoint pago antes da campanha completa:

    python3 openrouter_runner.py init \
      --source ic_v22.py \
      --selection v22_cases.json \
      --out res_openrouter_v22_0001_0050 \
      --report OPENROUTER_V22_REPORT.html \
      --max-cost 15
    python3 openrouter_runner.py run \
      --out res_openrouter_v22_0001_0050 \
      --report OPENROUTER_V22_REPORT.html \
      --api-key-file .openrouter.key \
      --case-limit 20

Os critérios para retomar os 30 casos restantes e, depois, promover o snapshot
ao Studio estão em [V22_EXPERIMENT_PLAN.md](V22_EXPERIMENT_PLAN.md).

## Notes

- "real" cases were reconstructed from public court decisions (CJPG/TJSP), with
  party names pseudonymized (LGPD compliance). "sintetico" cases contain no real data.
- Gold cases were manually curated; real cases were generated via LLM and should be
  sample-reviewed before use as evaluation ground truth.
- For honest evaluation of web-browsing models, consider keeping `gabaritos/`
  in a private repository during test runs.
