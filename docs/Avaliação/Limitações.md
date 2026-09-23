---
tags: [avaliacao]
---
# Limitações

- **Regras 2D:** landmarks projetados; escorço (dedo apontando para a câmera) e perfis quebram as comparações. [[Ex2 - Contagem de dedos]]
- **Oclusão e iluminação:** o modelo "completa" pontos ocultos; mão cortada na borda gera contagens erradas.
- **Diferenças individuais:** barba e bigode afetam os lábios ([[Ex4 - Boca aberta e fechada]]); o formato do rosto afeta o desvio do nariz.
- **Limiares não universais:** dependem de câmera, distância e pessoa — [[Limiares e calibração]].
- **Lateralidade** pode trocar com o dorso da mão voltado para a câmera — [[Espelhamento]].
- **Suavização** introduz atraso — [[Suavização temporal]].
- **Desempenho:** mão + rosto no CPU a 720 px processam abaixo do tempo real para vídeos de 60 fps.
- **Webcam:** o desempenho depende da CPU; abaixo de ~10 fps a suavização de 7 quadros fica lenta, então reduza `JANELA_SUAVIZACAO`.
- Ética e dados: [[Privacidade]].

Voltar ao [[Início]].
