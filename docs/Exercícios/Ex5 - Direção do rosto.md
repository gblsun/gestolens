---
tags: [exercicio]
exercicio: 5
---
# Ex5 — Direção do rosto

**Objetivo:** reconhecer se o rosto está de frente ou virado para um dos lados.

![[ex5_direcao.gif|260]]

![[regra_direcao.png]]

![[grafico_direcao.png]]

## Regra implementada
[[rosto]] → `classificar_direcao_rosto(lm)` retorna `(rótulo, desvio)`:

```
centro_x = (x[33] + x[263]) / 2        # cantos externos dos olhos
desvio   = (x[1] − centro_x) / |x[263] − x[33]|   # ponta do nariz
```

| Condição | Rótulo |
|---|---|
| `||desvio| − 0.12| ≤ 0.03` | Direcao indefinida |
| `desvio < −0.12` | Rosto virado p/ esquerda da imagem |
| `desvio > +0.12` | Rosto virado p/ direita da imagem |
| caso contrário | Rosto de frente |
| rosto ausente | Rosto nao detectado |

Os rótulos são **explícitos em relação à imagem exibida**, eliminando a ambiguidade do código-base ("um lado"/"outro lado"). A faixa indefinida (`FAIXA_INDEFINIDA_DIRECAO` em [[config]]) evita decisões perto do limiar.

## Observado nos vídeos
- [[IMG_7461]]: virar para o lado leva o desvio a −1,10 / +0,76 e o yaw a −60° / +48°, bem separados de "frente" (≈ 0).
- [[IMG_7457]] e [[IMG_7458]]: mesmo "de frente", o desvio mediano é 0,10–0,12 e o yaw ≈ 15°. O celular estava levemente de lado, e ~70% dos quadros caem na faixa indefinida. O limiar fixo depende da posição da câmera: calibre um **desvio de referência** com a pessoa olhando para a lente (ver [[Limiares e calibração]]).

## Extensão: yaw, pitch e roll
[[rosto]] → `estimar_pose(matriz)` decompõe a matriz de transformação facial do Face Landmarker em ângulos de Euler. Ver [[Pose facial]]. Exibidos no vídeo e gravados no CSV.

## Tarefas da proposta → onde estão
- [x] Calibrar olhando frente/esquerda/direita → coluna `desvio_nariz` no CSV; rotular trechos com `ex5`.
- [x] Espelhamento inverte os rótulos? → sim, por isso "da imagem"; com `--espelhar` a imagem exibida muda e os rótulos acompanham. Ver [[Espelhamento]].
- [x] Estado indefinido → landmarks ausentes ou desvio próximo ao limiar.

Relacionados: [[Landmarks do rosto]], [[Limiares e calibração]].
