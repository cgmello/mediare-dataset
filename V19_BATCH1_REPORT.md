# Relatório do lote comparativo v19 — casos 0001–0050

## Recomendação

A v19 foi uma evolução relevante e deve permanecer como marco recuperável. Ela
produziu consenso em 47 dos 50 casos, reduziu as falhas técnicas para três e
entregou orientação aproveitável ao mediador em 41 casos quando diligências úteis
são incluídas. A v20 deve partir da v19 e atacar apenas os dois gargalos observados:
excesso de diligências quando já existe uma base literal de negociação e retenções
motivadas somente por sobreposição que pode ser tratada como alternativa não
cumulativa.

Não há justificativa para voltar à v18. A v20 repetirá os mesmos 50 casos e não
avançará para 0051–0100 antes de nova avaliação.

## Comparação direta

| Métrica nos casos 0001–0050 | v18 | v19 |
|---|---:|---:|
| `MAJORITY_AGREE` | 38 (76%) | 47 (94%) |
| Falhas técnicas | 12 | 3 |
| Rotações | 59 | 24 |
| Tempo mediano por caso | 264 s | 186 s |
| Integral + parcial com opção | 27* | 29 |
| Incluindo somente diligências | 30* | 41 |
| Casos com `LIDER_SEM_RETORNO` | 24 | 11 |
| Ocorrências de `LLM_INVALID_PANEL` | 57 | 16 |
| Inconsistências estado/painel/Termo | 0 | 0 |

\* A v18 foi reclassificada com a taxonomia da v19 para permitir comparação.

## Resultado operacional da v19

- 13 `APTO_INTEGRAL`;
- 16 `APTO_PARCIAL_COM_RETENCOES`;
- 12 `SOMENTE_DILIGENCIAS`;
- 6 `SEM_OPCAO_APROVADA`;
- 3 `FALHA_TECNICA`.

Foram analisados 226 pedidos nos 47 Termos válidos: 80 diligências, 39 fórmulas,
19 faixas, 33 opções não monetárias, 39 `sem_opcao` e 16 opções que não passaram
pela validação estrutural. O estado consolidado foi 132 opções condicionais, 58
retidas e 36 sem opção.

## O que funcionou bem

1. **Consenso e estabilidade.** O acordo entre validadores subiu de 76% para 94%,
   com menos da metade das rotações e queda material do tempo mediano.
2. **Falhas localizadas.** Uma opção malformada deixou de apagar conclusões
   válidas do restante do painel; isso reduziu as falhas técnicas de 12 para 3.
3. **Termo útil mesmo quando parcial.** A nova taxonomia preservou as opções que
   passaram e explicou separadamente as que foram retidas.
4. **Auditoria cruzada.** Dezessete casos registraram conflitos entre pedidos. O
   caso 0027, defeito material da v18, foi corrigido: a multa de R$ 2.100,00 ficou
   retida com `DUPLA_CONTAGEM` e `ESCOPO`, em conflito com RP03.
5. **Integridade.** Os 47 painéis e Termos gravados passaram pelas verificações
   locais de versão, estrutura e correspondência entre estado e arquivo.

## O que ainda limitou o resultado

- A meta prévia de 35 casos com opção integral ou parcial não foi atingida:
  foram 29. Doze casos ficaram somente em diligências e seis sem opção aprovada.
- Dezesseis opções caíram no fallback estrutural. Entre as causas estavam base
  ou citação não localizada, ausência de valor, tipo incompatível e proporção
  sem suporte literal.
- Treze das 58 retenções tinham somente `DUPLA_CONTAGEM`. Algumas podem ser
  apresentadas com segurança como escolhas alternativas, desde que o Termo proíba
  expressamente somá-las. As outras 45 retenções possuem risco adicional ou não
  são recuperáveis por essa regra.
- `LIDER_SEM_RETORNO` apareceu em 11 casos, um acima do gate de 10, embora a
  queda em relação aos 24 casos da v18 seja expressiva.

## Gates pré-registrados da v19

| Gate | Resultado | Situação |
|---|---:|---|
| Pelo menos 40/50 `MAJORITY_AGREE` | 47/50 | Passou |
| Zero inconsistências estado/painel/Termo | 0 | Passou |
| Pelo menos 35/50 integral + parcial | 29/50 | Falhou |
| Casos com `LIDER_SEM_RETORNO` no máximo 10 | 11/50 | Falhou por um |
| Menos de 20 `LLM_INVALID_PANEL` | 16 | Passou |
| Sem repetição do erro material do 0027 | opção retida | Passou |

## Hipótese v20

A v20 preserva a arquitetura, as três lentes, o EP único, o Termo determinístico
e todas as barreiras de integridade da v19. Ela acrescenta somente recuperações
conservadoras: transforma uma diligência monetária em fórmula quando o valor do
pedido aparece literalmente na PR, rebaixa faixa com percentual não comprovado
para fórmula com percentual em aberto, corrige tipo monetário em pedido não
monetário e admite `apta_com_ressalva` apenas quando o único risco é
`DUPLA_CONTAGEM`, existe outro pedido identificado e a opção já proíbe soma.

Qualquer risco adicional continua retendo a opção. Essa regra preserva
explicitamente a proteção que corrigiu o caso 0027.
