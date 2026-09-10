# Plano de expansão da base — +500 casos reais resumidos

## Decisão atual

A fonte continua sendo o CJPG/TJSP. A expansão será feita em dez lotes de até
50 novos processos, com deduplicação contra tudo que já foi coletado. Cada lote
gera um relatório apenas com contagens, categorias e erros técnicos; o texto
integral das decisões permanece na área local ignorada pelo Git.

**Coleta concluída em 2026-09-10:** dez lotes adicionaram 500 decisões, levando
o staging privado de 244 a 744 processos únicos. A transformação em casos
resumidos permanece como etapa separada e ainda não foi executada.

## Duas etapas diferentes

1. **Coleta pública:** `coletar_cjpg.py` consulta o site do TJSP, pagina os
   resultados e salva as decisões ainda não vistas. É um web scraper online,
   não um processo offline, mas **não usa OpenRouter nem qualquer LLM**.
2. **Transformação:** uma decisão bruta precisa ser filtrada, pseudonimizada e
   convertida nas peças resumidas usadas pelo dataset. Essa etapa se beneficia
   de LLM. O OpenRouter pode substituir a API Anthropic direta e usar o crédito
   patrocinado, mas somente depois de uma sanitização local e de uma validação
   contra vazamento de dados pessoais.

Portanto, baixar 50 novas fontes custa zero em API de LLM. Produzir 50 novos
casos estruturados pode consumir OpenRouter. Os custos dessa segunda etapa serão
medidos separadamente dos testes do IC.

## Controles

- lote máximo de 50 e intervalo mínimo de três segundos entre páginas;
- retomada por número de processo e escrita incremental;
- exclusão de resultados marcados como segredo de justiça;
- nenhum corpo de sentença no terminal, relatório versionado ou commit;
- metadados anormalmente longos são descartados para impedir que o corpo seja
  confundido com data, vara ou comarca;
- transformação externa bloqueada até existir sanitização local, teste de
  vazamento e teto de custo próprio;
- casos novos ficam fora da calibração v21 inicial e podem formar holdouts.

## CourtListener / RECAP

CourtListener é o mecanismo público de pesquisa jurídica da organização
americana Free Law Project. RECAP é o arquivo associado de processos da Justiça
Federal dos Estados Unidos, alimentado por documentos obtidos do sistema PACER,
por usuários e por parcerias. Ele contém dockets, petições e PDFs originais — em
alguns casos digitalizações, OCR e anexos — e por isso é uma boa fonte para testar
ingestão de documentos heterogêneos.

Para a Mediare, seu valor imediato é **técnico**, não jurídico: testar PDF,
imagem, OCR, anexos e classificação documental. A base não representa o direito
brasileiro nem necessariamente disputas de pequeno valor. Alguns documentos já
arquivados são gratuitos; documentos ausentes podem exigir recuperação paga no
PACER. Documentos públicos também podem conter dados pessoais.

Fontes oficiais:

- [CourtListener e RECAP](https://free.law/projects/courtlistener/)
- [RECAP API](https://wiki.free.law/c/courtlistener/help/api/rest/v4/recap)
- [API usage](https://wiki.free.law/c/courtlistener/help/api/rest/v4/api-usage)
- [Bulk legal data](https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data)
