---
tags: [avaliacao]
---
# Protocolo de testes

Baseado na seção *Avaliação e cuidados* da proposta.

1. **Diversidade:** mais de uma pessoa, distâncias diferentes, variações de iluminação.
2. **Separação:** vídeos (ou trechos) usados para [[Limiares e calibração|calibrar]] ≠ vídeos usados para avaliar.
3. **Registro:** acertos, erros e situações em que o sistema deve responder "indefinido" — contabilizados por [[avaliacao]].
4. **Apresentação:** tabela de condições e resultados → [[Avaliação]] e notas por vídeo em [[Resultados]]; imagens a partir de `saidas/*_anotado.mp4`.

## Fluxo
```
python exercicio_mediapipe.py --sem-janela   # gera CSVs e vídeos anotados
# assistir aos anotados e preencher rotulos.csv
python exercicio_mediapipe.py --so-avaliar   # gera Avaliação.md
```

## Tabela de condições (preencher)
| Vídeo | Conteúdo observado | Exercícios | Pessoa | Distância | Iluminação | Uso |
|---|---|---|---|---|---|---|
| [[IMG_7457]] | mão aberta/fechada, contagem com as duas mãos | Ex1, Ex2 | P1 | braço estendido | interna, fluorescente | |
| [[IMG_7458]] | contagem de dedos / mão semiaberta | Ex1, Ex2 | P1 | braço estendido | interna, fluorescente | |
| [[IMG_7459]] | polegar para cima e para baixo | Ex3 | P1 | braço estendido | interna, fluorescente | |
| [[IMG_7460]] | boca aberta e fechada (sem mãos) | Ex4 | P1 | perto / longe | interna, fluorescente | |
| [[IMG_7461]] | rosto de frente, esquerda, direita, cima | Ex5 + pose | P1 | braço estendido | interna, fluorescente | |

Conteúdo identificado a partir dos vídeos anotados; confirme e complete as colunas. Há só uma pessoa: o item 1 do protocolo (mais de uma pessoa) ainda falta.

Métricas: acurácia sobre quadros decididos + taxa de indefinidos (cobertura). Ver [[Limitações]].

Voltar ao [[Início]].
