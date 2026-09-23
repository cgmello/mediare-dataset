# v28 — relatório experimental

Data: 21–22 de setembro de 2026.

## Objetivo

A v27 terminou a campanha Studio com 97/100 resultados válidos. Os três casos
sem consenso (`0013`, `0019` e `0144`) apontaram a mesma família de problema:
regras de catálogo amplas demais eliminavam encargos materialmente autônomos ou
honorários contratuais negociáveis.

A v28 corrige essa fronteira sem relaxar a exclusão de custas, honorários
judiciais e sucumbenciais. Também exige que uma crítica de omissão feita pelo
revisor esteja literalmente ancorada na fonte citada.

## Gates dirigidos

Os três casos atingiram maioria local ao longo dos gates dirigidos. As rodadas
intermediárias foram mantidas porque representam custo e diagnóstico reais. A
última mudança foi isolada ao tratamento determinístico de honorários
contratuais do `0019`; portanto, o conjunto não deve ser interpretado como uma
única execução congelada de três casos.

| Caso | Problema da v27 | Resultado dirigido da v28 |
|---|---|---|
| `0013` | encargo autônomo removido/consolidado | maioria local e catálogo completo |
| `0019` | honorários contratuais confundidos com verba judicial | maioria local após normalização dirigida |
| `0144` | multa/encargo material tratado como mero acessório | maioria local e catálogo completo |

## Gate de 20 sentinelas

| Métrica | v26 | v28 | Variação |
|---|---:|---:|---:|
| Maiorias locais | 15/20 | 16/20 | +1 |
| Painéis do líder válidos | 20/20 | 20/20 | 0 |
| Saídas úteis do líder | 16/20 | 18/20 | +2 |

Os ganhos de maioria ocorreram em `0009`, `0013` e `0023`. As duas perdas
aparentes foram:

- `0001`: o catálogo material permaneceu equivalente; a divergência veio do
  rigor variável dos revisores sobre retenção defensiva e conclusões.
- `0017`: o líder separou retenção/compensação e pagamento subjacente em itens
  redundantes. É um defeito real de granularidade do líder e fica para a v29,
  pois uma nova regra ampla agora poderia desfazer os ganhos da v28.

## Custo OpenRouter

O desenvolvimento dirigido, incluindo repetições, e o gate de sentinelas
totalizaram 34 unidades concluídas, 346 chamadas, 2.728.911 tokens e
US$ 6,538627530425. O valor foi incorporado ao relatório consolidado
`OPENROUTER_BUDGET_REPORT.html`.

## Promoção ao Studio

- Contrato: `0x9311E810d85aB09F8f2E3cDE040fF93c73e31cB9`
- Versão: `28.0.0-experimental`
- SHA-256: `ce1485d7f01a23abe0ad8e5c69fa66a1b6c4641c3b11f386a7bfaa28a3171268`
- Upgrade: `0x4be3a7c9b3655c46633d896a5c0d3e992f8a2964c7ea307e1df9fec0076bc442`
- Amostra: 100 casos aleatórios inéditos nas campanhas Studio v25–v27
- Seed: `20260922`
- Manifesto: `studio_v28_random100_seed20260922.json`

A campanha de 100 casos foi concluída. Seus resultados são avaliados
separadamente dos consensos simulados localmente na seção seguinte.

## Resultado final e comparação com o gabarito

A campanha terminou com 98/100 `MAJORITY_AGREE` e dois `UNDETERMINED`. A
comparação off-chain com o gabarito separou consenso, cobertura e acerto:

- o IC produziu uma conclusão exata de três classes em 11 dos 97 casos cujo
  gabarito era diretamente mapeável, acertando 9/11 (81,8% quando concluiu);
- a inspeção dos dois erros encontrou um defeito no gabarito do `0482`, que
  concede danos morais e multa não pedidos na petição; excluída somente essa
  referência defeituosa, o resultado auditado é 9/10 (90%);
- no teste binário — alguma tutela versus nenhuma tutela — o IC concluiu 24 dos
  98 casos mapeáveis e acertou 24/24;
- apenas três dos 54 casos com valor de referência confiável tiveram conclusão
  integralmente quantificada; os três intervalos continham o gabarito;
- o erro material remanescente é o `0054`: o gabarito concede danos morais, mas
  o IC rejeitou esse pedido.

O resultado mostra boa precisão condicional, mas baixa cobertura: na maior parte
dos casos o painel consensual registra `sem_maioria` ou necessidade de
informação. Portanto, 98% de consenso do protocolo não equivale a 98% de acerto
jurídico. Relatório reproduzível: `V28_STUDIO_GROUND_TRUTH_REPORT.md`.

Os 100 casos foram sorteados entre os 500 registros já compatíveis com o IC
(`0001`–`0500`). Os registros `0501`–`1000` são decisões pseudonimizadas, mas
ainda não foram convertidos nos quatro blocos de entrada exigidos pelo contrato.
