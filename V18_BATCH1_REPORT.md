# Relatório do lote comparativo v18 — casos 0001–0050

## Recomendação

**Não iniciar os casos 0051–0100 ainda.** A v18 é uma melhora técnica grande
sobre a v17, mas não passou todos os gates definidos antes da execução. O próximo
passo recomendado é uma v19 focada na confiabilidade do líder, na auditoria entre
pedidos e numa classificação de utilidade alinhada ao Termo parcial do mediador.

Esta conclusão não invalida a arquitetura de revisão compacta da v18. Ela elevou
o consenso de 10% para 76% na mesma amostra e reduziu tempo e rotações de forma
material. O resultado justifica evoluir a v18, não voltar à v17.

## Comparação direta

| Métrica nos casos 0001–0050 | v17 | v18 |
|---|---:|---:|
| `MAJORITY_AGREE` | 5 (10%) | 38 (76%) |
| `MAJORITY_DISAGREE` | 45 | 12 |
| Rotações | 142 | 59 |
| Tempo mediano por caso | 611 s | 263 s |
| Tempo médio por caso | 1.075 s | 618 s |
| Satisfatório automático | 0 | 3 |
| Revisar utilidade | 4 | 20 |
| Conteúdo com opção retida | 1 | 15 |
| Falha técnica | 45 | 12 |

Das 45 falhas de consenso da v17, 33 passaram a `MAJORITY_AGREE` na v18; 12
continuaram sem consenso. Todos os cinco casos aprovados pela v17 também foram
aprovados pela v18.

## Gates pré-registrados

| Gate | Resultado | Situação |
|---|---|---|
| Pelo menos 40/50 `MAJORITY_AGREE` | 38/50 | **Falhou** |
| Nenhuma inconsistência estado/painel/Termo | 0 em 38 Termos | **Passou** |
| Pelo menos 26/50 úteis pela triagem estrita | 23/50 | **Falhou** |
| Nenhum erro estrutural em mais de 25 casos | máximo 24/50 | **Passou por margem estreita** |
| Amostra manual sem defeito material | houve defeito em 0027 | **Falhou** |

O gate de utilidade estrito subestima o produto pedido. Oito dos 15 casos marcados
como conteúdo insatisfatório tinham ao menos uma opção aprovada e outra retida,
com comentário explicando o que não passou. Contando esses Termos mistos como
úteis parciais, seriam 31/50. Portanto, a classificação deve mudar antes do próximo
lote, mas essa correção de métrica não altera as falhas de consenso e auditoria.

## Qualidade dos Termos

Foram gravados 38 painéis e Termos. Todos passaram novamente pelas verificações
locais: JSON válido, versão correta, painel completo, igualdade entre estado e
arquivo do Termo e ausência de sufixos inventados como `DR1`.

Os 38 painéis continham 165 pedidos. As opções foram: 56 diligências, 37
`sem_opcao`, 34 fórmulas, 27 não monetárias e 11 faixas documentadas. Em 21 opções
de 15 casos, a auditoria pediu reformulação; os riscos mais frequentes foram
`PREMISSA` (16), `VALOR_INVENTADO` (7) e `ESCOPO` (7).

A leitura manual dos três casos classificados como satisfatórios automáticos
mostrou que esse rótulo certifica apenas integridade operacional:

- 0027 produziu uma pauta clara, mas aprovou multa contratual de R$ 2.100,00;
  o gabarito a rejeita por sobreposição com encargos do mesmo inadimplemento.
  A auditoria afirmou o contrário e não sinalizou possível dupla contagem.
- 0030 foi útil e ancorou R$ 400,00, mas deixou a multa de R$ 200,00 em diligência,
  enquanto o gabarito a considera devida.
- 0041 ofereceu substituição não monetária útil, porém manteve responsabilidade
  como indeterminada; o gabarito reconhece responsabilidade do requerido.

Os dois últimos podem ser cautelas aceitáveis numa mediação, mas demonstram que
`SATISFATORIO_AUTOMATICO` não significa equivalência ao desfecho judicial.

## Falhas técnicas

`LIDER_SEM_RETORNO` apareceu em 24 dos 50 casos e somou 176 ocorrências nas
rotações. Houve 57 `LLM_INVALID_PANEL`, contra 105 na v17. A distribuição foi:
38 na lente jurisprudencial, 15 na probatória e 4 na auditora.

Mesmo com a terceira tentativa e campos menores, a lente jurisprudencial continua
sendo o maior ponto de falha. Erros recorrentes incluem JSON iniciado e truncado,
opção que exige reformulação, citação de base não localizada e incoerência entre
decisão, valor, partes e fontes.

## Proposta para a v19

1. **Reduzir a saída jurisprudencial:** o modelo escolhe decisão, tipo de opção,
   fonte, valor e condições em campos curtos; proposta, premissa, ressalva, partes
   e trechos literais passam a ser derivados ou renderizados pelo código sempre
   que isso for mecanicamente verificável.
2. **Auditar o conjunto dos pedidos:** acrescentar verificação explícita de
   sobreposição entre multas, encargos, caução, danos e pedidos alternativos. O
   caso 0027 vira teste de regressão obrigatório.
3. **Reparar opção de forma limitada:** quando a auditoria marcar somente defeito
   corrigível de premissa, polo, escopo ou base, permitir uma única reformulação
   dirigida e nova auditoria. Não alterar conclusão nem inventar percentual.
4. **Corrigir a taxonomia do runner:** distinguir Termo integralmente apto, Termo
   misto com opções retidas, Termo sem opção aprovada e falha técnica. A auditoria
   que barra uma opção insegura não deve tornar inúteis as opções válidas do mesmo
   caso.
5. **Separar utilidade de equivalência:** manter uma nota operacional do Termo e
   calcular fora do IC uma nota semântica contra o gabarito, sem enviar o gabarito
   aos modelos.

Depois dos testes locais, a v19 deve repetir novamente os casos 0001–0050. Somente
um resultado que supere os gates autoriza o próximo bloco de 50.

## Encaminhamento

A proposta acima foi implementada na `v19.0.0-experimental`. A definição exata
do novo lote, as mudanças efetivamente incorporadas e os gates estão registrados
em `V19_BATCH1_PLAN.md`. Este relatório permanece congelado como baseline da v18.
