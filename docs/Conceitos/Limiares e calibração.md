---
tags: [conceito]
---
# Limiares e calibração

Todas as regras são heurísticas com limiares em [[config]]. Procedimento sugerido:

1. Rodar o [[pipeline]] e abrir `saidas/<video>.csv`.
2. Para cada estado (ex.: boca fechada / entreaberta / bem aberta), anotar trechos em `rotulos.csv` ([[Como preencher rotulos.csv]]).
3. Usar as colunas contínuas (`proporcao_boca`, `desvio_nariz`, `*_polegar_dif`, `yaw`) para ver onde as classes se separam e escolher o limiar no meio da lacuna.
4. **Separar vídeos de calibração e de avaliação** (ex.: calibrar em IMG_7457–7458, avaliar em 7459–7461) — ver [[Protocolo de testes]].
5. Rodar `--so-avaliar` e conferir [[Avaliação]].

## Achados nos vídeos

![[grafico_boca.png]]

- **Boca** ([[Ex4 - Boca aberta e fechada]]): fechada ≈ 0,00–0,02; aberta em [[IMG_7460]] chega a 0,74. O limiar 0,15 separa bem os dois estados; fala e sorriso ainda precisam ser testados.
- **Direção** ([[Ex5 - Direção do rosto]]): com a câmera fora do eixo o "de frente" já tem desvio ≈ 0,12 ([[IMG_7457]]). Subtrair uma referência calibrada resolveria isso.
- **Dedos** ([[Ex2 - Contagem de dedos]]): a regra vertical falha com a mão invertida ([[IMG_7459]]); por isso `REGRA_DEDOS = "distancia"`.

Faixas "indefinido" perto do limiar ([[Ex3 - Polegar para cima e para baixo]], [[Ex5 - Direção do rosto]]) e a [[Suavização temporal]] reduzem decisões instáveis.

Voltar ao [[Início]].
