---
tags: [modulo]
arquivo: gestos/desenho.py
---
# desenho

`gestos/desenho.py` · voltar ao [[Início]]

Sobreposição visual com OpenCV (sem `drawing_utils`, ausente nas versões recentes).

- `desenhar_mao` — 21 pontos + 21 conexões; cor por lado (verde = direita, laranja = esquerda).
- `desenhar_rosto` — só os pontos usados nas regras (1, 13, 14, 33, 61, 263, 291).
- `desenhar_analise` — painel com todas as classificações, proporção da boca, desvio do nariz e yaw/pitch/roll; "Mao nao detectada"/"Rosto nao detectado" quando ausentes.

Textos sem acento porque `cv2.putText` não renderiza Unicode.
