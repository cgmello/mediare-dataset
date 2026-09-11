# v23.1 — relatório do gate de catálogo

## Resultado

A v23.1 foi **aprovada no gate semântico de catálogo**:

- correções: 6 de 7 casos corrigidos (mínimo exigido: 6);
- preservações: 6 de 6 casos preservados (mínimo exigido: 5);
- nomenclatura nova: pedidos do requerente usam `RP`; contrapedidos materiais e
  autônomos do requerido usam `CR`;
- nenhum painel novo aceitou IDs de contrapedido no formato histórico `RR`.

Esse resultado avalia fidelidade e granularidade do catálogo. Não equivale a
aprovação jurídica do mérito nem exige que o painel completo ou o consenso
local tenha terminado em `Agree`.

## Casos de correção

| Caso | Resultado v23.1 | Veredito |
|---|---|---|
| 0008 | 2 RP; multa e encargos permaneceram acessórios da cobrança | corrigido |
| 0017 | 4 RP + 2 CR; cinco componentes materiais consolidados em um CR | corrigido |
| 0023 | 1 RP; perícia contábil não virou CR | corrigido |
| 0026 | 4 RP; inexigibilidade/exclusão defensiva não virou CR | corrigido; painel posterior falhou por variação técnica do DeepSeek |
| 0029 | 1 RP + 2 CR; o líder voltou a calcular R$ 23.400,00 | não corrigido nesta repetição; GLM detectou `VALOR_INFERIDO` corretamente |
| 0033 | 1 RP; inexigibilidade e competência não viraram CR | corrigido; painel posterior falhou na lente auditora |
| 0035 | 1 RP; reconhecimento e pagamento da mesma dívida foram unidos | corrigido |

## Casos de preservação

| Caso | Resultado v23.1 | Veredito |
|---|---|---|
| 0001 | 5 RP + 3 CR, incluindo retenção da caução expressamente contraposta | preservado |
| 0015 | 6 RP; valores já pagos são abatimento defensivo, não crédito autônomo | preservado; somente o catálogo completou antes de chamada lenta interrompida |
| 0018 | 1 RP; improcedência e recálculo defensivo não viraram CR | preservado |
| 0020 | 1 RP; principal e acessórios da mesma cobrança permaneceram unidos | preservado |
| 0024 | 3 RP; recálculo da multa e devolução do saldo permaneceram separados | preservado |
| 0031 | 1 RP de R$ 2.490,00 | preservado |

## O que as justificativas dos revisores revelaram

O schema estruturado cumpriu sua função: tornou possível distinguir defeito
material de objeção contraditória.

- O Mistral continuou tentando fragmentar componentes internos no 0017.
- No 0008, usou `OMISSAO` para exigir um valor que a fonte não permite calcular.
- Em 0023, propôs simultaneamente “incluir ou consolidar”, sem indicar uma
  correção material determinada.
- Em 0001, tentou remover contrapedidos expressamente formulados como
  reconvenção.
- GPT e Mistral, em rodadas anteriores, chamaram valores de inferidos enquanto
  sua própria evidência reproduzia literalmente o mesmo valor.

A v23.1 normaliza somente o caso objetivamente impossível de
`VALOR_INFERIDO`: campo nulo ou valor idêntico presente na evidência do próprio
revisor. Outros dissensos continuam visíveis e fail-closed.

## Estabilidade técnica observada

O catálogo melhorou, mas a estabilidade do painel completo ainda precisa de
trabalho separado. Na repetição principal da v23.1 houve 12 casos concluídos e
um catálogo adicional do caso 0015:

- 10/12 painéis completos válidos;
- 8/12 maiorias locais;
- falhas posteriores ao catálogo em 0026 e 0033;
- latência excessiva do DeepSeek interrompida depois de o catálogo 0015 ser
  persistido.

Essas falhas pertencem às lentes/retries, não ao gate semântico de catálogo.

## Contabilidade completa da v23

Todas as versões canário, gates, rechecagens, respostas incompletas e chamadas
interrompidas foram somadas a partir dos recibos locais:

| Atividade v23 | Chamadas | Tokens | Custo |
|---|---:|---:|---:|
| v23.0.0 canário | 11 | 63.604 | US$ 0,2037 |
| v23.0.1 canário | 12 | 77.118 | US$ 0,2112 |
| v23.0.2 gate de 13 casos | 106 | 753.237 | US$ 1,7716 |
| v23.1 rechecagem dirigida | 22 | 192.708 | US$ 0,4771 |
| v23.1 gate principal e chamada parcial | 65 | 515.740 | US$ 1,2017 |
| v23.1 preservações restantes | 38 | 236.675 | US$ 0,5769 |
| **Total v23** | **254** | **1.839.082** | **US$ 4,4422** |

## Próximo gate recomendado

Antes do Studio, executar os 20 sentinelas completos com a v23.1. O avanço deve
exigir:

- manutenção dos 6/7 casos corrigidos e 6/6 preservados;
- nenhum `RR01...` em painel novo;
- melhoria ou estabilidade frente aos 18/20 painéis válidos da v22;
- investigação separada das falhas de lente do DeepSeek e da auditora;
- inspeção manual de toda nova divergência de catálogo fundamentada.
