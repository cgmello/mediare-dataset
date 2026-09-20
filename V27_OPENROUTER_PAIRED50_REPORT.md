# Gate pareado OpenRouter — v26 × v27 · 50 casos

## Resultado

| Métrica | v26 | v27 | Variação |
|---|---:|---:|---:|
| Casos concluídos | 50/50 | 50/50 | — |
| Maiorias locais | 34/50 | **42/50** | **+8** |
| Painéis de líder válidos | 47/50 | **50/50** | **+3** |
| Saídas automaticamente úteis | 19/50 | 19/50 | 0 |
| Chamadas API | 453 | 475 | +22 |
| Tokens | 2.381.020 | 2.424.218 | +43.198 |
| Custo | US$ 5,2026425779065 | **US$ 5,1930646974235** | −US$ 0,0095778804830 |

A v27 passou o gate local para promoção ao Studio. O runner não representa
consenso do protocolo; mede estabilidade do painel e preserva os pareceres dos
quatro revisores para diagnóstico.

## Mudanças de resultado

Nove casos passaram de `LOCAL_MAJORITY_DISAGREE` para
`LOCAL_MAJORITY_AGREE`: `0119`, `0240`, `0286`, `0313`, `0380`, `0434`,
`0472`, `0479` e `0488`.

- `0119`, `0286` e `0472`: as três falhas técnicas da v26 foram eliminadas.
- `0240`, `0380` e `0434`: parcelamento ou legitimidade de retenção deixaram
  de ser tratados como contrapedidos autônomos.
- `0313`, `0479` e `0488`: montantes obtidos por conta deixaram de ser
  apresentados como valores literais do pedido.

Houve uma oscilação de `Agree` para `Disagree` em `0197`. O catálogo do líder
continuou correto, com ressarcimento e drenagem separados. Dois revisores
aprovaram; um inventou CR a partir da frase defensiva “farei drenagem se
preciso”, e outro confundiu uma objeção à opção com defeito de catálogo. Isso é
variação/excesso dos revisores, não regressão causada pelas regras v27.

## Oito divergências remanescentes

| Caso | Diagnóstico |
|---:|---|
| 0028 | Defeito real: ainda omite a alternativa expressa de rescisão amigável e desocupação. |
| 0036 | Controle de excesso dos revisores: valor final é literal e juros são acessórios da mesma cobrança. |
| 0124 | Defeito real e conhecido: líder Claude ainda omite restituição/multa material; os revisores rejeitam corretamente. |
| 0136 | CR defensivo foi removido; divergência remanescente mistura parcelas vincendas e conclusão sobre água/gás. |
| 0197 | Variação dos revisores; catálogo do líder permanece materialmente correto. |
| 0354 | Defeito real: o líder ainda duplica reparo e responsabilidade pelo mesmo dano. |
| 0368 | Defeito real: o líder inventa restituição/abatimento do preço quando o texto só quantifica reparo. |
| 0468 | Valor calculado foi anulado, mas o líder ainda inventa conclusão da obra sem pedido expresso. |

Os cinco defeitos semânticos remanescentes (`0028`, `0124`, `0354`, `0368`,
`0468`) foram corretamente barrados pela maioria dos revisores. Não é seguro
transformá-los agora em regras determinísticas amplas: isso poderia omitir
pedidos autônomos legítimos. Eles permanecem como backlog para uma futura v28,
após evidência em novos holdouts.

## Decisão de promoção

A v27 é promovida para validação no Studio porque:

1. aumentou as maiorias locais em oito casos líquidos;
2. chegou a 50/50 painéis válidos;
3. eliminou todas as falhas técnicas alvo;
4. corrigiu padrões materiais recorrentes sem prejudicar os controles positivos;
5. manteve fail-closed os defeitos semânticos que ainda não têm correção geral segura.

Próximo passo: sortear 100 casos reproduzíveis do universo de 1.000 casos,
registrar o manifesto/seed, atualizar o contrato no Studio e executar a campanha.

