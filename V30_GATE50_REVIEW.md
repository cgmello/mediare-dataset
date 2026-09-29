# Revisão qualitativa do gate v30 — 50 casos

## Resultado executivo

- 50/50 casos concluídos; 39 `LOCAL_MAJORITY_AGREE` e 11 `LOCAL_MAJORITY_DISAGREE`.
- 50/50 painéis do líder foram estruturalmente válidos; 28/50 foram classificados como úteis.
- Custo: US$ 6,4878; 464 chamadas; 3.062.294 tokens.
- A v30 encontrou um ponto intermediário melhor que os dois gates da v29: reduziu as 98 pendências da v28 para 56, preservou 27/33 lacunas indispensáveis e manteve 27/28 acertos binários nos pedidos que resolveu.
- Decisão: **não promover ainda ao Studio**. Corrigir somente regras de catálogo demonstradas por vários casos, sem reabrir o portão probatório.

## Os 11 desacordos, caso a caso

| Caso | Diagnóstico | Leitura qualitativa | Ação segura |
|---|---|---|---|
| `0017` | Misto | A proposta integral de R$ 500 para energia foi retida pela própria auditoria porque o nexo com débito pretérito não estava demonstrado. As objeções para criar uma CR de retenção e remover a rescisão expressa são excesso dos revisores. | Preservar RP/CR; reforçar que uma conclusão retida pela auditora não deve ser reprovada como proposta final. |
| `0021` | Defeito real de catálogo | `CR01` era apenas compensação defensiva, limitada às dívidas já discutidas, sem saldo positivo pedido ao requerente. | Excluir compensação/retensão defensiva de CR quando não houver pagamento independente. |
| `0037` | Variação dos revisores | Um revisor quis remover a declaração; outro quis separar declaração e pagamento. O pedido expresso era negociar a própria dívida admitida, e o painel já havia passado no gate dirigido. | Não mudar a semântica; limitar objeções contraditórias de forma. |
| `0050` | Defeito real de catálogo | Houve sobreposição entre devolução dos valores pagos e indenização que repetia entrada e parcelas do mesmo financiamento. | Consolidar verbas materiais sobrepostas e evitar dupla contagem. |
| `0081` | Misto de mérito | Dois revisores aceitaram e dois entenderam prematura a negativa dos danos morais enquanto validade/coação do acordo permaneciam abertas. | Não criar regra global; usar como sentinela de dependência entre pedidos. |
| `0083` | Defeito real de catálogo | `RP07` transformou uma admissão narrativa do requerente em pedido autônomo. | Proibir que reconhecimento parcial feito na narrativa vire RP sem providência solicitada. |
| `0142` | Defeito real de catálogo | Declaração de inexigibilidade e abstenção de cobrar a mesma multa foram catalogadas como dois resultados, embora componham um único efeito material. | Unir declaração e obrigação acessória inseparável sobre a mesma dívida. |
| `0145` | Fronteira de política/revisor | Dois revisores exigiram “excesso de execução”, mas a regra vigente exclui providência exclusivamente processual; outro aprovou. | Manter exclusão processual até decisão explícita de produto; não alterar por este caso. |
| `0173` | Defeito real de catálogo | A devolução do financiamento foi pedida apenas se houvesse restituição ao consumidor; era defesa subsidiária, não contrapedido independente. | Excluir restituição condicional puramente defensiva de CR. |
| `0243` | Misto | O principal de oito cotas estava comprovado, mas multa/juros dependiam do conteúdo não resumido da convenção. Um revisor também tratou pedido de isenção como CR, contrariando a semântica congelada. | Separar direção segura do principal e acessórios condicionais; não criar CR de isenção. |
| `0476` | Defeito real de catálogo | A retenção de R$ 3.700 estava limitada à própria caução e não pedia saldo positivo ao requerente. Três revisores convergiram. | Tratar a retenção dentro do RP da caução, sem CR separada. |

## Síntese

- **6 defeitos reais de catálogo:** `0021`, `0050`, `0083`, `0142`, `0173`, `0476`.
- **3 casos mistos de mérito ou suficiência probatória:** `0017`, `0081`, `0243`.
- **2 casos dominados por fronteira de política ou variação dos revisores:** `0037`, `0145`.

## Recomendação para v31

Criar uma major separada, mantendo intacto o portão probatório da v30. A v31 deve aplicar somente quatro correções reversíveis: (1) excluir CR defensiva sem saldo positivo independente; (2) impedir que admissão narrativa vire pedido; (3) consolidar resultados e valores sobrepostos; e (4) unir declaração e obrigação acessória inseparável sobre a mesma dívida. Depois, repetir primeiro estes 11 casos e só então o gate pareado de 50.
