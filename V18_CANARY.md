# Plano de canário — v18.0.0-experimental

## Hipótese

A v17 falhou principalmente por variabilidade de geração: catálogo divergente,
saída JSON inválida/truncada e regeneração completa do painel por cada validador.
A v18 mantém as três lentes no líder, mas transforma o trabalho do validador em
uma revisão compacta e estruturada da mesma proposta. O objetivo não é fabricar
`Agree`; é reduzir divergência acidental sem deixar passar pedido, fonte, conclusão
ou opção materialmente indefensável.

## Seleção congelada

O arquivo `canary_v18.json` contém 30 casos escolhidos antes do primeiro envio:
6 ouro, 12 reais e 12 sintéticos. A ordem também é fixa. Gabaritos continuam
fora dos prompts e são usados somente em revisão posterior.

## Critérios de saída

O canário aprova a abertura de uma nova campanha de 500 somente se:

1. ao menos 24 de 30 transações tiverem `MAJORITY_AGREE`;
2. não houver divergência entre os getters de estado e Termo nem painel inválido;
3. pelo menos 16 dos 30 casos produzirem Termo considerado útil na triagem
   operacional (`SATISFATORIO_AUTOMATICO` ou `REVISAR_UTILIDADE`);
4. nenhum único diagnóstico de falha estrutural dominar mais de metade dos casos;
5. uma amostra manual dos Termos aprovados não revelar inversão de partes, valor
   inventado, fonte inexistente ou conclusão apresentada como acordo.

O gate 3 mede disponibilidade de uma pauta útil, não acerto jurídico. A comparação
semântica com os gabaritos será registrada separadamente antes da decisão final.

## Parada

Falha evidente e sistemática pode interromper o canário antes dos 30 casos. Sem
aprovação de todos os gates, o runner não cria nem inicia a campanha de 500.
