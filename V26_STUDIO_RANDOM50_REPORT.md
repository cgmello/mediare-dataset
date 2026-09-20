# v26 — validação Studio em 50 casos

## Resultado

A v26 concluiu os 50 casos com consenso e execução válida:

| Métrica | Resultado |
|---|---:|
| Casos concluídos | 50/50 |
| `MAJORITY_AGREE` | 50/50 |
| `execution_result=SUCCESS` | 50/50 |
| `UNDETERMINED` | 0 |
| Erros do contrato ou do runner | 0 |
| Encerrados na primeira rodada | 46/50 |
| Rotações de líder | 4 |
| Duração média | 72,3 s/caso |
| Duração total das transações | 3.613,7 s |

Os quatro casos que precisaram de uma rotação foram `0240`, `0375`, `0197` e
`0434`. Todos terminaram com `MAJORITY_AGREE`. O caso `0124`, único sem consenso
no lote aleatório da v25, foi aceito na primeira rodada em 139 segundos.

## Amostra

O manifesto [`studio_v26_random50_seed20260918.json`](studio_v26_random50_seed20260918.json)
fixa o caso `0124` na primeira posição e sorteia outros 49 casos entre
`0001–0500`, com semente `20260918`. Os 49 holdouts excluem a amostra aleatória
anterior da v25.

## Identidade do código

- Versão: `26.0.0-experimental`
- SHA-256: `72870db2c28e49cb38d90ff6bb71ee4b416d2c4e8b2871e6275aa103bd833602`
- Contrato: `0x9311E810d85aB09F8f2E3cDE040fF93c73e31cB9`
- Upgrade: `FINALIZED / SUCCESS`

## Sobre o antigo `erro_decode`

O campo `erro_decode: Expecting value: line 1 column 1` era um falso positivo
do monitor, não uma falha das execuções. O parser histórico esperava que o EP0
contivesse texto JSON, como nas versões antigas. A v26 retorna um objeto nativo
serializado pelo GenVM, que não começa com `{` e portanto não pode ser enviado a
`json.loads`.

O runner agora distingue os dois formatos. Para a v26 registra
`painel_ep0_formato: objeto_genvm`; erros reais continuam sendo identificados por
`execution_result=ERROR`, status terminal inválido ou falha do script.

## Limite da conclusão

O resultado demonstra excelente estabilidade de consenso e execução nessa
amostra. Ele não substitui revisão qualitativa dos 50 Termos: a etapa seguinte
deve inspecionar cobertura dos pedidos, utilidade das opções e correção das
faixas, separadamente do sucesso do protocolo.
