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

## v11.0.0-experimental — 2026-09-06 — candidata, ainda nao avaliada no Studio

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
Tag planejada: `ic-v11.0.0` no commit do marco. Resultado on-chain pendente.

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
