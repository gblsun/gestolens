---
tags: [exercicio]
exercicio: 2
---
# Ex2 — Contagem da quantidade de dedos

**Objetivo:** exibir continuamente um número de 0 a 5 para cada mão detectada.

![[ex2_dedos.gif|260]]

![[regra_dedos.png]]

![[grafico_suavizacao.png]]

## Regra implementada
[[maos]] → `contar_dedos(lm, aspecto)` = dedos longos estendidos + polegar estendido.

**Dedos longos** (indicador, médio, anelar, mínimo — pares ponta/PIP 8/6, 12/10, 16/14, 20/18), duas regras em [[geometria]] escolhidas por `REGRA_DEDOS` em [[config]]:
- `"vertical"` (código-base): `lm[ponta].y < lm[pip].y`. Só funciona com a mão em pé.
- `"distancia"` (padrão): ponta mais longe do punho (0) que a PIP. Invariante à rotação da mão no plano.

**Polegar:** `dist(4, 5) > dist(3, 5) × 1.15` — ponta do polegar longe da base do indicador. Não depende de lado nem de [[Espelhamento]].

As distâncias são corrigidas pela [[Proporção da imagem]] (vídeos em retrato 1080×1920).

## Suavização (extensão)
[[suavizacao]] aplica a **moda dos últimos 7 quadros** (`JANELA_SUAVIZACAO`) por mão. O CSV guarda `dedos_bruto` e `dedos` (suavizado) para comparar. Ver [[Suavização temporal]].

## Tarefas da proposta → onde estão
- [x] Testar 0 a 5 com a palma de frente → rotular trechos em [[Como preencher rotulos.csv]] com `ex2`.
- [ ] Registrar ≥ 3 contagens incorretas e a pose → preencher a partir de [[Avaliação]] (tabela de erros) e do vídeo anotado.
- [x] Orientação, oclusão e espelhamento → discutidos abaixo e em [[Espelhamento]].

## Casos de erro esperados
1. Mão invertida com regra vertical → dedos dobrados contados (corrigido com a regra por distância).
2. Polegar dobrado sobre a palma em mão pequena na imagem → razão 1.15 fica no limite e oscila.
3. Dedo apontando para a câmera (escorço) → ponta e PIP quase coincidem em 2D.
4. Dedos colados lateralmente (mão de perfil) → landmarks sobrepostos.

Relacionados: [[Ex1 - Mão aberta e fechada]], [[Landmarks da mão]].
