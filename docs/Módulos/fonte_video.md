---
tags: [modulo]
arquivo: gestos/fonte_video.py
---
# fonte_video

`gestos/fonte_video.py` · voltar ao [[Início]]

Aquisição de quadros.

- `listar_videos(entrada)` — aceita arquivo ou pasta (`.mov .mp4 .avi .mkv .m4v`).
- `FonteVideo(origem)` — abre arquivo ou webcam (índice inteiro); aplica a rotação dos metadados dos `.MOV` de celular (`CAP_PROP_ORIENTATION_AUTO`).
- `quadros()` — gera `Quadro(indice, timestamp_ms, imagem)` com timestamps **estritamente crescentes**, exigência do modo VIDEO de [[MediaPipe Tasks]]:
  - arquivo: `índice / fps` (determinístico);
  - **webcam**: relógio (`time.monotonic`), porque o fps real da câmera varia.
- `eh_webcam` indica fonte ao vivo; na webcam `total_quadros` é 0.

Consumido por [[pipeline]].
