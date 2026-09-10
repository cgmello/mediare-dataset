# Changelog experimental — Mediare IC / Studio

Registro para o relatorio de evolucao. Datas em America/Sao_Paulo, salvo indicacao.
Resultados negativos e versoes nao analisadas permanecem no historico.
**A v17 obteve consenso e foi recomendada para teste com mediador; nenhum Termo
gerado constitui acordo, condenacao ou validacao juridica de merito.**

## Candidatas v21 e fechamento da v20 — 2026-09-10

- Criado o runner retomável de pseudonimização para as 500 novas decisões. Dois
  modelos de alta qualidade detectam entidades independentemente, mas todas as
  substituições são aplicadas local e deterministicamente para preservar fatos,
  datas e valores. IDs internos 0501–1000, iniciais sem partículas portuguesas,
  revisão de cada processo, cache privado, auditoria local, ZDR obrigatório,
  proibição de coleta e teto de US$ 30 estão documentados em
  `PSEUDONYMIZATION_PLAN.md`.

- A v20 foi congelada como baseline após 100 casos no Studio: 95
  `MAJORITY_AGREE`, 96 `FINALIZED`, 52 `APTO_INTEGRAL`, 27
  `APTO_PARCIAL_COM_RETENCOES`, oito `SOMENTE_DILIGENCIAS`, oito
  `SEM_OPCAO_APROVADA`, cinco falhas técnicas e 56 rotações.
- O holdout 0051–0100 confirmou 39/50 opções integrais ou parciais. Casos 0062,
  0082 e 0083 falharam tecnicamente; catálogo e tratamento da opção foram os
  diagnósticos dominantes nas discordâncias.
- A campanha local v20 terminou 50/50: 42 painéis de líder válidos, 37 saídas
  úteis, 20 maiorias locais, 519 requisições, 4.714.908 tokens e US$ 11,2932
  de gasto reconciliado. O relatório do investidor foi atualizado com os 50
  resultados.
- Criadas três candidatas independentes a partir do mesmo snapshot: `v21-schema`
  substitui os booleanos ambíguos da revisão por enums de falha fechados;
  `v21-catalog` define a unidade material de pedido; `v21-options` especializa
  declarações e bases documentais condicionais.
- Nenhuma candidata relaxa fonte literal, auditoria, dupla contagem, polos,
  distinção entre base e dívida ou falha fechada. Hipóteses, gates e ordem de
  seleção estão em `V21_EXPERIMENT_PLAN.md`; o baseline consolidado está em
  `V20_FINAL_REPORT.md`.
- O runner OpenRouter e o relatório HTML deixaram de presumir a versão v20; cada
  campanha agora registra e apresenta a versão real do snapshot congelado.
- Adicionado comparador reprodutível para as três campanhas v21. A classificação
  automática aplica gates antes das métricas de utilidade e nunca promove uma
  candidata sem inspeção manual dos casos alterados e confirmação no Studio.
- Adicionado orquestrador retomável que aguarda uma campanha v21 já ativa,
  executa as candidatas restantes estritamente em sequência e para no checkpoint
  de seleção manual. O cache do runner continua impedindo cobrança duplicada.
- O coletor CJPG foi refeito para expansão em lotes retomáveis de no máximo 50,
  deduplicação incremental, intervalo mínimo, relatório sem conteúdo judicial e
  proteção contra corpo de sentença absorvido como metadado. A coleta não chama
  LLM; o plano da transformação posterior e a avaliação CourtListener/RECAP
  estão em `DATASET_EXPANSION_PLAN.md`.
- Primeiro lote de expansão concluído: 50 novas decisões públicas, sendo 40 da
  busca de cobrança e dez de consumo. O acervo bruto local passou de 244 para
  294 processos únicos. Uma resposta HTTP da busca de cobrança falhou depois do
  lote parcial, sem perda dos itens já coletados; outras categorias completaram
  o lote. `dataset_expansion_batch_01.json` registra somente telemetria e zero
  chamadas de LLM; `sentencas.jsonl` continua local e ignorado pelo Git.
- Segundo lote concluído com 50 novas decisões da busca de locação, sem erros e
  sem chamadas de LLM. O acervo bruto local chegou a 344 processos únicos, ou
  100 dos 500 adicionais planejados. Telemetria em
  `dataset_expansion_batch_02.json`.
- Terceiro lote concluído com mais 50 decisões da busca de locação, sem erros ou
  chamadas de LLM. O staging privado chegou a 394 processos únicos, totalizando
  150 dos 500 adicionais. Telemetria em `dataset_expansion_batch_03.json`.
- Quarto lote concluído com 50 novas decisões da busca de locação, sem erros ou
  chamadas de LLM. O staging privado chegou a 444 processos únicos, totalizando
  200 dos 500 adicionais. Telemetria em `dataset_expansion_batch_04.json`.
- Quinto lote concluído com 50 novas decisões da busca de locação. A
  deduplicação atravessou páginas parcialmente repetidas sem erros e sem LLM. O
  staging privado chegou a 494 processos únicos, totalizando 250 dos 500
  adicionais. Telemetria em `dataset_expansion_batch_05.json`.
- Sexto lote concluído com 50 novas decisões da busca de locação. A retomada
  percorreu 28 páginas para superar duplicatas, sem erros ou chamadas de LLM. O
  staging privado chegou a 544 processos únicos, totalizando 300 dos 500
  adicionais. Telemetria em `dataset_expansion_batch_06.json`.
- Sétimo lote concluído com 50 novas decisões da busca de locação. A retomada
  percorreu 33 páginas, sem erros ou chamadas de LLM. O staging privado chegou
  a 594 processos únicos, totalizando 350 dos 500 adicionais. Telemetria em
  `dataset_expansion_batch_07.json`.
- Oitavo lote concluído com 50 novas decisões da busca de locação. A retomada
  percorreu 38 páginas, sem erros ou chamadas de LLM. O staging privado chegou
  a 644 processos únicos, totalizando 400 dos 500 adicionais. Telemetria em
  `dataset_expansion_batch_08.json`.
- Nono lote concluído com 50 novas decisões da busca de locação. A retomada
  percorreu 43 páginas, sem erros ou chamadas de LLM. O staging privado chegou
  a 694 processos únicos, totalizando 450 dos 500 adicionais. Telemetria em
  `dataset_expansion_batch_09.json`.
- Décimo lote concluído com 50 novas decisões da busca de locação. A retomada
  percorreu 48 páginas, sem erros ou chamadas de LLM. A meta de coleta foi
  alcançada: o staging privado passou de 244 para 744 processos únicos, somando
  500 novas fontes. Telemetria em `dataset_expansion_batch_10.json` e consolidação
  em `dataset_expansion_summary.json`.

