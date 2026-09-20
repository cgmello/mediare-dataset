# Auditoria qualitativa pareada — v26 · 50 casos

## Resultado executivo

A campanha foi concluída em **50/50 casos**. No Studio, **50/50** chegaram a `ACCEPTED / MAJORITY_AGREE`; no OpenRouter, **34/50** obtiveram maioria local. A diferença não é contradição: o Studio mede consenso real do protocolo, enquanto o runner local preserva objeções individuais e permite inspecionar o conteúdo.

A leitura humana do texto-fonte, catálogo do líder e objeções dos revisores classificou **33 casos sem defeito material**, **1 caso de variação/excesso do revisor**, **13 casos com defeito material** e **3 falhas técnicas**.

> Conclusão: a v26 é tecnicamente forte no Studio, mas a inspeção local revela padrões suficientemente repetidos para justificar uma v27 conservadora. Consenso de protocolo não deve ser confundido com perfeição semântica do painel.

## Padrões que justificam a v27

1. **CR meramente defensivo** — casos 0136, 0240, 0347, 0380 e 0434 transformaram limitação, parcelamento ou legitimidade da retenção em contrapedido autônomo.
2. **Valor aritmético não literal** — casos 0313, 0468, 0479 e 0488 calcularam subtrações ou multiplicações que deveriam permanecer como fórmula com valor nulo.
3. **Granularidade/omissão** — houve omissão material em 0028 e 0124, duplicação em 0354 e remédio inventado em 0368.
4. **Estabilidade mecânica** — 0119 e 0286 falharam por enum/ID da auditoria; 0472 não conseguiu representar um pedido não monetário diretamente implícito no bloco intitulado ‘Fatos e pedidos’.

## Limites da correção

A v27 não deve relaxar o quórum local nem ensinar respostas específicas dos casos. As correções seguras são: validar deterministicamente que valores do catálogo aparecem literalmente na fonte; ampliar apenas marcadores inequívocos de defesa/condição dependente; normalizar riscos e IDs inválidos da auditoria em modo fail-closed; e esclarecer a regra de pedidos não monetários diretamente implícitos, sem inventar indenização, valor ou obrigação adicional.

## Análise caso a caso

