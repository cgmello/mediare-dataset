# v24 — análise dirigida dos casos 0023 e 0048

## Resultado

Os dois casos foram repetidos após o gate de 20 sentinelas, usando a mesma
fonte v24, a mesma seleção e a mesma rotação de modelos. Ambos formaram painéis
válidos, mas ambos terminaram `LOCAL_MAJORITY_DISAGREE`.

| Caso | Resultado v24 dirigido | Leitura |
|---|---|---|
| 0023 | 11 chamadas, 94.528 tokens, US$ 0,217944; 2 Agree e 2 Disagree | Regressão semântica reproduzível no líder: ele criou `CR01`–`CR05` para exclusões, recálculos e negativa de caução que são somente defesa. GPT-5.4 e GLM marcaram todos como excesso; Claude e DeepSeek aceitaram o catálogo. |
| 0048 | 11 chamadas, 83.613 tokens, US$ 0,151497; 2 Agree, 1 Disagree e 1 erro | O líder produziu `APTO_INTEGRAL`, igual ao baseline do Studio. A instabilidade restante está nos revisores: GPT-5.4 pediu anulação de valor/inclusão de compensação, e Mistral falhou no formato compacto. |

## Decisão de promoção

Não promover a v24 ao Studio ainda. O caso 0023 mostra um erro material
repetível na extração de `CR`: o sistema final é fail-closed porque a maioria
dos revisores bloqueia a proposta, mas isso ainda pode gerar `Disagree` no
protocolo. O caso 0048 melhorou em relação à falha técnica anterior, porém sua
revisão não atingiu estabilidade suficiente.

Para a v25, manter a semântica RP/CR e acrescentar uma regra determinística que
rejeite como `CR` qualquer exclusão, redução, recálculo, índice, perícia ou
negativa sem pedido afirmativo autônomo do requerido. Separadamente, corrigir o
formato compacto do Mistral e a objeção de valor/compensação em 0048.

## Custo adicional

Esta repetição acrescentou 22 chamadas, 178.141 tokens e US$ 0,36944089236 ao
orçamento OpenRouter. O relatório consolidado inclui esses recibos na linha v24.