## Avaliação v20 — Studio holdout e OpenRouter — 2026-09-09

- Iniciado holdout fora da amostra com os casos 0051–0100 e o snapshot v20
  congelado. Como a instância histórica não mantinha bytecode, foi implantado o
  bootstrap `0xCb46400C0bD70a694673ED28f6A9Adec6915aCae` e instalada a mesma v20,
  SHA-256 `d2b719467cf96874244a4e5990c501c0b93ef5d900dc0bc93480e71e43cbadf4`.
  Deploy: `0xfc6c6f93ebd7301578adb51991ff746a45d9314cf7159eaecb594dc521c5c212`;
  upgrade: `0x0088af450dc6e0c7ce18cb2b319be03724df62e638811f8d3222054a0d1bd34b`.
- Adicionado `openrouter_runner.py`, que importa as funções do snapshot exato da
  v20 e executa líder rotativo mais quatro revisores. Respostas, hashes de prompt,
  votos, diagnósticos, tokens, latência e custo informado pela API são mantidos
  localmente; a chave nunca é persistida nos resultados.
- O cache por chamada torna a retomada idempotente: resposta concluída não é
  solicitada nem cobrada novamente. Há teto de gasto, consultas sanitizadas de
  saldo, espera entre requisições e parada imediata para erros de autenticação,
  pagamento ou autorização.
- O relatório em inglês foi consolidado em um único HTML:
  `OPENROUTER_V20_INVESTOR_REPORT.html`. Ele reúne ganho experimental, comparação
  Studio/OpenRouter, resultados, tempo, custo e proposta de uso do crédito.
- A primeira etapa local foi limitada aos casos 0001–0010 dentro da campanha
  definitiva 0001–0050. São 50 papéis de modelo; como o líder chama catálogo e
  lentes separadamente, a contagem real esperada é de pelo menos 80 requisições.
- A chave foi validada com uma geração mínima. O endpoint de conta informou
  US$ 1.120,00 em créditos históricos e US$ 1.106,973649132 de uso, saldo próximo
  de US$ 13,03. O limite de US$ 500 da chave é autorização de gasto, não saldo.
- Cinco testes unitários do runner aprovados antes do piloto.
- Piloto concluído nos casos 0001–0010: 103 requisições HTTP, 808.949 tokens
  itemizados e US$ 2,248825110 de custo reconciliado pela variação de uso da
  própria chave. Médias: US$ 0,224882511 por caso, US$ 0,021833 por requisição
  e 288,5 segundos de execução ativa por caso.
- Oito líderes produziram painel válido e útil; seis atingiram o quórum analítico
  local. Os casos 0001–0006 coincidiram com o Studio tanto em consenso quanto na
  classe operacional. A classe coincidiu em 7/10 no total.
- Os casos 0007–0008 tiveram opção integral do líder, mas somente 2/4 revisores:
  DeepSeek recusou compatibilidade das fontes e Mistral falhou no schema booleano
  após três tentativas. O 0009 falhou na auditora do líder DeepSeek; o 0010 falhou
  na coerência entre concessão monetária e valor nulo do líder Mistral.
- O piloto detectou respostas cobradas sem conteúdo final em modelos de raciocínio.
  O runner passou a contabilizar respostas vazias, tentativas HTTP e custo por
  variação do uso da chave. GLM 5.3 foi estabilizado com esforço `low`; o próximo
  lote deve controlar também o orçamento de raciocínio do DeepSeek antes de
  promovê-lo novamente a líder.
- Projeção linear: US$ 11,2441 para 50 casos e US$ 112,4413 para 500. Os 40 casos
  restantes custariam cerca de US$ 8,9953; o saldo real ao fim do piloto era
  US$ 10,7775. Apesar de suficiente na projeção, o teto persistente da campanha
  continua em US$ 10 e não será elevado sem nova decisão.
- Relatório único em inglês gerado em `OPENROUTER_V20_INVESTOR_REPORT.html`, com
  comparação Studio/OpenRouter, observação de cada caso, telemetria por modelo,
  tempo, custo reconciliado, projeções e plano condicional para o grant. Suíte
  completa concluída com 206 testes aprovados.
- Após revisar o piloto, o usuário autorizou a retomada dos 40 casos. O runner
  ganhou ação explícita e auditável `set-budget`; o teto total será elevado de
  US$ 10 para US$ 12, permitindo no máximo cerca de US$ 9,66 adicionais após a
  liquidação tardia do piloto. O saldo conferido antes da retomada era US$ 10,6893.

## Pós-processador off-chain de Termos — 2026-09-09

- Os blocos de assinatura do acordo final passam a repetir o documento do
  requerente e do requerido. O rótulo é inferido pela quantidade de dígitos
  (`CPF`, `CNPJ` ou, quando indeterminável, `CPF/CNPJ`). O modo rascunho continua
  sem campos de assinatura.

- O gerador final passa a aceitar `--rascunho` para demonstrações com o arquivo
  de exemplo ainda não preenchido. O modo substitui todas as identidades por
  personagens, documentos e endereços inequivocamente fictícios; exibe alertas
  de simulação sem validade em Markdown/HTML/JSON e suprime assinaturas e
  testemunhas. Sem a diretiva, a validação estrita dos dados reais permanece.

- Adicionado `termo_acordo.py`, segundo estágio determinístico que converte um
  cenário aceito em Termo Final de Mediação e Acordo Extrajudicial. Ele exige
  aceite unânime, dados formais completos e fechamento de toda fórmula/faixa.
- Fórmulas usam percentual explícito e aritmética decimal; o valor final é
  arredondado ao centavo e escrito em algarismos e por extenso. Faixas recusam
  valores fora dos limites aprovados. Valores ou percentuais de pedidos não
  aceitos também são rejeitados.
- Identidade, qualificação e endereço vêm de arquivo off-chain separado: o
  gerador não tenta reconstruir dados pessoais a partir dos casos anonimizados.
- O documento identifica objeto, obrigações, pagador, beneficiário, forma e data
  de pagamento, quitação específica após cumprimento, assinaturas e somente as
  cláusulas opcionais expressamente configuradas.
- Pesquisa e avaliação do modelo visual registradas em
  `docs/TERMO_ACORDO_FORMAL.md`, com Lei de Mediação, CPC, Código Civil e materiais
  do CNJ como fontes primárias. O exemplo apresentava boa síntese, mas precisava
  qualificação, local/data, pagamento mais preciso e coerência entre a referência
  ao art. 784, III, do CPC e a ausência de duas testemunhas.
- Adicionados exemplo de dados formais e testes de aceite, cálculo, limites,
  campos obrigatórios, valor por extenso, CLI e HTML seguro para impressão.

