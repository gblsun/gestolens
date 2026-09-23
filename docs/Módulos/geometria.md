---
tags: [modulo]
arquivo: gestos/geometria.py
---
# geometria

`gestos/geometria.py` · voltar ao [[Início]]

Funções geométricas sobre landmarks normalizados.

- `distancia(a, b, aspecto)` — euclidiana com correção de [[Proporção da imagem]].
- `dedos_longos_estendidos(lm, aspecto, regra)` — regra `"vertical"` (código-base) ou `"distancia"` (ponta mais longe do punho que a PIP; invariante à rotação).
- `tamanho_mao(lm, aspecto)` — dist(punho 0, base do médio 9), escala para normalizar margens.

Usado por [[maos]] e [[rosto]]. Ver [[Landmarks da mão]].
