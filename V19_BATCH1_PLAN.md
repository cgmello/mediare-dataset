# Plano e hipótese do lote v19 — casos 0001–0050

## Decisão

A `v19.0.0-experimental` repetirá exatamente os casos 0001–0050 usados na v17 e
na v18. O contrato continuará sendo `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`,
com uma transação por vez e intervalo mínimo de 15 segundos depois de cada
resultado terminal. O lote para novamente ao completar 50 casos.

A v18 está preservada pela tag `ic-v18.0.0`; se os resultados piorarem, o código
pode ser restaurado sem confundir os artefatos das campanhas. A v19 terá saída
isolada em `res_canary_v19/` e snapshot imutável do código instalado.

## Baseline v18

- 38/50 `MAJORITY_AGREE`; 12/50 `MAJORITY_DISAGREE`.
- 59 rotações; mediana de 263 segundos.
- 3 satisfatórios automáticos, 20 para revisão, 15 com retenções e 12 falhas
  técnicas na taxonomia antiga.
- 31/50 Termos seriam úteis se oito Termos mistos fossem corretamente contados.
- 57 painéis inválidos de LLM, dos quais 38 na lente jurisprudencial.
- 24/50 casos tiveram ao menos um diagnóstico `LIDER_SEM_RETORNO`.
- Zero inconsistências entre estado, painel e Termo.
- Defeito material observado no caso 0027: multa aprovada sem detectar possível
  sobreposição com encargos do mesmo inadimplemento.

O detalhamento e os exemplos permanecem em `V18_BATCH1_REPORT.md`.

## O que muda na v19

1. **Saída jurisprudencial menor.** O modelo decide tipo, fontes, base e critério.
   Partes, citações e redação padronizada são preenchidas pelo contrato sem mudar
   valor, fonte, percentual ou mérito escolhidos.
2. **Falha localizada.** Uma opção estruturalmente inválida vira
   `opcao_nao_validada`; as conclusões válidas daquele painel não são descartadas.
3. **Auditoria cruzada.** Cada auditoria pode indicar `conflitos_com` e precisa
   associar `DUPLA_CONTAGEM` a outro `pedido_id` real. O prompt manda comparar dano,
   base, fato gerador, cumprimento, pedidos alternativos, multas e encargos. A
   auditora não repete uma terceira decisão: devolve apenas o teste refutador da
   opção; probatória e jurisprudencial continuam como lentes decisórias.
4. **Um reparo no máximo.** Opções retidas recebem uma tentativa dirigida e uma
   reauditoria. Falha, repetição do defeito ou estrutura insegura mantém a retenção.
5. **Taxonomia orientada ao produto.** O relatório distingue Termo integral, Termo
   parcial com retenções, somente diligências, nenhuma opção aprovada e falha
   técnica. Aderência ao gabarito continua separada da utilidade para mediação.

## Gates após 50 casos

| Gate | Meta |
|---|---:|
| `MAJORITY_AGREE` | pelo menos 40/50 |
| Integridade estado/painel/Termo | zero inconsistências |
| `APTO_INTEGRAL` + `APTO_PARCIAL_COM_RETENCOES` | pelo menos 35/50 |
| Casos com `LIDER_SEM_RETORNO` | no máximo 10/50 |
| Ocorrências de `LLM_INVALID_PANEL` | menos de 20 |
| Revisão manual dos Termos aptos | nenhum erro material como o 0027 |

Os gabaritos nunca entram no IC nem nos prompts dos validadores. Depois do lote,
a revisão externa deve registrar separadamente utilidade para mediação e aderência
ao benchmark. Não iniciar 0051–0100 antes dessa reavaliação.