- `termo_mediador.py` recebe diretamente o JSON de `get_case`, inclusive quando
  a resposta ou o campo `painel` estão codificados como strings JSON.
- Cada opção aprovada origina escolhas de aceitar/não aceitar. O script gera as
  combinações válidas com ao menos uma opção aceita, apresenta primeiro o cenário
  com mais aceitações e exclui tanto a rejeição total quanto combinações que
  somariam opções declaradas não cumulativas.
- Faixas e fórmulas permanecem numéricas; descrições, pendências e decisões são
  apresentadas de forma determinística, curta e com acentuação em português.
- Opções retidas nunca são promovidas pelo pós-processamento: aparecem em todos
  os cenários somente com os riscos registrados pela auditoria.
- A saída pode ser Markdown, JSON estruturado ou HTML autocontido. O HTML usa
  UTF-8, layout responsivo e folha de impressão A4, com um Termo por página, e
  escapa todo conteúdo dinâmico recebido do painel.
- O limite padrão de 256 combinações falha de forma explícita, sem truncamento.
- O retorno real de `get_case` do caso 0005 foi usado como teste de aceitação:
  gerou dois Termos, preservou a faixa de R$ 0,00 a R$ 64.734,88 e manteve RP02
  retida. Após os refinamentos de apresentação, a suíte completa terminou com
  186 testes aprovados.
- Os códigos `RPxx` passam a ser definidos uma única vez, numa seção de
  identificação anterior ao cenário. O restante do documento usa somente o ID,
  sem repetir a descrição longa, e fórmulas exibem “percentual (%) a definir” em
  vez da variável técnica `p`.
- Os títulos passam a usar `Termo de Opção Nr. N`. A identificação de cada pedido
  incorpora a conclusão das lentes e informa quando nenhuma opção é apresentável;
  pedidos retidos não são repetidos como alternativas. A finalidade fica restrita
  a “cenário objetivo para discussão pelo mediador”.

## v20.0.0-experimental — 2026-09-08 — candidata para repetição dos 50 casos

Motivação: a v19 consolidou uma melhora importante — 47/50 consensos, três falhas
técnicas, 24 rotações, 16 painéis inválidos e nenhuma inconsistência nos 47 Termos
— mas entregou opção integral ou parcial em 29/50 casos, abaixo da meta de 35.

- Preserva integralmente a arquitetura da v19, inclusive as três lentes, o Termo
  determinístico, a auditoria cruzada, o reparo único e a retenção correta da
  multa do caso 0027.
- Um pedido monetário com lacuna de nexo, valor ou proporção pode gerar fórmula
  `valor pedido × p` somente quando o valor está literalmente ancorado na PR.
  O Termo mantém a indicação de que a base é pauta de discussão, não dívida.
- Uma faixa cuja proporção não esteja documentada pode ser rebaixada para fórmula
  com percentual aberto, preservando a base válida e removendo o número sem fonte.
- Uma opção monetária incompatível com pedido não monetário pode ser recuperada
  como opção não monetária condicionada, sem inventar prazo, custo ou extensão.
- A auditoria admite `apta_com_ressalva` apenas quando o único risco é
  `DUPLA_CONTAGEM`, há outro pedido identificado e a redação já proíbe soma. O
  Termo apresenta os IDs conflitantes como alternativas não cumulativas.
- Qualquer risco adicional — inclusive escopo, suporte, valor, polo ou premissa —
  continua exigindo reformulação. A flexibilização não alcança o defeito material
  corrigido no caso 0027.
- Relatório consolidado da v19: `V19_BATCH1_REPORT.md`. Hipótese, amostra e gates
  da nova execução: `V20_BATCH1_PLAN.md` e `canary_v20.json`.
- 172 testes locais aprovados. SHA-256 do candidato:
  `d2b719467cf96874244a4e5990c501c0b93ef5d900dc0bc93480e71e43cbadf4`.
- Upgrade `FINALIZED/SUCCESS` e versão/hash remoto verificados, sem executar caso
  durante a instalação: `0x95da380703534119ef4a2bec45f7d3b2132ec50884d6216328a875d933a104b3`.
- O lote comparativo v20 foi inicializado com exatamente os casos 0001–0050 em
  `res_canary_v20/`; runner serial persistente ativo, intervalo mínimo de 15
  segundos e parada obrigatória após 50 resultados.

## v19.0.0-experimental — 2026-09-07 — candidata para repetição dos 50 casos

Motivação: a v18 obteve 38/50 consensos e 31/50 Termos úteis quando os casos
mistos são contados corretamente, mas ainda descartou painéis por falhas locais
da opção e aprovou, no caso 0027, uma multa possivelmente sobreposta.

- A lente jurisprudencial escolhe os campos decisórios da opção, enquanto o
  contrato deriva pagador/beneficiário, ancora os trechos literais já escolhidos
  e redige proposta, premissa e ressalva com modelos determinísticos. O modelo
  devolve `AUTO` nesses campos mecânicos, reduzindo volume e variabilidade.
- Erro restrito à opção deixa de invalidar todas as conclusões do painel. O
  contrato substitui somente a opção por `opcao_nao_validada`, mantém as três
  análises e força retenção explícita no Termo.
- A auditoria passa a examinar todas as opções em conjunto e retorna
  `conflitos_com` com IDs de pedidos. `DUPLA_CONTAGEM` só é válido com outro ID
  identificado, cobrindo multas, encargos, bases, fatos e pedidos alternativos.
- A auditora deixa de produzir uma terceira conclusão repetida: sua saída contém
  somente `pedido_id` e o teste refutador da opção. As conclusões independentes
  permanecem nas lentes probatória e jurisprudencial.
- Uma opção marcada para reformulação pode passar por exatamente um reparo
  dirigido e uma reauditoria. O reparo não pode mudar decisão/lacuna nem criar
  fonte, valor ou percentual; erro nessa etapa preserva a retenção original.
- O runner adota cinco classes: `APTO_INTEGRAL`,
  `APTO_PARCIAL_COM_RETENCOES`, `SOMENTE_DILIGENCIAS`,
  `SEM_OPCAO_APROVADA` e `FALHA_TECNICA`. Assim, uma retenção local não apaga
  as opções aprovadas do mesmo Termo.
- Gabaritos permanecem fora do IC e dos prompts. Utilidade operacional e
  aderência ao benchmark são dimensões independentes no relatório local.
- 167 testes locais aprovados antes do upgrade. SHA-256 do candidato:
  `e83d3c1f902078805020c098bd0a1b54c11d0aceb31b1a83de001f3cc5a8cd61`.
  Plano, gates e comparação com a v18: `V19_BATCH1_PLAN.md`; relatório-base:
  `V18_BATCH1_REPORT.md`.

