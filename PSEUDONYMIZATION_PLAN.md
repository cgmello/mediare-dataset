# Pseudonimização das 500 novas decisões públicas

## Escopo

Os registros 245–744 de `sentencas.jsonl` recebem IDs internos 0501–1000. O
processo original e as respostas dos detectores ficam somente em
`res_pseudonymization_0501_1000/`, que é ignorado pelo Git. A saída consolidada
é `res_pseudonymization_0501_1000/pseudonymized.jsonl`.

O resultado é chamado de **pseudonimizado**, e não de anonimizado de forma
irreversível. Data, comarca, foro, vara, fatos e valores são preservados a pedido
do projeto e podem permitir reencontrar uma sentença pública.

## Método

1. Claude Sonnet 4.6 e GPT-5.4 identificam entidades independentemente.
2. Cada modelo devolve apenas substrings exatas e sua classe; nenhum deles
   reescreve fatos ou valores.
3. O Python une as detecções com identificadores e papéis extraídos localmente.
4. O número do processo atual vira o ID interno; processos citados viram
   `PRECEDENTE-NNN`; pessoas e organizações privadas viram iniciais sem
   partículas portuguesas; identificadores diretos viram `[DADO_REMOVIDO]`.
5. Uma varredura local remove processos, CPF, CNPJ e e-mail eventualmente
   omitidos pelos modelos.
6. Auditoria determinística retém qualquer registro em que um identificador
   detectado permaneça.

Toda chamada exige simultaneamente `provider.zdr=true` e
`provider.data_collection=deny`. O OpenRouter declara que ZDR restringe o
roteamento a endpoints que não retêm prompts; o logging de conteúdo também deve
permanecer desativado na conta.

## Execução e custo

- Primeiro checkpoint: cinco processos.
- Campanha total: 500 processos, duas chamadas principais por processo.
- Teto persistente inicial: US$ 30.
- Cache local permite retomada sem repetir chamadas concluídas.
- Logs de terminal contêm somente ID interno, estado, progresso e custo.

Depois da pseudonimização, outro estágio selecionará decisões aproveitáveis e
produzirá os diretórios de casos uniformizados. Esse estágio não está misturado
ao presente runner para que falhas de privacidade sejam detectadas antes da
reconstrução documental.

Referências:

- [OpenRouter Zero Data Retention](https://openrouter.ai/docs/guides/features/zdr)
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [LGPD — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm)
- [FAQ da ANPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/perguntas-frequentes/perguntas-frequentes)
