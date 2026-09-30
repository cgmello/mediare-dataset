# v32 — revisão do gate dirigido

Data: 2026-09-30

Baseline: v30

Snapshot final: `5d919274e51c3d671b222a41cfa6e88609c5fbe0f6029a2b0eaf37825ed10045`

## Resultado

- 9/9 casos concluídos e 9/9 painéis estruturalmente válidos.
- 7/9 maiorias locais `Agree`.
- 5/9 saídas classificadas automaticamente como imediatamente úteis.
- Snapshot final: 87 chamadas, 763.579 tokens e US$ 1,50451791091.
- Desenvolvimento completo em três rodadas: 268 chamadas, 2.348.062 tokens e
  US$ 4,75187808533.

## Caso a caso

| Caso | Resultado final | Leitura qualitativa |
|---|---|---|
| 0021 | Agree | Removeu o falso CR de benfeitorias: a fonte pedia apenas compensação defensiva com os aluguéis. |
| 0046 | Agree | Sentinela passou: rescisão, inexigibilidade, retirada cadastral e dano moral permaneceram separados. |
| 0050 | Agree | Preservou pedidos sobrepostos expressos e a contenção de dupla contagem pela auditora. |
| 0079 | Agree | Sentinela passou: reparos e prejuízos fiscais/CNO permaneceram em dois RPs. |
| 0083 | Disagree | Catálogo manteve os seis pedidos expressos; desacordo combina granularidade declarativa, conclusão e a limitação conhecida de múltiplos requeridos. |
| 0088 | Disagree | Sentinela passou: RP01, CR01, CR02 e CR03 foram mantidos; revisores divergiram sobre conclusão de lucros cessantes e retirada cadastral. |
| 0142 | Agree | Painel válido; resultado conservador ficou restrito a diligências. |
| 0173 | Agree | Recuperou painel válido e consenso local sem alterar o portão probatório da v30. |
| 0476 | Agree | Painel válido e consenso local; a saída permaneceu conservadora por depender de diligência. |

## Decisão

O gate dirigido foi aprovado. As três regressões materiais da v31 não se
repetiram, e as correções portadas foram obtidas sem modificar o teste
probatório da v30. O próximo controle é repetir o gate pareado de 50 casos no
OpenRouter. A v32 ainda não deve ser promovida ao Studio.
