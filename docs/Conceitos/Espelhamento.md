---
tags: [conceito]
---
# Espelhamento

Webcams costumam ser exibidas **espelhadas** (`cv2.flip(img, 1)`) para parecerem um espelho. No GestoLens a **webcam é espelhada por padrão** (`--sem-espelho` desliga) e os **vídeos gravados não** (`--espelhar` liga), porque o celular grava sem espelhar.

Efeitos:
- **Esquerda/direita na imagem** trocam de lado → os rótulos de [[Ex5 - Direção do rosto]] dizem "da imagem" para não depender disso.
- **Lateralidade da mão:** o MediaPipe assume imagem espelhada; em imagem não espelhada o rótulo vem trocado. [[deteccao]] corrige para refletir a mão real da pessoa.
- Regras que só usam y ou distâncias (dedos, polegar cima/baixo, boca) **não** são afetadas.
- Uma regra horizontal para o polegar (`x[4] < x[3]`, comum em tutoriais) **seria** afetada — por isso o projeto usa a regra de distância ([[Ex2 - Contagem de dedos]]).

Questão ligada: [[Ex3 - Polegar para cima e para baixo]].

Voltar ao [[Início]].
