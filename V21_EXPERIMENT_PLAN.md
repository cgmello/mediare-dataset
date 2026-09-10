# Plano experimental v21

## Decisão

Três candidatas independentes partem byte a byte do snapshot v20. Cada uma
altera uma única classe de problema e será executada nos mesmos casos 0001–0050,
com a mesma rotação de cinco modelos e quórum local 3/4.

| Candidata | Alteração isolada | Hipótese |
|---|---|---|
| `v21-schema` | resposta do revisor usa `catalogo=completo|incompleto` e lista fechada de falhas | evitar objetos indevidos em campos booleanos sem relaxar reprovação |
| `v21-catalog` | unidade objetiva de pedido no catálogo e na revisão | reduzir divergência de granularidade sem aceitar omissão ou invenção |
| `v21-options` | declaração sem devedor/credor e instrução conservadora para base documental | recuperar opções sem transformar pauta em dívida |

## Execução OpenRouter

- Uma pasta, snapshot, journal, cache e teto de custo por candidata.
- Casos 0001–0050; gabaritos nunca entram no prompt.
- Mesmo `openrouter_models_v20.json`, roteamento sem fallback e política de
  não coleta quando suportada.
- Respostas concluídas são reutilizadas somente dentro da mesma candidata.
- Estimativa inicial: aproximadamente US$ 11,30 por candidata; teto persistente
  de US$ 15 por campanha.

## Seleção

A melhor candidata deve primeiro preservar as barreiras de segurança. Entre as
elegíveis, a ordem de decisão é:

1. maior número de painéis de líder válidos;
2. maior número de saídas integrais ou parciais;
3. maior número de maiorias locais;
4. menos falhas estruturais e menor custo como desempate;
5. inspeção dos casos que mudaram, antes da escolha final.

Metas orientativas: pelo menos 45/50 líderes válidos, 40/50 saídas úteis e
zero promoção insegura. Maioria local é diagnóstico, não consenso protocolar.

## Studio

Somente a candidata escolhida e congelada será instalada no Studio. O holdout
será 0101–0150, sem ajuste durante a campanha, com intervalo mínimo de 15
segundos. Gates: pelo menos 47/50 `MAJORITY_AGREE`, no máximo duas falhas
técnicas, pelo menos 40/50 opções integrais ou parciais, zero inconsistência e
preservação das regressões de segurança.
