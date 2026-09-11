# v23.2.1 — relatório do gate técnico

## Resultado

A sequência técnica v23.2.0 → v23.2.1 foi **aprovada para o gate de 20
sentinelas**. O gate primário e os dois controles rodaram na v23.2.0; a falha
residual observada em 0048 gerou a correção estreita v23.2.1, validada por testes
determinísticos e por uma repetição nova de 0048. A semântica RP/CR da v23.1
permaneceu congelada: o prompt do catálogo é byte a byte equivalente e o
validador de catálogo não foi alterado.

O gate não exige maioria em todo caso difícil. Ele exige que falha de
disponibilidade, objeção de mérito e defeito de catálogo sejam observáveis como
eventos diferentes.

## Alterações técnicas

- OpenRouter local: raciocínio opcional do DeepSeek desativado, evitando que o
  modelo consuma os 10.000 tokens sem produzir o JSON solicitado.
- Auditora: `DUPLA_CONTAGEM` sem outro ID conflitante permanece fail-closed,
  mas é normalizada para `reformular/PREMISSA` em vez de invalidar o painel.
- Revisores: `PEDIDO` exige falha de catálogo estruturada para o mesmo ID, com
  fonte, evidência e correção; objeção vaga não vira voto favorável.
- Normalização: ao descartar `VALOR_INFERIDO` objetivamente impossível, apenas
  o código `PEDIDO` redundante é removido; `CONCLUSAO`, `FONTES` e `OPCAO`
  continuam intactos.
- GLM local: `reasoning=low` preservado e teto de saída aumentado para 20.000,
  pois o raciocínio desse modelo é obrigatório.

## Resultados por caso

| Caso | Antes | v23.2.1 / controle relevante | Leitura |
|---|---|---|---|
| 0013 | nenhum painel; DeepSeek esgotava 10.000 tokens | painel válido; 2 Agree, 2 objeções | falha técnica corrigida; divergência atual é substantiva |
| 0017 | painel variável; 1 aprovação, 2 objeções vagas, 1 erro | painel válido; 4/4 Agree | consistência da revisão corrigida sem mudar 4 RP + 2 CR |
| 0033 | auditora invalidava o painel | painel válido; 4/4 Agree | preocupação preservada como `reformular/SEM_SUPORTE` |
| 0048 | falha intermitente do DeepSeek; primeiro controle 2 Agree + 2 erros | repetição v23.2.1 válida; 4/4 Agree | líder e revisores recuperados em snapshot novo |
| 0050 | risco de RP03/RP04 passar sem bloqueio explícito | painel válido; 4/4 Agree e conflitos preservados | normalização não apagou dupla contagem real |

Em 0050, a auditora manteve `RP01↔RP02` como alternativas e
`RP03↔RP04` como sobreposição material. Isto é o controle central de que a
correção estrutural não relaxou a proteção semântica.

## Custos

| Rodada | Casos concluídos | Chamadas | Tokens | Custo |
|---|---:|---:|---:|---:|
| v23.2.0 — gate primário + controles | 5 | 57 | 554.910 | US$ 1,316493867654 |
| v23.2.1 — repetição limpa de 0048 | 1 | 8 | 67.861 | US$ 0,152919033000 |
| **Total** | **6 execuções** | **65** | **622.771** | **US$ 1,469412900654** |

## Decisão e próximo checkpoint

- promover a v23.2.1 apenas para a repetição dos mesmos 20 sentinelas;
- manter `0013` como caso de divergência semântica 2–2, não como falha técnica;
- contabilizar separadamente painel válido, maioria, erro de revisor e objeção
  substantiva;
- não promover ao Studio antes de confirmar que os ganhos técnicos não
  degradam os outros sentinelas.
