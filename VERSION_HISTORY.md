# Histórico de versões do IC Mediare

Este documento apresenta, de forma curta, a evolução funcional do Intelligent
Contract da Mediare. Ele complementa o [`CHANGELOG.md`](CHANGELOG.md), que contém
resultados experimentais, custos e detalhes operacionais.

As descrições foram reconstruídas a partir dos snapshots, do changelog e do
histórico Git. As versões v1–v4 antecedem a política formal de marcos e não foram
isoladas em tags; por isso, seus limites são aproximados. Desde a v24, somente
números major são usados publicamente, embora o literal interno mantenha
`x.0.0-experimental` por compatibilidade com o Studio.

| Versão | Data | Evolução resumida |
|---|---|---|
| **v1** | 2026-08-22 | Primeiro `MediareCommittee`: carregava um caso do dataset, solicitava análise jurídica ao comitê e armazenava um resultado/termo inicial on-chain. |
| **v2** | 2026-08-22 | Estruturou a resposta em JSON e tornou a comparação de equivalência mais explícita, com categorias comuns para responsabilidade e resultado. |
| **v3** | 2026-08-22/24 | Estabilizou a leitura dos casos pelo `case_id`, a URL do dataset e o tratamento dos valores e documentos informados no resumo. |
| **v4** | 2026-08-24/25 | Refinou padrões probatórios, regras de resultado e tratamento do termo; também iniciou um harness para comparar o comportamento do comitê fora do Studio. |
| **v5** | 2026-08-28 | Retirou da equivalência a exigência de que modelos produzissem listas idênticas de divergências, reduzindo desacordo meramente redacional. |
| **v6** | 2026-08-28 | Passou a aceitar rateio comprovado no mérito, inclusive culpa concorrente, e removeu a categoria ambígua de responsável “divergente”. |
| **v7** | 2026-08-28 | Unificou `parcial_ambos` e `ambos_culpa_concorrente` como resultados materialmente equivalentes. |
| **v8** | 2026-08-28 | Reforçou a coerência entre responsável e valores: repartições precisavam fechar numericamente e dúvidas sobre extensão não podiam zerar automaticamente a pretensão. |
| **v9** | 2026-08-29 | Tornou o parser de JSON e a conversão de números mais resistentes, evitando que erros reproduzidos por todos os nós parecessem consenso válido; contrato e harness passaram a usar o mesmo painel. |
| **v10** | 2026-09-04/06 | Migrou das quatro rubricas agregadas para catálogo por pedido (`RP`/`CR`) e três lentes — probatória, jurisprudencial e auditora. As revisões v10.1/v10.2 acrescentaram opções condicionais, valores desconhecidos distintos de zero, auditoria sequencial, diagnósticos e upgrade verificável por hash. |
| **v11** | 2026-09-06 | Criou um marco auditável com diagnósticos persistentes, changelog e mecanismo seguro de rollback do código. |
| **v12** | 2026-09-06 | Passou a explicar divergências por campo decisório, permitindo distinguir desacordo de catálogo, conclusão, valor, fonte ou opção. |
| **v13** | 2026-09-06 | Explicitou as categorias dos pedidos e as regras de coerência entre modalidade, natureza, valor, partes e decisão. |
| **v14** | 2026-09-06 | Introduziu revisão independente da proposta compartilhada do líder. A estrutura funcionou, mas a versão ainda não atingiu consenso estável. |
| **v15** | 2026-09-06 | Fez os validadores julgarem a aptidão da mesma proposta do líder, reduzindo divergências entre propostas alternativas igualmente defensáveis; obteve consenso no caso de referência. |
| **v16** | 2026-09-06 | Transformou a saída consensual em Termo de Opção acionável para o mediador, com faixas e pendências explícitas para discussão. |
| **v17** | 2026-09-06 | Tornou o Termo mais curto, factual e revisável. Obteve consenso e foi a primeira candidata recomendada para teste com mediador humano. |
| **v18** | 2026-09-07 | Substituiu a regeneração integral dos validadores por revisão compacta da proposta, reduziu textos e separou opções aprovadas de retenções. No lote 0001–0050 chegou a 38/50 consensos, mas não passou todos os gates de utilidade e estabilidade. |
| **v19** | 2026-09-07 | Derivou campos mecânicos de forma determinística, adicionou auditoria cruzada contra dupla contagem e permitiu um reparo dirigido da opção. Atingiu 47/50 consensos, sem inconsistências nos Termos aceitos. |
| **v20** | 2026-09-08 | Preservou a estabilidade da v19 e ampliou opções condicionais seguras: fórmulas com percentual aberto, faixas sem proporção inventada e alternativas não cumulativas. Tornou-se a principal baseline para Studio e OpenRouter. |
| **v21** | 2026-09-10 | Testou três candidatas isoladas — `schema`, `catalog` e `options` — nos mesmos 50 casos via OpenRouter, para medir separadamente estrutura, identificação de pedidos e geração de opções. Nenhuma candidata isolada substituiu a v20. |
| **v22** | 2026-09-11 | Combinou os melhores resultados das três v21: schema mais estável, correções declarativas de opções e apenas regras de catálogo consideradas seguras. |
| **v23** | 2026-09-11 | Formalizou o catálogo material auditável: `RP` passou a significar pedido do requerente e `CR`, somente contrapedido afirmativo do requerido. Separou erros técnicos de divergências semânticas e exigiu evidência estruturada dos revisores. |
| **v24** | 2026-09-11 | Endureceu a execução sem mudar a semântica RP/CR: controlou raciocínio dos modelos, recuperou painéis inválidos e normalizou diagnósticos impossíveis de dupla contagem ou valor. |
| **v25** | 2026-09-15/16 | Criou uma fronteira determinística para o catálogo: defesa, inexigibilidade, redução e recálculo não viram `CR`; restituições afirmativas permanecem. Consolidou acessórios da mesma cobrança e melhorou a validação jurisprudencial. No Studio, 49/50 casos aleatórios produziram resultado válido; apenas o caso 0124 ficou sem consenso. |
| **v26** | 2026-09-17/20 | Tratou o caso complexo 0124: excluiu providências exclusivamente judiciais do catálogo bilateral, preservou multas civis expressas e encurtou campos das lentes para evitar JSON truncado. No gate OpenRouter melhorou de 14/20 para 15/20 consensos e chegou a 20/20 painéis válidos. No Studio, o 0124 foi aceito na primeira rodada e a campanha com 49 novos holdouts terminou com 50/50 `MAJORITY_AGREE` e `SUCCESS`. |
| **v27** | 2026-09-20 | Impede que valores obtidos por soma/subtração/multiplicação sejam gravados como valor literal, remove CRs de retenção/limitação/parcelamento meramente defensivos, estabiliza riscos e conflitos inválidos da auditora em modo fail-closed e esclarece pedidos não monetários mínimos diretamente implícitos. No gate pareado OpenRouter, melhorou de 34/50 para 42/50 maiorias locais e de 47/50 para 50/50 painéis válidos, sendo aprovada para validação no Studio. |
| **v28** | 2026-09-21/22 | Corrige a normalização ampla demais identificada nos três `UNDETERMINED` da v27: preserva multa/encargo autônomo e honorários contratuais expressamente pedidos, sem reintroduzir verbas judiciais ou sucumbenciais. Os três casos passaram nos gates dirigidos; nos 20 sentinelas, chegou a 16/20 maiorias locais, 20/20 painéis válidos e 18/20 saídas úteis. Foi promovida ao Studio e está em validação numa nova amostra aleatória de 100 casos. |
| **v29** | 2026-09-23/24 | Separou direção do mérito de quantificação: informação apenas útil para valor, proporção, prazo ou modo deixou de bloquear `conceder`/`negar`, enquanto fatos capazes de inverter a direção deveriam permanecer em `necessita_informacao`. No gate balanceado OpenRouter, reduziu pendências de 98 para 27 e ampliou a cobertura, mas preservou somente 19/33 lacunas indispensáveis, obteve 39/50 maiorias locais e 47/50 painéis válidos. **Não promovida ao Studio**: a próxima correção deve recuperar precisão e estabilidade sem perder o ganho de cobertura. |

## Regra de manutenção

Ao criar uma nova versão major, este arquivo deve receber uma nova linha com:

1. a mudança funcional principal;
2. o resultado experimental conhecido, sem transformar simulação local em
   consenso do protocolo;
3. o estado da versão: candidata local, em validação no Studio, promovida ou
   abandonada.

Detalhes extensos, hashes, transações, custos e análises caso a caso continuam no
`CHANGELOG.md` e nos relatórios específicos.