## Lote comparativo v18 — 2026-09-07 — encerrado em 50; não avançar

- A campanha 0001–0050 terminou e foi encerrada de forma persistente. Nenhum
  próximo bloco foi iniciado.
- Na mesma amostra, a v18 elevou `MAJORITY_AGREE` de 5/50 para 38/50 e reduziu
  rotações de 142 para 59. O tempo mediano caiu de 611s para 263s.
- Resultado operacional v18: 3 `SATISFATORIO_AUTOMATICO`, 20
  `REVISAR_UTILIDADE`, 15 `INSATISFATORIO_CONTEUDO` e 12
  `INSATISFATORIO_TECNICO`.
- Gates: consenso falhou (76% < 80%); integridade passou (0 inconsistências em
  38 Termos); utilidade estrita falhou (23/50 < 26); dominância estrutural passou
  por margem estreita (`LIDER_SEM_RETORNO` em 24/50); revisão manual falhou.
- A triagem de utilidade é excessivamente severa: 8 dos 15 Termos com retenção
  também continham opções aprovadas, exatamente o formato parcial pedido para o
  mediador. A próxima versão deve separar retenção parcial de inutilidade total.
- A amostra manual dos três supostos satisfatórios encontrou defeito material no
  0027: a auditoria aprovou multa que o gabarito rejeita por sobreposição. Os
  casos 0030 e 0041 foram úteis, mas mais cautelosos que o desfecho esperado.
- Persistem 57 `LLM_INVALID_PANEL`, sobretudo na lente jurisprudencial (38), e
  líder sem retorno em 24 casos. A recomendação é criar v19 com saída de opção
  menor, auditoria cruzada entre pedidos e uma reformulação dirigida no máximo.
- Relatório completo e proposta: `V18_BATCH1_REPORT.md`.

## v18.0.0-experimental — 2026-09-07 — candidata para lote comparativo de 50 casos

Motivacao: a campanha multicase da v17 mostrou apenas 5 `MAJORITY_AGREE` nos
primeiros 50 casos. Os diagnósticos foram dominados por ausência de retorno do
líder, divergência/recontagem do catálogo e schemas longos inválidos, especialmente
nas lentes jurisprudencial e probatória.

- O líder mantém catálogo, lentes probatória, jurisprudencial e auditora e o Termo
  determinístico. O validador deixa de regenerar esse painel completo e devolve
  uma revisão compacta da mesma proposta, com quatro booleanos por pedido:
  fidelidade, conclusões defensáveis, fontes compatíveis e opção segura.
- O novo voto aceita redações e leituras alternativas defensáveis, mas continua
  recusando omissão de pedido, fonte incompatível, conclusão indefensável ou
  tratamento inseguro da opção. O objetivo é retirar variabilidade acidental,
  não pressionar o validador a concordar.
- Limites dos textos caem para 500/600 caracteres; respostas inválidas ganham uma
  terceira tentativa com instrução explícita de concisão.
- Campos mecânicos de pagador/beneficiário são derivados do catálogo. Uma citação
  inválida de base ou proporção pode ser substituída somente por trecho literal
  da mesma fonte que já contenha exatamente o valor/proporção escolhido pelo
  modelo; valor, fonte e mérito não são corrigidos pelo código.
- O Termo passa a distinguir conclusão que passou, conclusão que não passou,
  opção retida e ausência coerente de opção. Sufixos inventados como `DR1` são
  apresentados como o ID real `DR`.
- O runner aceita seleção explícita sem reposição por `--case-ids-file`, registra
  encerramento irreversível de campanha e instala uma versão em modo
  `--upgrade-only`, persistido inclusive após retomada.
- Após a criação do marco, a estratégia de avaliação foi ampliada antes do
  primeiro envio: `canary_v18.json` fixa os mesmos casos 0001–0050 do baseline
  v17. Gates e regra de parada a cada 50 estão em `V18_CANARY.md`.
- 163 testes locais aprovados. Snapshot SHA-256:
  `945c8e33eafec4c37731070d1285321455f44dbc6184e7329be5c6a372e73175`.
- Upgrade `FINALIZED/SUCCESS`, com versão e hash remoto verificados e sem análise
  adicional: `0x3ae67ce12e7efbf2ddfae7416aab2180a7f0079d8a8e97c17a5e5fd9b364db81`.
- Primeiro lote v18 inicializado com exatamente os casos 0001–0050. Caso 0001
  enviado em `0x00a55358090b2a0257302cb6de28723c3ceaedf788adf92a581d03e1f3f43207`;
  runner serial ativo com intervalo mínimo de 15 segundos e parada após 50.

## Fase 2A — 2026-09-07 — baseline v17 encerrado antecipadamente

- A decisão de parada usou os primeiros 50 resultados: 45
  `MAJORITY_DISAGREE`, 5 `MAJORITY_AGREE`, nenhum `SATISFATORIO_AUTOMATICO`,
  4 `REVISAR_UTILIDADE` e 1 `INSATISFATORIO_CONTEUDO`.
- Houve 105 `LLM_INVALID_PANEL`: 68 na lente jurisprudencial, 33 na probatória
  e 4 na auditora. Diagnósticos agregados incluíram `LIDER_SEM_RETORNO` 326,
  `REVISOR_CATALOGO` 166 e `CATALOGO_QUANTIDADE` 123 ocorrências.
- O caso 0051 já estava transmitido no momento da parada e foi somente acompanhado
  até o término: também terminou `UNDETERMINED/ERROR`, elevando o fechamento para
  46 falhas técnicas em 51 processados. Nenhum caso a partir do 0052 foi enviado.
- O manifesto foi encerrado de forma persistente após o caso 0051; 449 itens
  permaneceram na fila histórica e o runner recusa retomada dessa campanha.
- O relatório de causa, exemplos e hipótese seguinte está em `PHASE2A_REPORT.md`.
- A campanha avança em blocos de 50 e sempre para para reavaliação.

## Fase 2 multicase — 2026-09-06 — preparada

- Nova campanha congelada na `v17.0.0-experimental`, sem upgrades entre casos:
  exatamente 500 chamadas seriais de `analyze_case`, IDs 0001 a 0500, no contrato
  `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`.
- Intervalo mínimo persistido de 15 segundos depois de observar cada término.
  Timeout ou envio incerto pausam a campanha; a retomada consulta o hash existente
  e não repete a transação.
- `studio_phase2.py` confere versão/SHA remoto e snapshot imutável, salva recibo
  sanitizado, estado e Termo por caso e mantém `events.jsonl`, `cases.jsonl`,
  `impressions.jsonl`, `summary.json` e `report.md` locais em `res_phase2_v17/`.
