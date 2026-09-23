---
tags: [conceito]
---
# MediaPipe Tasks

A partir das versões recentes (aqui **1.0.1**, Python 3.14) o MediaPipe removeu a interface legada `mp.solutions` usada no código-base da proposta. O projeto usa a API **Tasks**:

| Código-base (`solutions`) | Este projeto (`tasks`) |
|---|---|
| `mp.solutions.hands.Hands` | `vision.HandLandmarker` |
| `mp.solutions.face_mesh.FaceMesh` | `vision.FaceLandmarker` |
| `hands.process(rgb)` | `detect_for_video(mp.Image, timestamp_ms)` |
| `results.multi_hand_landmarks[i].landmark` | `result.hand_landmarks[i]` (lista) |
| `drawing_utils.draw_landmarks` | desenho próprio em [[desenho]] |

**Running modes:** `IMAGE` (quadros independentes), `VIDEO` (arquivo; rastreia entre quadros, timestamps crescentes — usado aqui), `LIVE_STREAM` (assíncrono). Os modelos `.task` são baixados por [[modelos]] e carregados por [[deteccao]].

A topologia dos landmarks é a mesma do Face Mesh/Hands, então os índices da proposta continuam válidos: [[Landmarks da mão]], [[Landmarks do rosto]].

Voltar ao [[Início]].
