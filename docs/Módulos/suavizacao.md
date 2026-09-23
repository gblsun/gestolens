---
tags: [modulo]
arquivo: gestos/suavizacao.py
---
# suavizacao

`gestos/suavizacao.py` · voltar ao [[Início]]

`FiltroModa(janela)` — guarda os últimos N valores por chave e devolve a **moda** (empate → valor mais recente). `limpar(chave)` descarta o histórico quando a mão some, garantindo que [[Ex1 - Mão aberta e fechada]] nunca reaproveite classificação antiga.

Extensão do [[Ex2 - Contagem de dedos]]. Ver [[Suavização temporal]]. Usado por [[analise]].
