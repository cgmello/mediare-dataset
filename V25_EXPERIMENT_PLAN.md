# Plano experimental v25

## Objetivo

Corrigir o excesso de contrapedidos defensivos observado em `0023` e reduzir a
instabilidade de revisão em `0048`, sem alterar as regras RP/CR que funcionaram
na v24.

## Mudanças controladas

- `CR` exige providência afirmativa, autônoma e ancorada em `RR`.
- Exclusão, redução, recálculo, índice, perícia, negativa de fato e declaração
  cujo único efeito é afastar o `RP` permanecem como defesa, não como `CR`.
- Parcelamento subsidiário é uma condição de cumprimento do `RP` monetário;
  somente uma pretensão autônoma permanece como item separado.
- A normalização de revisores continua exigindo tipo de falha, ID, fonte,
  evidência e correção; respostas malformadas permanecem erros técnicos
  observáveis, sem contaminar a conclusão semântica.

## Gate

1. Testes determinísticos locais: catálogo defensivo, restituição afirmativa,
   parcelamento dependente e compatibilidade do runner.
2. Repetir `0023` e `0048` com o mesmo manifesto e rotação v24.
3. Repetir os 20 sentinelas da v24.

A v25 só avança ao Studio se `0023` não criar `CR` defensivo, `0048` formar
maioria Agree, os 20 painéis forem estruturalmente válidos e nenhum controle
anterior regredir. Os testes OpenRouter devem ser registrados no relatório de
custos consolidado; nenhuma chamada é feita como parte deste commit.
