# Pipeline CJPG → casos de teste Mediare

## Passos
1. `pip install requests beautifulsoup4 anthropic`
2. `python coletar_cjpg.py --por-categoria 25`   → gera `sentencas.jsonl` (~250 sentenças, ~15-20 min)
   - Aumente `--por-categoria` para mais volume (ex.: 30 × 10 categorias = 300)
3. `export ANTHROPIC_API_KEY=sk-...`
4. `python gerar_casos.py --limite 200`          → gera `casos_reais/caso_real_NNN/`

## Avisos importantes
- **Ritmo:** o coletor espera 3 s entre requisições. Não reduza — respeite o e-SAJ.
- **Seletores:** se o TJSP mudar o HTML da listagem, ajuste `parse_pagina()` em
  `coletar_cjpg.py` (a função é curta e comentada).
- **LGPD:** as sentenças são públicas, mas o prompt manda pseudonimizar nomes.
  Não redistribua o dataset com dados pessoais.
- **Qualidade:** revise manualmente uma amostra de ~10% dos gabaritos gerados
  pela API antes de usar como métrica de acerto.
- **Custo API:** ~200 casos ≈ 200 chamadas de ~8-12k tokens de entrada cada.
