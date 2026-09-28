# v30 — revisão qualitativa do primeiro gate dirigido

## Resultado

O gate de 12 casos terminou com 10 maiorias locais e 11 painéis válidos. Ele não
autoriza ainda o gate de 50: houve uma falha técnica em `0037` e algumas
abstenções ignoraram informação que já estava resumida. Ao mesmo tempo, a
métrica automática foi excessivamente pessimista porque escolheu uma única
“direção” para painéis em que as lentes probatória e jurisprudencial discordam.

## Leitura caso a caso

| Caso | Avaliação qualitativa |
|---|---|
| `0003` | A pergunta sobre o laudo “prevalecer” era desnecessária: DR já resume que o laudo atribui a causa a fabricação/instalação. A divergência deve ser ponderada, não tratada como conteúdo ausente. |
| `0079` | A abstenção no reparo é defensável porque existem versões técnicas específicas e conflitantes. A negativa dos prejuízos fiscais eventuais também é defensável: não há perda atual descrita. |
| `0118` | O catálogo consolidou o segundo pedido como `RP03`; portanto, comparar apenas o ID gerou falso erro. Materialmente, DR e PR já descrevem a conclusão pericial sobre os vícios internos; perguntar novamente foi conservador demais. |
| `0017` | O painel preservou lacunas reais em energia e danos ao imóvel. A caução e o aluguel proporcional possuem suporte suficiente na entrada; a auditoria automática que exigia nova informação nesses pontos não deve ser tratada como verdade absoluta. |
| `0346` | Painel válido e resolvido; controle preservado. |
| `0037` | Falha técnica. O próprio requerente admite a dívida e pede negociação de pagamento; o catálogo não deve criar pagamento contra o requerido nem duplicar declaração e pagamento. O reparo também precisava explicar `valor=0` para não monetário e valor positivo quando a cifra monetária já está definida. |
| `0054` | O reparo da piscina consta como já executado. Não cabe pedir nova prova de nexo para ordenar a mesma prestação; o pedido deve ficar sem objeto atual. O dano moral continua autônomo. |
| `0243` | O principal estava correto. A multa de 2% não deveria ficar bloqueada só porque o conteúdo da convenção não foi transcrito quando há base legal independente para o limite pedido. |
| `0343` | A abstenção é adequada: “laudo mecânico” aparece apenas como nome, sem conteúdo, e há defesa específica de desgaste natural. O gabarito usa fatos que não estão no resumo entregue ao IC. |
| `0482` | A lente probatória pode pedir confirmação do conteúdo dos vídeos/BOs, pois eles são apenas listados; a lente jurisprudencial pode considerar a narrativa e a documentação indicada suficientes. A divergência entre lentes é informativa, não erro automático. |
| `0486` | A entrada já descreve cláusula de multa de duas mensalidades e a requerida admite que não cancelou formalmente. Perguntar novamente se houve rescisão sem aviso é conservador demais. |
| `0163` | O gabarito nega com base em perícia judicial, mas essa conclusão não está nos quatro blocos fornecidos ao IC. A lente probatória fez corretamente perguntas de nexo/falha; a lente jurisprudencial concedeu sob responsabilidade objetiva. Classificar o painel inteiro como “conceder” ocultou essa divergência legítima. |

## Correção aplicada antes da repetição

- Diferenciar conclusão documental resumida de documento meramente listado.
- Não reabrir admissão expressa contra o interesse da própria parte.
- Não bloquear o mérito quando outra base independente resolve a direção.
- Tratar obrigação expressamente cumprida como sem objeto atual.
- Impedir que pedido do devedor para negociar a própria dívida inverta os polos.
- Tornar o reparo de coerência explícito para valores e polos monetários e não monetários.

Os gabaritos continuam sendo usados apenas depois da execução. Quando o gabarito
depende de sentença, perícia ou outro fato ausente da entrada, a discrepância é
registrada como limitação do dataset, não como erro automático do IC.