- Os gabaritos não entram no IC. A triagem automática distingue satisfação estrita,
  revisão de utilidade, problema de conteúdo e falha técnica. Fórmula com envelope
  apenas 0%–100% não infla o total satisfatório: fica para revisão.
- O relatório é cumulativo e contém impressão por caso. O balanço deve ser publicado
  a cada 50 casos ou imediatamente diante de resultado relevante.
- Cinco novos testes cobrem classificação, consenso, relatório, formato do ID e a
  garantia de não persistir mensagem sensível em envio incerto. Suíte completa:
  155 testes.
- Primeiras execuções revelaram que `FINALIZED` e o `SUCCESS` do recibo do líder
  podem coexistir com `MAJORITY_DISAGREE`; nesse caso o estado é revertido. A
  campanha passou a exigir os três sinais juntos antes de ler o Termo, evitando
  atribuir ao caso atual o estado preservado de uma análise anterior.

## Politica de marcos — 2026-09-06

- A pedido do usuario, novos resultados relevantes orientam marcos **major**:
  v11.0.0, v12.0.0 etc. Uma major experimental nao significa aprovada.
- Codigo candidato em `ic_experimental.py`; `ic_v10_2.py` fica preservado em
  v10.2.4. Tags Git `ic-vM.x.y` identificam snapshots recuperaveis. Nao mover tags
  nem reescrever commits para substituir resultados ruins.
- Cada marco registra motivacao, alteracoes, testes locais, versao/hash instalado,
  transacoes, tempo observado, consenso, qualidade do Termo e proximo passo.
- Comparacao: cobertura dos pedidos, formulas/faixas sustentadas, distincao entre
  divida e negociacao, pertinencia da auditoria, consenso e tempo. Aumentar Agree
  sozinho nao e criterio de melhora. Campos desconhecidos nao viram zero.
- Comunicacao no chat: cada resultado relevante e balanco a cada 50 envios.
- Campanha: ate 1.000 envios totais, 6 horas, intervalo minimo de 15s apos cada
  execucao; consultas seriadas. Os limites nao reiniciam com major ou rollback.
- Rollback restaura **codigo**, nao desfaz transacoes, estado ou documentos ja
  gerados. Exige snapshot registrado, SHA-256, autorizacao de upgrade e nenhum
  envio pendente. Depois e preciso nova analise para um novo Termo daquela versao.

### Ambiente da campanha

- Studio: chain ID 61999, SDK Python 0.18.0.
- Instancia: `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`.
- Conta SDK local: `0x6d96d47e3370A838F4414F63Ba79D1c8b9812bCf`.
- Caso: 0005. Entrada fixada no commit `6bf13ae581afd08415c54d0d825543c21e34bff5`.
- Artefatos locais: `res_cycle_v10_2/cycle.json`, snapshots, recibos sanitizados,
  estados e termos quando disponiveis. Chaves e dados completos nao vao ao Git.
- Paineis de **lideres** podem aparecer nos recibos de EP; paineis dos validadores
  nao sao gravados. Nao atribuir causa individual a voto Disagree sem diagnostico.

### Seguranca operacional — 2026-09-06

- Uma leitura diagnostica `gen_call` contra o Studio devolveu, dentro do objeto
  JSON-RPC de erro, configuracao interna com `node_config.private_key` de um
  validador. O objeto bruto foi acidentalmente exibido no registro da sessao.
- A chave local da conta da campanha nao foi exibida. Nao houve teste, uso ou
  publicacao Git da credencial retornada pelo Studio.
- Recibos locais foram ressanitizados. O runner persiste redacao recursiva e
  reduz erros RPC a `codigo+metodo`, descartando `message` e `data`; excecoes do
  SDK nao imprimem traceback. Teste de regressao cobre explicitamente esse caso.
- A credencial exposta nao e reproduzida neste changelog. Rotacao e correcao da
  serializacao no servidor dependem do time do Studio.

## v17.0.0-experimental — 2026-09-06 — consenso; candidata recomendada

Motivacao: a v16 resolveu a faixa e a leitura `passou/nao passou`, mas ainda
despejava as tres lentes completas no Termo. A revisao encontrou repeticao e
afirmacoes juridicas gerais que nao estavam ancoradas nos quatro resumos do caso.

- O Termo passa a mostrar somente proposta, premissa, ressalva, auditoria, faixa,
  suporte e controversia probatorios e uma pergunta factual com seu impacto.
- As lentes jurisprudencial e auditora integrais continuam no painel JSON para
  auditoria tecnica, mas deixam de ser apresentadas como laudo ao mediador.
- Remove o longo detalhamento de conclusoes repetidas. Acrescenta observacoes de
  uso e indica explicitamente ausencia de faixa para opcao nao monetaria ou
  diligencia. Nao altera painel, prompts, consenso, EPs ou storage.
- 150 testes locais aprovados, incluindo regressao que injeta tese juridica nas
  lentes e confirma que ela nao aparece no Termo.
- Tag `ic-v17.0.0`, commit `a2d0546`. Snapshot SHA-256:
  `4e7b7f94c942dd39da6487515578da9165ba706a90d3dd54ac07534709afa704`.
- Upgrade FINALIZED/SUCCESS em 48,34s:
  `0x83202e196c45a9f3ea2c365d1947f818565f542a15b1ffc55b1cd3017881bd68`.
- Analise 0005 FINALIZED/SUCCESS/MAJORITY_AGREE, sem rotacao, em 303,34s:
  `0xe1d7f88607335dcf1611d0713c1e57a32d58b224659844f8161faa3c4a5d6384`.
- Tres validadores registraram `REVISOR_APROVA`; um pediu reformulacao e um teve
  erro local/transporte. O quorum aprovou na primeira rodada.
- Termo final: RP01 passou para discussao com formula e envelope de R$ 0,00 a
  R$ 64.734,88; RP02 passou como diligencia tecnica. O documento separa ambos
  das conclusoes definitivas ainda abertas e usa somente a sintese probatoria
  como pauta factual. Painel completo continua armazenado.
- Revisao de utilidade: candidato adequado para teste pelo mediador. Manter v16
  e v15 como retornos recuperaveis; encerrar o loop porque novas revisoes sem
  defeito concreto tenderiam a adicionar variabilidade, nao evidencia de melhora.
- Acumulado final: 21 envios (1 deploy, 11 upgrades, 9 analises), muito abaixo
  do teto de 1.000. Nenhuma transacao ficou pendente.

## v16.0.0-experimental — 2026-09-06 — consenso; faixa pronta para discussao

Motivacao: a v15 obteve consenso e gerou opcao util, mas o Termo ainda enfatizava
`necessita informacao / valor indeterminado` e escondia a faixa discutivel dentro
da formula. O usuario ja havia apontado que esse resultado isolado era ruim.

