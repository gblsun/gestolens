---
tags: [modulo]
arquivo: gestos/classificadores/rosto.py
---
# rosto

`gestos/classificadores/rosto.py` · voltar ao [[Início]]

Classificadores de rosto.

- `classificar_boca(lm, aspecto)` → (rótulo, proporção) — [[Ex4 - Boca aberta e fechada]]
- `classificar_direcao_rosto(lm)` → (rótulo, desvio) — [[Ex5 - Direção do rosto]]
- `estimar_pose(matriz)` → (yaw, pitch, roll) em graus — [[Pose facial]]

Índices usados em [[Landmarks do rosto]]. Chamado por [[analise]].
