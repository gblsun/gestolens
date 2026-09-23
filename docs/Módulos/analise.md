---
tags: [modulo]
arquivo: gestos/analise.py
---
# analise

`gestos/analise.py` · voltar ao [[Início]]

Liga detecção e regras. `Analisador(aspecto)` mantém um [[suavizacao|FiltroModa]] por mão (chave = lado) e `analisar(indice, ts, deteccao)` devolve `AnaliseQuadro` com:

- `AnaliseMao`: lado, dedos brutos/suavizados, estado, polegar (suavizado), diferença do polegar.
- `AnaliseRosto`: boca, proporção, direção, desvio, yaw/pitch/roll.

Chama [[maos]] e [[rosto]]; entrega para [[desenho]] e [[registro]]. Orquestrado pelo [[pipeline]].
