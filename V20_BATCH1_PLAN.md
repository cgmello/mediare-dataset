# Plano e hipótese do lote v20 — casos 0001–0050

## Decisão

A `v20.0.0-experimental` repetirá exatamente os casos 0001–0050 das versões 18 e
19 no contrato `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`. As chamadas serão
seriais, com intervalo mínimo de 15 segundos após cada resultado terminal e parada
obrigatória ao completar 50 casos.

A v19 está preservada pela tag `ic-v19.0.0`. A v20 terá saída isolada em
`res_canary_v20/` e snapshot imutável do código efetivamente instalado.

## Baseline v19 a preservar

- 47/50 `MAJORITY_AGREE`, três falhas técnicas e 24 rotações;
- mediana de 186 segundos;
- 29/50 Termos com opção integral ou parcial e 41/50 com orientação se as
  diligências são incluídas;
- zero inconsistências nos 47 Termos;
- 16 `LLM_INVALID_PANEL` e 11 casos com `LIDER_SEM_RETORNO`;
- o caso 0027 reteve corretamente a multa com riscos de dupla contagem e escopo.

## O que muda na v20

1. **Fórmula a partir do valor pedido, sem convertê-lo em dívida.** Para pedido
   monetário indeterminado por nexo, valor ou proporção, uma diligência ou opção
   estruturalmente inválida pode virar `valor literal da PR × p`, com `p` aberto
   entre 0% e 100%. Sem valor exatamente localizado na PR, não há conversão.
2. **Rebaixamento seguro de faixa.** Se a base está válida mas o percentual da
   faixa não está documentado, o código remove o percentual e mantém somente a
   fórmula negociável. Nenhum número novo é criado.
3. **Recuperação de modalidade.** Uma opção monetária gerada para pedido não
   monetário pode virar alternativa não monetária condicionada, usando apenas as
   fontes já selecionadas e as partes do catálogo.
4. **Alternativa não cumulativa.** A auditoria ganha `apta_com_ressalva` somente
   para risco isolado de `DUPLA_CONTAGEM`, com conflito identificado e redação que
   proíbe soma. O Termo exibe o alerta e os IDs conflitantes.
5. **Barreira preservada.** Falta de suporte, valor inventado, escopo, polo,
   premissa ou qualquer combinação de riscos continua em `reformular`. O 0027
   permanece teste obrigatório para impedir regressão.

## Gates após 50 casos

| Gate | Meta |
|---|---:|
| `MAJORITY_AGREE` | pelo menos 47/50 |
| Integridade estado/painel/Termo | zero inconsistências |
| `APTO_INTEGRAL` + `APTO_PARCIAL_COM_RETENCOES` | pelo menos 35/50 |
| `SOMENTE_DILIGENCIAS` | no máximo 8/50 |
| `SEM_OPCAO_APROVADA` | no máximo 5/50 |
| Casos com `LIDER_SEM_RETORNO` | no máximo 10/50 |
| Ocorrências de `LLM_INVALID_PANEL` | menos de 20 |
| Revisão do caso 0027 | multa insegura continua retida |

Os gabaritos não entram no IC nem nos prompts. A análise após o lote deve separar
integridade, utilidade para mediação, consenso e aderência externa ao benchmark.
Nenhum caso de 0051 em diante será enviado antes dessa reavaliação.
