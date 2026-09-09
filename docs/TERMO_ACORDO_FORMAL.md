# Termo Final de Mediação: pesquisa e critérios do gerador

Este documento registra os critérios usados por `termo_acordo.py`. É uma base
técnica para elaboração e conferência; não substitui a análise de um advogado,
especialmente em matéria de família, trabalho, direitos indisponíveis, relações
de consumo, participação de incapaz, poder público ou acordo já judicializado.

## Conclusão em termos simples

O Termo de Opção ainda não é o acordo. Ele apresenta ao mediador um cenário e
mantém números em aberto para negociação. O Termo Final só pode ser preparado
depois que todas as partes:

1. escolherem o mesmo cenário;
2. fixarem cada percentual ou valor que estava aberto;
3. definirem exatamente quem fará o quê, para quem, como e até quando; e
4. fornecerem os dados de qualificação e a forma de assinatura.

O gerador segue essa separação. Ele calcula valores com `Decimal`, arredonda
somente ao centavo e interrompe a geração se ainda existir variável aberta ou
dado formal obrigatório ausente.

## Base oficial consultada

- A [Lei de Mediação, arts. 1º a 3º e 20](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13140.htm)
  preserva a autonomia das partes, permite acordo sobre todo o conflito ou parte
  dele e estabelece que o termo final com acordo é título executivo
  extrajudicial. Direitos indisponíveis que admitam transação exigem homologação
  judicial e oitiva do Ministério Público.
- O [Código de Processo Civil, arts. 783, 784 e 786](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105compilada.htm)
  exige obrigação certa, líquida e exigível para execução. O art. 784 prevê, entre
  outras vias, documento particular assinado pelo devedor e por duas testemunhas
  e instrumento de transação referendado pelos profissionais ali enumerados.
- O [Código Civil, arts. 840 a 850](https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm)
  disciplina a transação, determina sua interpretação restritiva e permite
  cláusula penal. Por isso, a quitação produzida pelo script é condicionada ao
  cumprimento integral e limitada aos pedidos expressamente acordados.
- O [Curso de Mediação Judicial do CNJ](https://www.cnj.jus.br/wp-content/uploads/conteudo/destaques/arquivo/2015/03/a801d32fa970c1b2a382e0ca346d03e0.pdf)
  recomenda redação clara, objetiva e específica, compreensão e assinatura por
  todos e, havendo pagamento, identificação de quem paga e recebe, montante,
  forma e momento do pagamento.
- A [Resolução CNJ nº 125/2010](https://atos.cnj.jus.br/atos/detalhar/156)
  inclui entre os dados essenciais a qualificação das partes, identificação e
  natureza do conflito, e enfatiza requisitos mínimos e exequibilidade.

## Avaliação do exemplo da imagem

O exemplo tem uma boa estrutura visual e acerta ao resumir o conflito, indicar
devedor e credor, escrever o valor em número e por extenso, fixar prazo, tratar
da quitação e reservar espaço para assinaturas. Ele não deve, porém, ser usado
sem ajustes como padrão final:

- a numeração salta as cláusulas 1 e 5;
- faltam a qualificação completa das partes, local e data da assinatura;
- convém tornar vencimento e forma de pagamento inequívocos;
- a quitação ampla deve ser conferida e vinculada ao cumprimento integral e ao
  objeto preciso do acordo;
- multa, juros e correção só devem aparecer se efetivamente negociados;
- citar o art. 784, III, do CPC não substitui seus requisitos. A imagem mostra
  partes e mediador, mas não duas testemunhas. O termo final de mediação também
  possui fundamento próprio no art. 20 da Lei nº 13.140/2015, desde que seja de
  fato o termo que encerra uma mediação com acordo;
- a adequação a regras especiais, homologação ou foro depende do caso concreto.

## Decisões conservadoras do script

- O JSON precisa registrar `aceite.todos_concordam: true` e o ID exato do Termo
  de Opção escolhido.
- Uma fórmula exige `--percentual`; uma faixa exige `--valor`, sempre dentro dos
  limites aprovados pelo IC.
- Dados anonimizados do caso não são usados para inventar nomes ou documentos.
  A qualificação real das partes fica em um segundo arquivo local, que não deve
  ser enviado ao blockchain nem versionado com dados pessoais.
- A quitação é específica e só ocorre depois do cumprimento integral.
- Multa, juros, correção, confidencialidade, foro, advogados e testemunhas só são
  incluídos quando informados expressamente.
- O documento informa a origem do cenário para rastreabilidade, mas não reproduz
  raciocínios das lentes nem apresenta o IC como autor da decisão.

Antes da assinatura, o mediador deve conferir identidade e poderes de
representação, consentimento, valores, datas, dados de pagamento, escopo da
quitação, regras especiais e o mecanismo de assinatura aplicável.