| Caso | Studio | OpenRouter | Adjudicação | Observação |
|---:|---|---|---|---|
| 0026 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Catálogo coerente com rescisão, desocupação e aluguéis vencidos/vincendos. |
| 0028 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Omitiu a alternativa expressa de rescisão amigável com desocupação; condições de pagamento são dependentes e não exigem RP próprio. |
| 0036 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Variação do revisor** | O valor de R$ 13.000,00 é pedido literal; juros são acessórios do mesmo crédito. A inconsistência com o pagamento anterior pertence ao mérito, não ao catálogo. |
| 0053 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de ressarcimento material, com valor literal e sem duplicação. |
| 0060 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Danos emergentes, lucros cessantes e danos morais foram separados como resultados autônomos. |
| 0068 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Danos materiais e morais foram separados com valores literais. |
| 0071 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de danos morais, fiel ao texto-fonte. |
| 0084 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Parcela contratual e serviços adicionais são créditos autônomos e literais. |
| 0086 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Quatro resultados materiais distintos foram preservados sem cálculo novo. |
| 0101 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Danos materiais, morais e obrigação de cessar risco são resultados autônomos; objeção minoritária não demonstrou duplicação. |
| 0105 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Obrigações de fazer, dano moral e contrapedido afirmativo foram corretamente separados. |
| 0110 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Catálogo amplo, mas cada providência possui objeto negociável próprio. |
| 0119 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Falha técnica** | A auditora repetiu risco fora do enum em três tentativas; o mérito do painel não chegou ao gate local. |
| 0122 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Reparação, despesa técnica e dano moral foram preservados sem remédio processual. |
| 0124 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | O líder omitiu o pedido expresso de restituição de valores cobrados indevidamente; quatro revisores convergiram na omissão. |
| 0131 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | As multas descritas formam uma cobrança agregada coerente com o pedido literal. |
| 0136 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | CR01 apenas limita defensivamente a responsabilidade pelo RP; não é contrapedido afirmativo autônomo. |
| 0154 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Rescisão, restituição e dano moral são resultados autônomos e expressos. |
| 0160 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | O catálogo preservou os resultados principal e subsidiário sem fundi-los. |
| 0169 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | O próprio pedido agrega dano material e lucros cessantes em R$ 20.000,00; separá-los seria rigor excessivo. |
| 0178 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Restituição principal, restituição subsidiária e dano moral estão corretamente separados. |
| 0184 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Parcelas e multa contratual são resultados monetários expressos e autônomos. |
| 0193 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparação material, com valor literal. |
| 0197 | MAJORITY_AGREE · 2 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Ressarcimento e drenagem são providências autônomas de pagar e fazer. |
| 0203 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparos, fiel ao texto-fonte. |
| 0240 | MAJORITY_AGREE · 2 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | CR01 é pedido dependente de parcelamento do próprio débito; deve ser condição de negociação do RP, não contrapedido. |
| 0280 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Reparo e lucros cessantes são resultados autônomos com valores literais. |
| 0281 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparação material, fiel ao texto-fonte. |
| 0286 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Falha técnica** | A auditora apontou conflito de dupla contagem com ID inválido e não convergiu após três correções. |
| 0311 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparação do veículo com base literal. |
| 0313 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Calculou R$ 8.200,00 por subtração e criou conclusão da obra sem pedido expresso suficiente. |
| 0317 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparação material, com valor literal. |
| 0336 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparação material, com valor literal. |
| 0345 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Cotas, multa e juros pertencem à mesma cobrança; a objeção de separação foi rigor excessivo. |
| 0347 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Defeito material** | CR01 apenas afirma a legitimidade defensiva da retenção e não pede providência autônoma contra o requerente. |
| 0354 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Duplicou o mesmo dano material em reparos e ressarcimento, embora o texto descreva uma única recomposição. |
| 0359 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de reparos, fiel ao texto-fonte. |
| 0368 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Inventou devolução do preço do veículo; o texto só quantifica o reparo do motor. |
| 0375 | MAJORITY_AGREE · 2 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Ressarcimento e drenagem são providências autônomas. |
| 0380 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | CR01 é mera defesa da retenção; devolução e multa do requerente permanecem autônomas. |
| 0390 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | A providência de conserto é diretamente identificável e não recebeu valor inventado. |
| 0424 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de ressarcimento, com valor literal. |
| 0434 | MAJORITY_AGREE · 2 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | CR01 é mera justificativa defensiva da retenção, não contrapedido; o desconto integra a negociação do RP. |
| 0459 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | O total não foi calculado; aluguéis e compensação com caução permaneceram em um único resultado. |
| 0468 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Calculou R$ 25.000,00 por subtração e acrescentou conclusão da obra sem pedido expresso suficiente. |
| 0472 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Falha técnica** | O líder devolveu catálogo vazio três vezes; o schema v26 exige ao menos um pedido e não tratou a cessação implicitamente pedida. |
| 0479 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Calculou R$ 13.600,00 e separou a compensação com caução, que é condição do mesmo débito. |
| 0488 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_DISAGREE` | **Defeito material** | Calculou R$ 9.300,00; a fonte informa 3 × R$ 3.100,00, portanto o valor final deve permanecer nulo. |
| 0491 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Parcelas e multa contratual foram preservadas como resultados expressos. |
| 0495 | MAJORITY_AGREE · 1 rodada(s) | `LOCAL_MAJORITY_AGREE` | **Adequado** | Pedido único de ressarcimento, com valor literal. |

## Casos prioritários para regressão

- Defeitos materiais: 0028, 0124, 0136, 0240, 0313, 0347, 0354, 0368, 0380, 0434, 0468, 0479, 0488.
- Falhas técnicas: 0119, 0286, 0472.
- Controle contra excesso do revisor: 0036.
- Controles positivos sem alteração esperada: 0060, 0105, 0178, 0197 e 0459.

## Critério de promoção sugerido

A v27 só deve ir ao Studio depois de: (a) eliminar as três falhas técnicas; (b) corrigir os padrões determinísticos de CR defensivo e valor inferido; (c) não piorar os controles positivos; e (d) repetir estes 50 casos no OpenRouter para comparação pareada. Somente então faz sentido sortear 100 novos casos para o Studio.
