---
tags: [avaliacao]
---
# Como preencher rotulos.csv

Arquivo na raiz, lido por [[avaliacao]]. Uma linha por trecho contínuo com um único rótulo esperado:

```csv
video,inicio_s,fim_s,exercicio,lado,rotulo_esperado
IMG_7459,1.5,2.5,ex3,direita,cima
IMG_7457,0.0,2.0,ex2,,5
```

| Coluna | Valores |
|---|---|
| `video` | nome do arquivo sem extensão |
| `inicio_s`, `fim_s` | segundos (o tempo aparece no topo do vídeo anotado) |
| `exercicio` | `ex1` … `ex5` |
| `lado` | `esquerda`, `direita` ou vazio (qualquer mão); ignorado em ex4/ex5 |
| `rotulo_esperado` | apelido ou rótulo completo |

Apelidos: **ex1** aberta/fechada/parcial · **ex2** 0–5 · **ex3** cima/baixo/outro · **ex4** aberta/fechada · **ex5** frente/esquerda/direita (da imagem).

Linhas iniciadas com `#` são ignoradas. Depois rode `python exercicio_mediapipe.py --so-avaliar`. Ver [[Protocolo de testes]].

Voltar ao [[Início]].
