---
tags: [modulo]
arquivo: gestos/registro.py
---
# registro

`gestos/registro.py` · voltar ao [[Início]]

Persistência das classificações.

- `RegistroVideo` — grava `saidas/<video>.csv` (uma linha por quadro, colunas `esquerda_*`, `direita_*`, boca, direção, pose) e acumula contagens.
- `salvar_resumo` — `saidas/resumo.csv` em formato longo (video, campo, rótulo, quadros, %). Atualiza só os vídeos processados; os demais são preservados.
- `gerar_nota_resultado` — cria `docs/Resultados/<video>.md` ligada aos exercícios, alimentando o grafo. Ver [[Resultados]].

Entrada da [[avaliacao]].