- O resumo passa a separar explicitamente `PASSOU PARA DISCUSSAO` de `nao passou
  como conclusao definitiva`, preservando a diferenca entre composicao e divida.
- Para formula com base auditada, calcula envelope matematico de discussao entre
  0% e 100% da base. No caso 0005 isso produz R$ 0,00 a R$ 64.734,88.
- O texto declara que o envelope nao e faixa probatoria nem recomendacao, nao
  escolhe ponto medio e deixa `p` para as partes. Faixa documental continua sendo
  exibida separadamente quando os resumos realmente trouxerem percentuais.
- A faixa de discussao e campo derivado distinto de `faixa_centavos`; conclusao
  sobre valor devido permanece indeterminada. Opcao retida nao recebe envelope.
- Nao altera prompts, criterio de consenso, numero de EPs ou storage. Corrige a
  apresentacao e inclui a faixa no relatorio do runner. 149 testes aprovados.
- Tag `ic-v16.0.0`, commit `c054968`. Snapshot SHA-256:
  `ae59082b996d7224164b0ca8b42d094a9ab782d9f9ab201b3a1541411bf88ad7`.
- Upgrade FINALIZED/SUCCESS em 48,17s:
  `0x269de5abcaf6da23f92583ec37c2288ebaa431708fa2d6741981e6f22808c634`.
- Analise 0005 FINALIZED/SUCCESS/MAJORITY_AGREE em 242,79s, com uma rotacao:
  `0x5c45edaa88600c36acf71d7c888e72526c6c851aff4c3b36c0297282d8dfd834`.
- A primeira rodada foi corretamente recusada por CATALOGO_QUANTIDADE. Na
  segunda, tres revisores aprovaram e dois pediram reformulacao; quorum obtido.
- Termo confirmou RP01 `PASSOU PARA DISCUSSAO`, formula sobre R$ 64.734,88 e
  envelope R$ 0,00 a R$ 64.734,88; RP02 passou como diligencia. Nenhuma das duas
  virou conclusao definitiva de responsabilidade ou valor devido.
- Revisao de utilidade: o resumo resolve a queixa original, mas o detalhamento
  das tres lentes e longo e pode expor teses juridicas gerais nao ancoradas nos
  resumos. Preservar v16 como marco funcional e simplificar o Termo na v17.
- Acumulado: 19 envios (1 deploy, 10 upgrades, 8 analises).

## v15.0.0-experimental — 2026-09-06 — consenso obtido; revisao de utilidade

Motivacao: a v14 compartilhou a opcao do lider, mas ainda chamou o comparador de
equivalencia do painel inteiro. Isso reprovou diferencas semanticas e de lacuna
mesmo quando o revisor considerava a mesma proposta apta para mediacao.

- O voto agora exige painel estruturalmente valido, catalogo compativel, opcao
  exatamente igual a do lider e auditoria independente `apta` para cada pedido.
- Conclusoes, comentarios e lacunas continuam sendo gerados independentemente,
  mas diferencas de redacao ou avaliacao nao reprovam sozinhas uma opcao segura.
- Conclusao local fora de escopo continua incompatibilizando proposta financeira;
  auditoria `reformular`, opcao alterada, fonte falsa ou catalogo divergente
  continuam produzindo Disagree.
- O comparador semantico anterior sai do caminho de consenso, eliminando uma
  chamada LLM por validador quando os requisitos deterministas ja foram atendidos.
- O prompt da auditora explicita os dois formatos JSON aceitos para reduzir as
  falhas de schema vistas nas rotacoes intermediarias da v14.
- Mantem as tres lentes, um EP, Termo deterministico e nenhuma etapa humana
  adicional no blockchain. 149 testes locais aprovados. Tag `ic-v15.0.0`, commit
  `3253aa7`. Snapshot SHA-256:
  `b88a829d278a431db5528496ff81e6c1b3bdbffb3110ea4c551e32f1fbc0bbce`.
- Upgrade FINALIZED/SUCCESS em 48,32s:
  `0x5b1a0da5ba08bfa16c56c4005acd38f962bbdfe214782caa3f06c366187e6905`.
- Analise 0005 FINALIZED/SUCCESS/MAJORITY_AGREE, sem rotacao, em 211,87s:
  `0x094caa7992c4d7a43f6168b85d838e4160e14cb36f85a4a717de984a67dd84dc`.
- Tres validadores registraram `REVISOR_APROVA`; um registrou
  `REVISOR_REFORMULAR`. O quorum aprovou a mesma proposta sem exigir igualdade
  das conclusoes independentes.
- Termo gerado: RP01 com formula condicional `R$ 64.734,88 x p/100` e RP02 com
  diligencia tecnica conjunta. Ambas foram auditadas como aptas pelo painel do
  lider; conclusoes de responsabilidade e valor devido permaneceram abertas.
- Revisao de utilidade: conteudo e fontes sao pertinentes, mas a abertura ainda
  mostra valor indeterminado e nao traduz a formula em faixa clara ao mediador.
  Manter como primeiro marco de consenso e iterar a apresentacao na v16.
- Acumulado: 17 envios (1 deploy, 9 upgrades, 7 analises).

## v14.0.0-experimental — 2026-09-06 — sem consenso; proposta compartilhada validada

Motivacao: a v13 ainda comparou propostas alternativas geradas separadamente;
validadores divergiram sobretudo em auditoria, fontes, lacunas e estado da opcao.
O usuario autorizou testar, em major separada, uma unica proposta do lider sendo
revisada por conclusoes independentes dos validadores.

- O lider continua gerando catalogo e as tres lentes. Cada validador ainda forma
  catalogo, leitura probatoria, conclusao jurisprudencial e auditoria proprios.
- A opcao jurisprudencial do lider e inserida pelo codigo no painel revisor. O
  modelo nao pode gerar, copiar ou substituir a proposta recebida.
- A conclusao do revisor pode contrariar a proposta. Incompatibilidade vira voto
  contrario fora do retry de formato, evitando pressionar o modelo a concordar.
- Catalogo divergente interrompe cedo. Citacoes do lider continuam verificadas
  contra os quatro blocos resumidos; a auditora local pode exigir reformulacao.
- Mantem tres lentes, um unico EP, cinco campos de storage e Termo deterministico,
  sem confirmacao humana adicional no blockchain.
- Risco deliberado: todos veem a proposta do lider, o que pode produzir ancoragem.
  A independencia de conclusoes, fontes e auditoria e a mitigacao testada.
- 148 testes locais aprovados, incluindo copia exata da proposta, rejeicao de
  opcao devolvida pelo modelo, catalogo divergente, conclusao contraria, auditoria
  contraria e nao propagacao de dados secretos de erros RPC.
