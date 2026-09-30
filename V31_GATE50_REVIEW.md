# Revisão qualitativa do gate v31 — 50 casos

## Resultado executivo

- 50/50 casos concluídos: 37 `LOCAL_MAJORITY_AGREE` e 13 `LOCAL_MAJORITY_DISAGREE`.
- 48/50 painéis válidos e 24/50 saídas úteis.
- 455 chamadas, 2.840.952 tokens e US$ 5,8011.
- A repetição de `0050` e `0173` recuperou dois painéis válidos e úteis, mas ambos permaneceram `Disagree`; custo adicional US$ 0,2973.
- Decisão: **não promover a v31 ao Studio**.

## Comparação direta v30 × v31

| Métrica | v30 | v31 | Leitura |
|---|---:|---:|---|
| Maioria local | 39/50 | 37/50 | regressão de 2 casos |
| Painéis válidos na campanha | 50/50 | 48/50 | as 2 falhas foram recuperadas no retry |
| Saídas úteis | 28/50 | 24/50 | regressão operacional |
| Pedidos pendentes | 56 | 46 | melhor cobertura |
| Correspondência com auditoria | 52/98 | 48/98 | pior equilíbrio das abstenções |
| Resultado exato resolvido/correto | 13/19 | 15/19 | melhora de precisão exata |
| Desfecho binário resolvido/correto | 27/28 | 24/25 | precisão semelhante, menor cobertura |
| Lacunas indispensáveis preservadas | 27/33 | 26/33 | pequena regressão |

Transições: 33 casos permaneceram `Agree`; quatro passaram de `Disagree` para `Agree` (`0017`, `0021`, `0142`, `0476`); seis passaram de `Agree` para `Disagree` (`0014`, `0046`, `0079`, `0088`, `0209`, `0430`); sete permaneceram `Disagree`.

## Classificação dos 13 desacordos

### Falhas técnicas recuperadas, sem consenso

- `0050`: `KeyError` na campanha; retry válido e útil, mas `Disagree` por variância sobre pedidos sobrepostos.
- `0173`: painel jurisprudencial inválido seguido de erro de transporte; retry válido e útil, mas `Disagree` por conclusão dos reembolsos.

### Regressões reais de catálogo

- `0046`: uniu declaração de inexigibilidade e retirada do cadastro restritivo, embora a PR enumere os dois pedidos separadamente.
- `0079`: omitiu o pedido expresso de ressarcimento dos prejuízos decorrentes da pendência fiscal no CNO.
- `0088`: omitiu o pedido contraposto expresso de exclusão de restrição cadastral.

### Fronteiras semânticas ou limitações do schema

- `0037`: os revisores continuam divididos entre declaração, pagamento e negociação da dívida admitida pelo próprio requerente.
- `0083`: o schema `autor/contra` representa papéis genéricos e não distribui integralmente pedidos entre locador e fiadora.
- `0145`: permanece aberta a política sobre “excesso de execução” como providência processual ou resultado bilateral.
- `0243`: divergência sobre consolidar ou separar principal, multa e juros da mesma cobrança.

### Divergências de mérito

- `0014`, `0081`, `0209` e `0430`: o catálogo é utilizável; os revisores discordaram das conclusões ou fontes.

## Recomendação

Não continuar ajustando a v31 diretamente. Criar a v32 sobre a v30 e portar apenas as correções confirmadas: remover CR defensiva sem saldo independente; impedir admissão narrativa como pedido; unir declaração/abstenção inseparáveis sobre a mesma dívida; e aceitar sobreposição expressa quando a auditora contiver dupla contagem. Acrescentar três sentinelas negativas (`0046`, `0079`, `0088`) para impedir novas omissões. Primeiro executar um gate dirigido com os seis ganhos e os três regressivos; depois repetir os 50 casos.
