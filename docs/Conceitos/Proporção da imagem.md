---
tags: [conceito]
---
# Proporção da imagem

![[aspecto.png]]

Landmarks são normalizados separadamente: x pela largura, y pela altura. Em vídeo 1080×1920 (retrato), 0,1 em x = 108 px e 0,1 em y = 192 px. Distâncias calculadas direto em coordenadas normalizadas ficam **distorcidas**.

[[geometria]] → `distancia(a, b, aspecto)` multiplica Δx por `largura/altura`, medindo tudo em unidades da altura. O [[pipeline]] calcula `aspecto` no primeiro quadro e o repassa via [[analise]].

Impacto: a proporção da boca ([[Ex4 - Boca aberta e fechada]]) sem correção sairia ~1,8× maior em retrato — o limiar 0.15 pensado para webcam paisagem não valeria. O desvio do nariz ([[Ex5 - Direção do rosto]]) é razão de duas medidas em x e não precisa da correção.

Voltar ao [[Início]].