- Commits: `aeaeaba` (arquitetura) e `fada976` (documentacao/hardening). Tag
  `ic-v14.0.0` publicada. Snapshot SHA-256:
  `5a8a7ece21ce51c86a400a2dfbf55d8642a20e9493ef9454fa6744be00c998d7`.
- Upgrade FINALIZED/SUCCESS em 52,23s:
  `0xef8d9b9475241c31d2ca0319e4c7e3d35b8c3cd3cd5e0c40481c9cbaa5b8fa69`.
- Analise 0005:
  `0x5c663b92b1e4d872a2ff1740c26a4fe8ae0458a2246d14e844d039ae2110de89`.
- UNDETERMINED apos 3 rotacoes; 411,91s. Nenhum Termo aprovado. A primeira
  rodada registrou um `REVISOR_APROVA`/Agree, mas os demais votos apontaram
  SEMANTICA, lacuna probatoria e erro local/transporte.
- Duas rotacoes tiveram lider sem retorno por `auditoria:SCHEMA_INVALIDO`. Na
  ultima, dois revisores divergiram semanticamente e o comparador de outro falhou.
- Os dois paineis de lider observados classificaram corretamente os pedidos e
  propuseram formula `R$ 64.734,88 x p/100` para RP01 e diligencia para RP02,
  ambas auditadas como aptas. O resultado sugere remover a equivalencia integral,
  nao afrouxar checagem de fonte ou auditoria.
- Acumulado: 15 envios (1 deploy, 8 upgrades, 6 analises).

## v13.0.0-experimental — 2026-09-06 — sem consenso

Motivacao: na primeira rodada da v12, o lider chamou ressarcimento de reparos
materiais de danos_morais; os validadores corretamente recusaram CATALOGO_NATUREZA.

- Explicita principal como cobranca/restituicao/ressarcimento material e reserva
  danos_morais a compensacao extrapatrimonial expressamente pedida.
- Define correspondencia obrigatoria entre fazer/nao_fazer/declarar e suas
  naturezas. Validacao estrutural recusa combinacoes incoerentes; pagar so admite
  categorias monetarias. Isso nao prova o merito da classificacao moral/material,
  que continua dependente do conteudo e do consenso.
- Manteve comparador e geracao independente de propostas. A alternativa de
  validadores revisarem a mesma proposta do lider nao foi implementada aqui.
- 142 testes locais aprovados. Tag `ic-v13.0.0`, commit `11e00dc`.
- Snapshot SHA-256:
  `bc5835f5bc33b3441849a7630e34d0aee55476ba5f7ee787ab7b305262c2ea57`.
- Upgrade FINALIZED/SUCCESS:
  `0x104ee52a48642b44848b1a122b2c18696b763d05667aa0665a078a3a9874576d`.
- Analise 0005:
  `0x919d95ea9fcd15cc149e49ca5e9482f4b0bcbd11c6b9aade8fa2e307f9f21a27`.
- UNDETERMINED apos 3 rotacoes; 1.008,70s ate observar o desfecho. Nenhum
  Termo aprovado. Diagnosticos apontaram divergencias em auditoria, lacuna
  probatoria, fontes, status da conclusao, riscos e erro do comparador.
- Acumulado: 13 envios (1 deploy, 7 upgrades, 5 analises).

## v12.0.0-experimental — 2026-09-06 — sem consenso; campos divergentes identificados

Motivacao: a v11 confirmou que o Studio preserva os codigos fixos de stdout,
mas os grupos CATALOGO/OPCOES ainda nao identificavam o campo divergente.

- Detalha diagnosticos de catalogo (quantidade, IDs, polos, modalidade, natureza,
  null/valor), conclusao (status, tendencia, flags, polos, faixas) e opcoes
  (auditoria, riscos, tipo, fontes, base, criterio e dimensao de lacuna por lente).
- Nenhuma nova permissao de aprovar: os mesmos testes de equivalencia continuam
  rejeitando as mesmas diferencas. Nao registra valores nem textos dos paineis.
- Runner agora extrai diagnosticos apenas das listas de recibos por rodada,
  evitando duplicatas que aparecem em monitoring/consensus_data. A primeira
  contagem exibida no chat usava a coleta recursiva e nao deve ser usada como
  numero de validadores distintos no relatorio; os tipos de erro eram reais.
- 141 testes locais aprovados, incluindo deteccao do campo e espelhos de recibos.
- Tag publicada: `ic-v12.0.0`, commit `1d650d6`.
- Snapshot SHA-256: `acc21a1c2c8104eff129ed67563d98bf17e0b2d6c0fdaea0891686fd99a45bb1`.
- Upgrade FINALIZED/SUCCESS:
  `0x1879ec607c28c3f78727602686296046318db70427a59a0fd1f0a2ffb739a2e8`.
- Analise 0005: `0x40d84230b072db2e49285acc2144ac524299dc267268e8b3ed600e8513a840c4`.
- UNDETERMINED apos 3 rotacoes; 494,61s ate observar o desfecho. Sem Termo aprovado.
- Diagnosticos confirmaram CATALOGO_NATUREZA, OPCOES_RISCOS,
  OPCOES_ESTADO_AUDITORIA e OPCOES_FONTES. A primeira rejeicao protegeu contra
  erro real do lider (reparo material rotulado como moral), nao mero formato.
- Outros campos de auditoria/fontes divergiram em rodadas posteriores; os
  codigos nao mostram o conteudo integral das propostas locais dos validadores.
- Acumulado: 11 envios (1 deploy, 6 upgrades, 4 analises).

## v11.0.0-experimental — 2026-09-06 — sem consenso; diagnosticos confirmados

Primeiro marco major apos a mudanca da politica de versionamento. Incorpora o
trabalho que estava sendo preparado como v10.2.5, que nao foi publicado nem
executado com esse numero.

### Motivacao

A v10.2.4 voltou a terminar UNDETERMINED. Houve erro explicito
`CRITERIO_INVALIDO` em dois pedidos/tentativas da lente jurisprudencial.
A causa individual das demais discordancias permanece desconhecida.

### Alteracoes

- Prompts mostram objetos `criterio` completos para formula e sem calculo,
  incluindo todos os campos null. Nao preenche ausencias nem flexibiliza valores.
- Diagnostico estrutural de criterio/base identifica campos ausentes, quantidade
  de extras e tipo recebido, sem copiar chaves desconhecidas ou dados do caso.
- Teste de mensagens `MEDIARE_DIAG` com codigos fixos em stdout para localizar
  fase da rejeicao: schema, catalogo, conclusao, opcoes, semantica ou erro de
  execucao. Sem paineis, textos livres ou novo EP. Retencao pelo Studio ainda
  precisa ser verificada no teste real; nao e garantia do protocolo.
