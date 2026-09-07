# Relatório da Fase 2A — baseline v17

## Decisão

A campanha da `v17.0.0-experimental` foi encerrada antecipadamente. Nos primeiros
50 casos, somente 5 transações (10%) obtiveram `MAJORITY_AGREE`; 45 tiveram
`MAJORITY_DISAGREE`. Continuar os 449 casos restantes produziria custo e volume
sem uma hipótese razoável de melhora dentro da mesma versão.

O caso 0051 já havia sido enviado quando a decisão de parada foi tomada. Ele foi
apenas acompanhado até o estado terminal, sem envio do caso 0052. Também terminou
`UNDETERMINED/ERROR`; o fechamento definitivo ficou em 51 processados, com 46
falhas técnicas, 4 casos para revisão de utilidade e 1 problema de conteúdo. O
manifesto local registra o encerramento e impede retomada acidental.

## Resultado que motivou a parada

Nos 50 resultados usados para decidir:

- 45 `INSATISFATORIO_TECNICO` por falta de consenso;
- 4 `REVISAR_UTILIDADE` (0005, 0006, 0007 e 0039);
- 1 `INSATISFATORIO_CONTEUDO` (0031);
- nenhum `SATISFATORIO_AUTOMATICO` sob a triagem estrita;
- 40 transações terminaram `UNDETERMINED` e 10 `FINALIZED`;
- a amostra continha 6 casos ouro e 44 reais.

## Padrões observados

Os recibos sanitizados registraram 105 ocorrências de `LLM_INVALID_PANEL`:
68 na lente jurisprudencial, 33 na probatória e 4 na auditora. Isso indica que o
principal problema não era uma única tese jurídica, mas a dificuldade de vários
modelos produzirem repetidamente o mesmo schema longo e estrito.

Os diagnósticos mais frequentes foram `LIDER_SEM_RETORNO` (326 ocorrências),
`REVISOR_CATALOGO` (166) e `CATALOGO_QUANTIDADE` (123). Entre erros de opção,
apareceram com frequência citação da base não localizada, valor ausente do trecho,
inversão das partes e concessão monetária sem valor positivo.

Mesmo nos cinco casos com consenso, a utilidade variou. Foram encontrados dois
problemas de apresentação no Termo: conclusão que passou descrita como não
definitiva e `sem_opcao` rotulada como reprovação da auditoria. No caso 0039,
texto livre também inventou sufixos como `DR1`, embora o protocolo tenha apenas
os IDs `PR`, `RR`, `DR` e `DD`.

## Hipótese da v18

A v18 ataca os grupos de falha sem remover as verificações materiais:

- o líder continua produzindo catálogo e três lentes completas;
- cada validador recebe a proposta do líder e retorna uma revisão compacta por
  pedido, em vez de regenerar catálogo e três lentes;
- a revisão separa fidelidade do pedido, defensabilidade das conclusões,
  compatibilidade das fontes e segurança da opção;
- textos ganham limites menores e até três tentativas para recuperar JSON
  truncado ou estruturalmente inválido;
- partes da opção são derivadas do catálogo e citações de base podem ser
  reancoradas somente em trecho literal do mesmo resumo, sem inventar valor,
  fonte ou conclusão;
- o Termo corrige os estados `passou`, `nao_passou` e `sem_opcao` e remove
  sufixos numéricos inexistentes dos quatro IDs de fonte.

## Próxima medição

A seleção fixa em `canary_v18.json` repete os casos 0001–0050 para uma comparação
direta entre versões. Os critérios de saída estão em `V18_CANARY.md`. O bloco
seguinte não será iniciado apenas por melhora pontual: depende de consenso,
integridade do estado/Termo, utilidade da pauta e ausência de erro dominante.
