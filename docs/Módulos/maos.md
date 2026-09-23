---
tags: [modulo]
arquivo: gestos/classificadores/maos.py
---
# maos

`gestos/classificadores/maos.py` · voltar ao [[Início]]

Classificadores de mão.

- `contar_dedos(lm, aspecto)` → 0–5 — [[Ex2 - Contagem de dedos]]
- `classificar_mao(qtd)` → aberta/fechada/parcial/não detectada — [[Ex1 - Mão aberta e fechada]]
- `classificar_polegar(lm, aspecto)` → (rótulo, diferença) — [[Ex3 - Polegar para cima e para baixo]]
- `polegar_estendido(lm, aspecto)` — regra de distância 4–5 vs 3–5.

Depende de [[geometria]] e [[config]]; chamado por [[analise]].
