---
tags: [modulo]
arquivo: exercicio_mediapipe.py
---
# exercicio_mediapipe

`exercicio_mediapipe.py` · voltar ao [[Início]]

Ponto de entrada do **GestoLens** (menu + CLI). Sem argumentos, em um terminal, abre um menu: **1) webcam**, **2) todos os vídeos**, **3) escolher um vídeo** (`escolher_fonte_interativa`). Uma fonte que não abre (câmera ausente, arquivo corrompido) gera uma mensagem de erro e o lote segue.

Fluxo: Lê os argumentos, lista os vídeos com [[fonte_video]], chama o [[pipeline]] para cada um, grava o resumo e as notas de [[Resultados]] via [[registro]] e, com `--avaliar`, executa a [[avaliacao]].

## Opções
`--entrada` **ou** `--webcam [i]` · `--saida` · `--sem-janela` · `--sem-video` / `--salvar-video` · `--espelhar` / `--sem-espelho` · `--avaliar [csv]` · `--so-avaliar`.

| | vídeos | webcam |
|---|---|---|
| janela | sim (`--sem-janela` desliga) | sempre |
| grava .mp4 | sim (`--sem-video` desliga) | não (`--salvar-video` liga) |
| espelha | não (`--espelhar` liga) | sim (`--sem-espelho` desliga) | Detalhes no [[README]].

## Detalhes
- Força `stdout` em UTF-8 (o console do Windows usa cp1252 e quebraria com acentos).
- `q` na janela levanta `Interrompido`; o que já foi processado é salvo mesmo assim.
