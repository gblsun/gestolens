---
tags: [modulo]
arquivo: gestos/deteccao.py
---
# deteccao

`gestos/deteccao.py` · voltar ao [[Início]]

`Detector(imagem_espelhada)` encapsula `HandLandmarker` (até 2 mãos) e `FaceLandmarker` (1 rosto, com matriz de transformação) em modo **VIDEO** de [[MediaPipe Tasks]].

`processar(imagem_bgr, timestamp_ms) → ResultadoDeteccao` com:
- `maos`: lista de `MaoDetectada(landmarks, lado, confianca_lado)` — ver [[Landmarks da mão]].
- `rosto`: 478 landmarks — ver [[Landmarks do rosto]].
- `matriz_rosto`: 4×4 usada em [[Pose facial]].

## Detalhes
- **Lateralidade:** o MediaPipe supõe imagem espelhada; sem `--espelhar` o rótulo é invertido para refletir a mão real da pessoa. Ver [[Espelhamento]].
- Modelos passados como **bytes** (`model_asset_buffer`): o MediaPipe não abre caminhos com acentos no Windows ("expressões").
- Um `Detector` por vídeo, pois os timestamps recomeçam em zero.
