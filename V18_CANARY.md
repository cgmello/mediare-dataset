# Plano do lote comparativo — v18.0.0-experimental

## Hipótese

A v17 falhou principalmente por variabilidade de geração: catálogo divergente,
saída JSON inválida/truncada e regeneração completa do painel por cada validador.
A v18 mantém as três lentes no líder, mas transforma o trabalho do validador em
uma revisão compacta e estruturada da mesma proposta. O objetivo não é fabricar
`Agree`; é reduzir divergência acidental sem deixar passar pedido, fonte, conclusão
ou opção materialmente indefensável.

## Seleção congelada

O arquivo `canary_v18.json` contém os casos 0001–0050, escolhidos antes do
primeiro envio. É a mesma janela que fundamentou a parada da v17, permitindo uma
comparação direta sem escolher casos favoráveis à v18. A ordem também é fixa.
Gabaritos continuam fora dos prompts e são usados somente em revisão posterior.

## Critérios de saída

O lote aprova a abertura do próximo bloco de 50 somente se:

1. ao menos 40 de 50 transações tiverem `MAJORITY_AGREE`;
2. não houver divergência entre os getters de estado e Termo nem painel inválido;
3. pelo menos 26 dos 50 casos produzirem Termo considerado útil na triagem
   operacional (`SATISFATORIO_AUTOMATICO` ou `REVISAR_UTILIDADE`);
4. nenhum único diagnóstico de falha estrutural dominar mais de metade dos casos;
5. uma amostra manual dos Termos aprovados não revelar inversão de partes, valor
   inventado, fonte inexistente ou conclusão apresentada como acordo.

O gate 3 mede disponibilidade de uma pauta útil, não acerto jurídico. A comparação
semântica com os gabaritos será registrada separadamente antes da decisão final.

## Parada

Falha evidente e sistemática pode interromper o lote antes dos 50 casos. Sem
aprovação dos gates, o runner não inicia o bloco seguinte. A avaliação se repete
a cada 50 casos; nunca há continuação automática para todos os 500.
