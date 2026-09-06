# Fase 2 — campanha multicase da v17

A Fase 2 executa o mesmo código congelado da `v17.0.0-experimental` nos 500
casos do dataset, em série. Não faz upgrade e não altera o IC durante a campanha.
O contrato esperado é `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`.

## Segurança e separação do benchmark

- Somente `casos/NNNN.json` é lido pelo IC, através da URL já fixada no código.
- `gabaritos/NNNN.json` é conferido apenas quanto à existência na inicialização.
  Seu conteúdo não entra em prompt, transação, estado ou Termo.
- Erros RPC brutos nunca são impressos ou persistidos. Recibos passam pela redação
  recursiva de credenciais; `events.jsonl` aceita somente campos controlados.
- Uma pasta/lock e um único nonce serializam os envios. Se o resultado de um envio
  for incerto, a campanha para e jamais reenvia o mesmo caso por tentativa.
- A chave é lida do arquivo local indicado e não aparece na linha de comando nem
  nos relatórios. Não executar outra campanha simultânea com a mesma conta.

## Classificação

O relatório separa disponibilidade técnica de utilidade:

- `SATISFATORIO_AUTOMATICO`: FINALIZED/SUCCESS **e** MAJORITY_AGREE,
  painel/Termo íntegros, ao menos uma opção acionável, nenhuma opção retida e
  nenhuma fórmula cujo único envelope seja 0%–100%.
- `REVISAR_UTILIDADE`: execução íntegra, mas opção aberta demais, somente
  diligência ou algum pedido sem opção.
- `INSATISFATORIO_CONTEUDO`: painel aceito com cobertura inválida ou opção retida.
- `INSATISFATORIO_TECNICO`: transação sem FINALIZED/SUCCESS.

Essa triagem é deliberadamente estrita e não certifica correção jurídica. Depois
dos 500 casos, o alinhamento semântico com os gabaritos será avaliado fora do IC,
sem contaminar as respostas geradas.

`execution_result=SUCCESS` isolado descreve a execução do líder. Se o resultado
do consenso for `MAJORITY_DISAGREE`, o estado é revertido mesmo quando a transação
aparece como `FINALIZED`; o runner classifica esse caso como falha técnica e não
lê o estado anterior como se pertencesse ao caso atual.

## Execução e retomada

Inicializar faz apenas leituras: valida os 500 pares caso/gabarito e confere que
versão e SHA-256 do contrato correspondem ao snapshot local.

```sh
.venv/bin/python studio_phase2.py init \
  --key-file res_v9/conta.key \
  --out res_phase2_v17 \
  --source ic_experimental.py \
  --contract 0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B \
  --max-cases 500 --delay 15 --execute

.venv/bin/python studio_phase2.py run \
  --key-file res_v9/conta.key \
  --out res_phase2_v17 \
  --max-cases 500 --delay 15 --execute
```

`run` e `resume` têm a mesma semântica: consultam primeiro qualquer transação já
registrada. Timeout pausa o processo, preservando o hash para retomada. O intervalo
mínimo de 15 segundos começa quando o runner observa o estado terminal; leituras e
geração local do relatório podem aumentar, mas nunca reduzir, esse intervalo.

Consultas locais não precisam da chave nem acessam o Studio:

```sh
.venv/bin/python studio_phase2.py status --out res_phase2_v17
.venv/bin/python studio_phase2.py report --out res_phase2_v17
```

O processamento de uma análise no Studio pode levar vários minutos. Por isso, 500
casos devem levar dezenas de horas, embora o intervalo adicional seja de 15 segundos.

## Artefatos locais

Tudo fica em `res_phase2_v17/`, ignorado pelo Git:

- `phase2.json`: journal retomável e orçamento de exatamente 500 envios;
- `events.jsonl`: log operacional append-only das 500 rodadas;
- `cases.jsonl`: resultados consolidados;
- `impressions.jsonl`: classificação e motivos compactos por caso;
- `report.md` e `summary.json`: relatório cumulativo;
- `receipts/`, `states/` e `terms/`: evidências sanitizadas por caso;
- `17.0.0-experimental.py`: snapshot imutável usado para conferir identidade.

O relatório é atualizado depois de cada caso. No acompanhamento, publicar balanço
a cada 50 casos e imediatamente em caso de falha relevante, padrão novo ou término.

## Validação local

```sh
.venv/bin/python -m unittest \
  test_ic_v10_1 test_ic_v10_2 test_ic_experimental test_studio_cycle test_studio_phase2
```
