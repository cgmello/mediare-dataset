# v32 — revisão do gate pareado de 50 casos

Data: 2026-10-02

Baseline: v30

Snapshot: `5d919274e51c3d671b222a41cfa6e88609c5fbe0f6029a2b0eaf37825ed10045`

## Resultado ajustado

| Métrica | v30 | v31 | v32 ajustada |
|---|---:|---:|---:|
| Maiorias locais | 39/50 | 37/50 | 39/50 |
| Painéis válidos | 50/50 | 48/50 | 50/50 |
| Saídas úteis | 28/50 | 24/50 | 28/50 |
| Pedidos pendentes | 56 | 46 | 56 |
| Correspondência com auditoria | 52/98 | 48/98 | 51/98 |
| Resultado exato resolvido/correto | 13/19 | 15/19 | 13/20 |
| Resultado binário resolvido/correto | 27/28 | 24/25 | 24/24 |

O gate bruto registrou 36/50 maiorias. Cinco casos continham erros de transporte
dos revisores; o retry recuperou `0164`, `0310` e `0343`, elevando o placar
ajustado para 39/50. `0145` e `0209` permaneceram `Disagree` por razões
semânticas.

## Transições frente à v30

- Recuperados: `0017`, `0021`, `0037`, `0050`, `0081`, `0083`, `0142`, `0243`.
- Perdas de voto: `0007`, `0014`, `0079`, `0088`, `0123`, `0209`, `0213`, `0370`.
- Permaneceram `Disagree`: `0145`, `0173`, `0476`.

As oito perdas foram dominadas por divergências de conclusão ou fontes entre
revisores. Em `0123`, um revisor discutiu a granularidade entre reconhecimento
e pagamento da mesma dívida; os dois objetos estão expressos na fonte, portanto
não houve omissão, mas essa fronteira deve permanecer observada no Studio.

## Sentinelas negativas obrigatórias

- `0046`: quatro pedidos preservados — rescisão, inexigibilidade, retirada
  cadastral e dano moral; resultado `Agree`.
- `0079`: dois pedidos preservados — reparos e prejuízos fiscais/CNO; o
  `Disagree` decorreu da conclusão/fontes do RP02, não de omissão.
- `0088`: RP01 e os três contrapedidos CR01/CR02/CR03 preservados; o
  `Disagree` decorreu do mérito de CR01–CR03, não do catálogo.

## Custo

- Gate de 50: 572 chamadas, 3.565.041 tokens, US$ 7,17268418722.
- Retry técnico de 5: 46 chamadas, 257.858 tokens, US$ 0,48135472075.

## Decisão

A v32 igualou a v30 nos principais agregados, preservou os ganhos seletivos de
catálogo e não repetiu as três regressões materiais da v31. O gate OpenRouter
está aprovado. O próximo passo recomendado é validar a v32 no Studio com uma
amostra aleatória, mantendo `0046`, `0079` e `0088` como controles obrigatórios.
