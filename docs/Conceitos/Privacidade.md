---
tags: [conceito]
---
# Privacidade

Da proposta: não gravar nem compartilhar imagens de pessoas sem consentimento; preferir processamento local; evitar armazenar vídeo sem necessidade.

No projeto:
- Todo o processamento é local (os modelos são baixados uma vez; nenhum quadro é enviado).
- **Webcam não grava vídeo por padrão.** Só com `--salvar-video`. Os CSVs guardam apenas rótulos e números.
- Para vídeos gravados, `--sem-video` desliga a gravação dos vídeos anotados.
- `saidas/` e `modelos/` estão no `.gitignore`.
- Os vídeos de teste em `Vídeos Exercício mediapipe/` são versionados **por decisão do autor**, que é a pessoa filmada. Antes de adicionar vídeos de outras pessoas, peça consentimento.

Ver [[Limitações]].

Voltar ao [[Início]].
