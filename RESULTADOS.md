# Medição de referência — v9, 128 casos

Amostra: `casos_utilizaveis.txt` (128 casos reais/ouro, gabaritos de vocabulário
fechado, coerentes, líquidos, confiança média ou alta, sem os cinco processos
duplicados). 48 de condenação patrimonial zero, 80 positivos.
Modelo: `claude-sonnet-4-5`. Painel de 1 estágio. IC95 de Wilson.

Reproduzir:

    python3 harness.py --rodar --out res_v9son --ic ic.py \
      --modelo claude-sonnet-4-5 --casos @casos_utilizaveis.txt
    python3 usar_v2.py res_v9son && python3 numeros.py res_v9son

## O mediador veria a resposta certa?

| métrica | taxa | IC95 |
|---|---|---|
| faixa contém o gabarito | 61,7% (79/128) | 53,1 – 69,7 |
| só os positivos | 60,0% (48/80) | 49,0 – 70,0 |
| só os zero | 64,6% (31/48) | 50,4 – 76,6 |
| faixa útil como pauta (largura ≤ 30%) | 64,1% (82/128) | 55,5 – 71,9 |

## O comitê sabe negar?

| métrica | taxa | IC95 |
|---|---|---|
| propõe valor > 0 onde o juiz negou | 54,2% (26/48) | 40,3 – 67,4 |
| unânime, faixa sem tocar o zero | 18,8% (9/48) | 10,2 – 31,9 |

Os nove do pior caso — unânimes, largura zero, gabarito improcedente. No
desenho de Termo automático virariam acordo sem revisão humana:

    0134 [44.994,24]   0131 [21.396,76]   0172 [16.881,81]
    0181 [12.500,00]   0180 [10.000,00]   0063 [ 8.764,00]
    0041 [ 2.598,00]   0115 [ 1.800,00]

0041, 0063 e 0086 reproduzem o mesmo valor ao centavo através de dois modelos
(sonnet-4-5 e haiku-4-5) e quatro versões de prompt. São erros sistemáticos,
não ruído amostral.

## Unanimidade é sinal de acerto?

| grupo | faixa contém o gabarito | IC95 |
|---|---|---|
| painéis unânimes (66) | 57,6% | 45,6 – 68,8 |
| painéis divergentes (62) | 66,1% | 53,7 – 76,7 |

Os intervalos se sobrepõem quase inteiramente e a direção é contra a
unanimidade. Terceira medição independente a dizer o mesmo: **unanimidade não
carrega informação sobre correção.** A premissa do Termo automático está morta.

## Acerto por lente (centro da tese, ±15%)

| lente | taxa | IC95 |
|---|---|---|
| jurisprudencial | 53,1% (68/128) | 44,5 – 61,6 |
| estrita | 52,8% (67/127) | 44,1 – 61,2 |
| ampla | 48,4% (62/128) | 40,0 – 57,0 |

## On-chain

16 transações no Studio (v8b + v9), 13 aceitas válidas. Faixas idênticas
reproduzidas em endereços independentes — a camada de consenso é estável.

## O que já foi descartado por medição

- **Painel de 2 estágios** (mérito antes do valor): pior nas duas direções.
  Concessão indevida 50% → 83%; contenção nos positivos 57% → 36%. Quantificar
  é a disciplina que produz a negação. Ver comentário no topo do bloco em
  `ic.py`.
- **Régua heurística de chaves livres** (`gold.py` sozinho): concorda consigo
  mesma em 0 de 5 pares duplicados, contra 5 de 5 do vocabulário fechado, e
  aceita valores errados (0079 a 64.734,88 quando o devido era 32.367,44).
