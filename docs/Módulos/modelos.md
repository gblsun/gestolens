---
tags: [modulo]
arquivo: gestos/modelos.py
---
# modelos

`gestos/modelos.py` · voltar ao [[Início]]

`garantir_modelo(nome)` baixa `hand_landmarker.task` e `face_landmarker.task` do Google Storage para `modelos/` na primeira execução e devolve o caminho. Usado por [[deteccao]]. Ver [[MediaPipe Tasks]].
