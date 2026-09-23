---
tags: [modulo]
arquivo: gestos/pipeline.py
---
# pipeline

`gestos/pipeline.py` · voltar ao [[Início]]

Laço principal por vídeo: [[fonte_video]] → redimensiona para 720 px de largura → (espelha) → [[deteccao]] → [[analise]] → [[registro]] → [[desenho]] → janela / `VideoWriter`.

`OpcoesPipeline(mostrar_janela, salvar_video, espelhar, pasta_saidas)`. Janela com título **GestoLens**. Esc pula o vídeo (ou encerra a webcam); q levanta `Interrompido`. Chamado por [[exercicio_mediapipe]].
