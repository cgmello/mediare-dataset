# Changelog experimental — Mediare IC / Studio

Registro para o relatorio de evolucao. Datas em America/Sao_Paulo, salvo indicacao.
Resultados negativos e versoes nao analisadas permanecem no historico.
**Nenhuma versao desta campanha recebeu ainda validacao completa de consenso e utilidade.**

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

## v15.0.0-experimental — 2026-09-06 — voto sobre aptidao da proposta

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
  adicional no blockchain. 149 testes locais aprovados; teste real pendente.

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
