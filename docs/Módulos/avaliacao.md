---
tags: [modulo]
arquivo: gestos/avaliacao.py
---
# avaliacao

`gestos/avaliacao.py` · voltar ao [[Início]]

Implementa o [[Protocolo de testes]]: cruza os CSVs de [[registro]] com o gabarito `rotulos.csv` ([[Como preencher rotulos.csv]]).

Para cada quadro dentro de um trecho rotulado:
- **acerto** — alguma mão (ou a mão do lado indicado) tem o rótulo esperado;
- **indefinido** — todas as previsões são indefinidas/não detectadas;
- **erro** — caso contrário (registrado na matriz de confusões).

Gera `saidas/avaliacao.csv` e [[Avaliação]] (nota em Resultados) com acurácia sobre quadros decididos.
