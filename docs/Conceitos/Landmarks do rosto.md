---
tags: [conceito]
---
# Landmarks do rosto

![[mapa_rosto.png]]

O Face Landmarker devolve 478 pontos (468 da malha + 10 da íris), mesma numeração do Face Mesh.

| Índice | Ponto | Uso |
|---|---|---|
| 13 / 14 | lábio interno superior / inferior | altura da boca — [[Ex4 - Boca aberta e fechada]] |
| 61 / 291 | cantos da boca | largura da boca |
| 33 / 263 | cantos externos dos olhos | centro e escala — [[Ex5 - Direção do rosto]] |
| 1 | ponta do nariz | desvio horizontal |

Além dos pontos, a matriz de transformação facial alimenta a [[Pose facial]]. Implementado em [[rosto]].

Voltar ao [[Início]].
