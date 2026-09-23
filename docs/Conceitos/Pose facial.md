---
tags: [conceito]
---
# Pose facial

Extensão do [[Ex5 - Direção do rosto]]. O Face Landmarker com `output_facial_transformation_matrixes=True` devolve uma matriz 4×4 que leva um rosto canônico 3D ao espaço da câmera. O bloco 3×3 é a rotação R.

[[rosto]] → `estimar_pose` decompõe R em:
- **yaw** (girar a cabeça para os lados) = atan2(R02, R22)
- **pitch** (olhar para cima/baixo) = asin(−R12)
- **roll** (inclinar a cabeça para o ombro) = atan2(R10, R11)

![[grafico_direcao.png]]

Usa o rosto inteiro (ajuste do modelo 3D), por isso é mais robusto que o desvio do nariz. Os **sinais** dependem da convenção de eixos: calibre olhando para cada lado e anote. Com `--espelhar` os sinais de yaw e roll se invertem ([[Espelhamento]]).

Voltar ao [[Início]].
