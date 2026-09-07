# Changelog experimental — Mediare IC / Studio

Registro para o relatorio de evolucao. Datas em America/Sao_Paulo, salvo indicacao.
Resultados negativos e versoes nao analisadas permanecem no historico.
**A v17 obteve consenso e foi recomendada para teste com mediador; nenhum Termo
gerado constitui acordo, condenacao ou validacao juridica de merito.**

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

## Fase 2A — 2026-09-07 — baseline v17 encerrado antecipadamente

- A decisão de parada usou os primeiros 50 resultados: 45
  `MAJORITY_DISAGREE`, 5 `MAJORITY_AGREE`, nenhum `SATISFATORIO_AUTOMATICO`,
  4 `REVISAR_UTILIDADE` e 1 `INSATISFATORIO_CONTEUDO`.
- Houve 105 `LLM_INVALID_PANEL`: 68 na lente jurisprudencial, 33 na probatória
  e 4 na auditora. Diagnósticos agregados incluíram `LIDER_SEM_RETORNO` 326,
  `REVISOR_CATALOGO` 166 e `CATALOGO_QUANTIDADE` 123 ocorrências.
- O caso 0051 já estava transmitido no momento da parada e foi somente acompanhado
  até o término. Nenhum caso a partir do 0052 foi enviado.
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