- Runner aceita majors >=10 e permite rollback com verificacao remota de
  versao/hash. Retomada consulta o mesmo envio, nunca o duplica.
- Preserva o comparador, as tres lentes, as condicoes financeiras e o layout
  dos cinco campos de storage. Nao altera gabaritos nem dados dos casos.

### Validacao

140 testes locais aprovados: baseline v10.1, v10.2.4 preservada, candidata major,
controle do ciclo, credenciais, limites, retomada e rollback simulado.
Isso nao demonstra consenso, qualidade juridica nem rollback real no Studio.
Tag publicada: `ic-v11.0.0`, commit `ad1d69d`.
Snapshot SHA-256: `e57713bb33f75dc578ea7e8719b9966e22d9a06f01f47adeb221d604ecaebb8e`.

### Resultado real

- Upgrade FINALIZED/SUCCESS e identidade remota conferida:
  `0x1ed759aa6095999d411847cc6e94d57a81d79abeb0da86f314a95e150d68c8e4`.
- Analise 0005: `0xdf5e46ae75759a2394341ce4b614bf86e3b5421a103b4a4964f90565a3e0d4af`.
- UNDETERMINED apos 3 rotacoes; 457,67s ate observar o desfecho.
  Lideres com SUCCESS nao atingiram consenso.
- **Resultado relevante:** codigos fixos apareceram em stdout de recibos de
  validadores: OPCOES, CATALOGO, LIDER_SEM_RETORNO e ERRO_PAINEL_LOCAL_OU_TRANSPORTE.
  Nao sao paineis gravados nem
  justificativas juridicas livres. Nao inferir o campo preciso dos dois primeiros.
- Um lider falhou na probatoria: RP02 esperava null e recebeu inteiro;
  na correcao, RR01 falhou em coerencia de decisao/valor/partes/fontes.
- Nenhum Termo aprovado. Manter como marco de observabilidade, nao de qualidade.
- Acumulado ao final: 9 envios, sendo 1 deploy, 5 upgrades e 3 analises.

## v10.2.4-experimental — 2026-09-06 — sem consenso

- Commit: `d4dec24`. Snapshot SHA-256:
  `456e3cc9639197ef684f685bced7fdc2c3eba2d6b885635dcc382e6efe970357`.
- Alteracoes: delimita pedido declaratorio concreto versus dever abstrato;
  distingue alegacao de fato aceito; audita utilidade condicional sem exigir p
  definido; reconhece envelope think completo e classifica erros de JSON.
- Testes locais na entrega: 97 aprovados.
- Upgrade FINALIZED/SUCCESS:
  `0x70ad618097f94c53ae5dafd6f457011cbb09442aef8ae301c0e5cfc765f1116f`.
- Analise: `0x706591aa4e18e0a52084bb122d7bfb80cd835a3f4f00c370c5ee63594fafbb3a`.
- Resultado observado: UNDETERMINED, 3 rotacoes; 522,22s ate detectar o desfecho.
  Execucoes de lideres com SUCCESS nao significaram consenso aprovado.
- Falha registrada: `lente=jurisprudencial`, RP01/RP02 `CRITERIO_INVALIDO`.
- Nao houve novo Termo aprovado. Nao afirmar melhora de merito pelo log.

## v10.2.3-experimental — 2026-09-06 — infraestrutura funcional, sem consenso

- Commit: `ce7dce7`. Snapshot SHA-256:
  `6bb74df34bf2befe0f0a5483404e928f0c9548b4663eb949375fb49676ac0104`.
- Alteracao: leitura unica do codigo no offset 4 de Root.code, compativel com
  SDK fixado; sanitiza credenciais eventualmente retornadas nos recibos.
- Testes locais na entrega: 97 aprovados.
- Upgrade FINALIZED/SUCCESS e hash remoto conferido:
  `0x654cb674f81ee9fe7d7642072393a0dfea61d851bcf8efbb65606fee67056eb5`.
- Analise: `0x05ead024baaffe8ab8f256dc2e0e0bfe7dfa7d99933e7d6f51ebbf05f7216b53`.
- Resultado observado: UNDETERMINED, 3 rotacoes; 289,30s ate detectar o desfecho.
- Lideres gravados variaram entre responsabilidade concreta/abstrata e entre
  aprovar formula aberta/rejeita-la por ausencia de p. Um lider falhou no JSON
  do catalogo. Esses achados nao revelam as causas individuais dos validadores.
- Nenhum Termo aprovado. Marco util para recuperar a primeira infraestrutura
  integralmente funcional, nao como baseline de qualidade aprovada.

## v10.2.2-experimental — 2026-09-06 — nao analisada

- Commit: `8c21a30`; 96 testes locais.
- Upgrade FINALIZED/SUCCESS:
  `0x146bcd7f86ab40f73e26203a25c7cc7415534f350c6b2b329ad8c2c6a1bb262e`.
- Tentou leitura em bloco com `data_offset()`, presente no SDK atual consultado,
  mas ausente na dependencia fixada. Erro real: AttributeError de VLA.
- Nenhuma chamada analyze_case; rodada encerrada explicitamente com motivo.

## v10.2.1-experimental — 2026-09-06 — nao analisada

- Commit: `5a5985a`; 94 testes locais e schemas compilados no Studio.
- Introduz ciclo SDK, journal, limites, snapshots/hash, bootstrap atualizavel,
  verificacao FINALIZED/SUCCESS e prompts separados por lente.
- Upgrade FINALIZED/SUCCESS:
  `0x298d7a601529e52c6615daf7d8b276fba809b4a5744f66079c468b9ef33774de`.
- `bytes(VLA)` percorria o codigo byte a byte; getter excedeu 30s duas vezes.
  Nenhuma chamada analyze_case. Mocks locais nao mediam latencia de storage.

## Bootstrap — 2026-09-06 — concluido

- `studio_runner.py` encontrado: acesso via SDK ja existia para lotes v9,
  mas sem upgrade. Novo supervisor em `studio_cycle.py`.
- Instancia manual anterior nao possuia upgrade; criada instancia de teste
  autorizada pelo usuario com a conta local existente, sem faucet/transferencias.
- Deploy FINALIZED/SUCCESS em 48,06s observados:
  `0x8a72ea80f8f2afc21da4734e22a52159ceff48c794b2582af1675ab1b6614881`.

## Campos a preencher em cada proximo marco

Motivacao; codigo/tag/commit; testes locais; snapshot/hash remoto; caso; hashes de
upgrade e analise; status/execucao/rotacoes; tempo observado; diagnosticos realmente
presentes; Termo aprovado (sim/nao); revisao de utilidade; comparacao com marco
anterior; manter/iterar/rollback; total acumulado de envios e prazo restante.
