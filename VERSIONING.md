# Política de versões do Mediare IC

As versões públicas do IC avançam somente por números inteiros:

`v24` → `v25` → `v26` → …

- Não serão usadas versões públicas minor, como `v24.1` ou `v24.2`.
- Qualquer nova candidata, inclusive uma correção pequena, recebe o próximo
  número inteiro.
- Resultados, relatórios, commits e campanhas usam o mesmo número público.
- O literal interno segue o formato `M.0.0-experimental` (por exemplo,
  `24.0.0-experimental`) apenas porque as ferramentas do Studio validam esse
  formato. Ele representa publicamente a **v24**, e não uma versão minor.
- Diretórios de recibos já produzidos não são renomeados: são evidência
  imutável das chamadas pagas. O relatório consolidado atribui esses recibos à
  versão pública correspondente.

Os protótipos técnicos internos que sucederam a v23 foram consolidados como
v24. A renomeação não mudou a lógica funcional e não repetiu chamadas pagas.
