---
tags: [conceito]
---
# Suavização temporal

Classificações quadro a quadro oscilam (ruído dos landmarks, poses no limite). [[suavizacao]] aplica a **moda** dos últimos 7 quadros (~0,12 s a 60 fps) por mão.

![[grafico_suavizacao.png]]

- Prós: remove oscilações de 1–3 quadros; mantém rótulos discretos (média não faria sentido para "Polegar para cima").
- Contras: atraso de ~meia janela nas transições.
- Alternativas: histerese (limiares diferentes para entrar e sair de um estado), média móvel exponencial nos valores contínuos antes do limiar.

Quando a mão desaparece o histórico é descartado ([[Ex1 - Mão aberta e fechada]]). Aplicada em [[Ex2 - Contagem de dedos]] e [[Ex3 - Polegar para cima e para baixo]].

Voltar ao [[Início]].
