# Relatório consolidado da v20 — casos 0001–0100

## Conclusão

A v20 é o marco estável a preservar. Nos dois lotes do Studio, processou 100
casos, incluindo o holdout 0051–0100 que não havia sido usado no seu ajuste.
Produziu opção integral ou parcial em 79 casos, obteve `MAJORITY_AGREE` em 95
e terminou 96 transações como `FINALIZED`.

Os resultados sustentam uma v21 incremental, não uma reescrita. Os principais
alvos restantes são falhas de schema, instabilidade do catálogo e recuperação
conservadora de casos que terminam sem opção acionável.

## Studio

| Métrica | 0001–0050 | 0051–0100 | Total |
|---|---:|---:|---:|
| `MAJORITY_AGREE` | 48 | 47 | 95 |
| `FINALIZED` | 48 | 48 | 96 |
| `APTO_INTEGRAL` | 27 | 25 | 52 |
| `APTO_PARCIAL_COM_RETENCOES` | 13 | 14 | 27 |
| `SOMENTE_DILIGENCIAS` | 2 | 6 | 8 |
| `SEM_OPCAO_APROVADA` | 6 | 2 | 8 |
| `FALHA_TECNICA` | 2 | 3 | 5 |
| Rotações | 32 | 24 | 56 |

No holdout, os casos 0062, 0082 e 0083 foram classificados como falha técnica.
Os diagnósticos de revisores concentraram-se em catálogo e tratamento da opção.
Os seis casos somente com diligências foram 0054, 0058, 0061, 0072, 0075 e
0085; 0086 e 0100 não tiveram opção aprovada.

## OpenRouter — v20, casos 0001–0050

- 42/50 painéis de líder válidos;
- 37/50 saídas de líder operacionalmente úteis;
- 20/50 maiorias locais;
- 519 requisições, 4.714.908 tokens e US$ 11,2932 de gasto reconciliado;
- 35/35 revisões solicitadas ao Mistral falharam no formato do schema;
- oito líderes falharam: quatro na auditora, três na probatória e um na
  jurisprudencial;
- entre revisões válidas, catálogo foi o motivo mais frequente de rejeição.

O OpenRouter é instrumento diagnóstico; sua maioria local não substitui consenso
GenLayer. O relatório completo está em `OPENROUTER_V20_INVESTOR_REPORT.html`.

## Barreiras que nenhuma v21 pode remover

- três lentes, EP único e Termo determinístico;
- gabaritos fora do IC e dos prompts;
- citação literal e valor presente na fonte resumida;
- distinção entre valor pedido, base de discussão e valor devido;
- retenção de risco de escopo, suporte, polo, premissa ou valor inventado;
- proibição de dupla contagem, incluindo a regressão do caso 0027;
- falha fechada quando um defeito material não puder ser corrigido com segurança.
