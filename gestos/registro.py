"""Registro das classificações: CSV por quadro, resumo por vídeo e nota no vault.

Saídas
------
- `saidas/<video>.csv`: uma linha por quadro, com as colunas de `COLUNAS`. Mãos
  ausentes aparecem como "Mao nao detectada"; valores contínuos (proporção da
  boca, desvio do nariz, diferença do polegar, pose) permitem calibrar os limiares.
- `saidas/resumo.csv`: distribuição de rótulos por vídeo, em formato longo.
- `docs/Resultados/<video>.md`: nota do Obsidian com tabelas e links para os
  exercícios. É o que liga os resultados ao grafo.

Documentação: docs/Módulos/registro.md
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

from . import config
from .analise import AnaliseQuadro
from .classificadores.maos import MAO_NAO_DETECTADA
from .classificadores.rosto import ROSTO_NAO_DETECTADO

LADOS = ("esquerda", "direita")
CAMPOS_MAO = ("dedos_bruto", "dedos", "estado", "polegar", "polegar_dif")
COLUNAS = (
    ["video", "quadro", "t_s", "maos_detectadas"]
    + [f"{lado}_{campo}" for lado in LADOS for campo in CAMPOS_MAO]
    + ["rosto_detectado", "boca", "proporcao_boca", "direcao", "desvio_nariz", "yaw", "pitch", "roll"]
)

# Campos categóricos resumidos (coluna do CSV -> nota de exercício no vault).
CAMPOS_RESUMO = {
    "esquerda_estado": "Ex1 - Mão aberta e fechada",
    "direita_estado": "Ex1 - Mão aberta e fechada",
    "esquerda_dedos": "Ex2 - Contagem de dedos",
    "direita_dedos": "Ex2 - Contagem de dedos",
    "esquerda_polegar": "Ex3 - Polegar para cima e para baixo",
    "direita_polegar": "Ex3 - Polegar para cima e para baixo",
    "boca": "Ex4 - Boca aberta e fechada",
    "direcao": "Ex5 - Direção do rosto",
}


def _fmt(valor, casas=3):
    """Formata um número com `casas` decimais; None vira texto vazio."""
    return "" if valor is None else f"{valor:.{casas}f}"


def linha_csv(nome_video: str, analise: AnaliseQuadro) -> dict:
    """Converte a análise de um quadro em uma linha do CSV.

    Parâmetros:
        nome_video: valor da coluna "video".
        analise: resultado do quadro.

    Retorna:
        Dicionário com todas as chaves de `COLUNAS`.
    """
    linha = {
        "video": nome_video,
        "quadro": analise.indice,
        "t_s": f"{analise.timestamp_ms / 1000:.3f}",
        "maos_detectadas": len(analise.maos),
    }
    por_lado = {m.lado: m for m in analise.maos}
    for lado in LADOS:
        mao = por_lado.get(lado)
        linha[f"{lado}_dedos_bruto"] = "" if mao is None else mao.dedos_bruto
        linha[f"{lado}_dedos"] = "" if mao is None else mao.dedos
        linha[f"{lado}_estado"] = MAO_NAO_DETECTADA if mao is None else mao.estado
        linha[f"{lado}_polegar"] = "" if mao is None else mao.polegar
        linha[f"{lado}_polegar_dif"] = "" if mao is None else _fmt(mao.polegar_diferenca)

    rosto = analise.rosto
    linha["rosto_detectado"] = int(rosto is not None)
    linha["boca"] = ROSTO_NAO_DETECTADO if rosto is None else rosto.boca
    linha["proporcao_boca"] = "" if rosto is None else _fmt(rosto.proporcao_boca)
    linha["direcao"] = ROSTO_NAO_DETECTADO if rosto is None else rosto.direcao
    linha["desvio_nariz"] = "" if rosto is None else _fmt(rosto.desvio_nariz)
    for eixo in ("yaw", "pitch", "roll"):
        linha[eixo] = "" if rosto is None else _fmt(getattr(rosto, eixo), 1)
    return linha


class RegistroVideo:
    """Escreve o CSV por quadro de um vídeo e acumula estatísticas para o resumo."""

    def __init__(self, nome_video: str, pasta_saida: Path):
        """Parâmetros:
            nome_video: nome usado no arquivo e na coluna "video".
            pasta_saida: pasta onde o CSV é criado (criada se não existir).
        """
        self.nome = nome_video
        self.caminho = pasta_saida / f"{nome_video}.csv"
        pasta_saida.mkdir(parents=True, exist_ok=True)
        self._arquivo = open(self.caminho, "w", newline="", encoding="utf-8")
        self._escritor = csv.DictWriter(self._arquivo, fieldnames=COLUNAS)
        self._escritor.writeheader()
        self.total = 0
        self.com_mao = 0
        self.com_rosto = 0
        self.contagens: dict[str, Counter] = defaultdict(Counter)
        self.proporcoes: list[float] = []

    def adicionar(self, analise: AnaliseQuadro) -> None:
        """Grava a linha do quadro e atualiza as contagens."""
        linha = linha_csv(self.nome, analise)
        self._escritor.writerow(linha)
        self.total += 1
        self.com_mao += bool(analise.maos)
        self.com_rosto += analise.rosto is not None
        for campo in CAMPOS_RESUMO:
            valor = linha[campo]
            if valor != "":
                self.contagens[campo][str(valor)] += 1
        if analise.rosto is not None:
            self.proporcoes.append(analise.rosto.proporcao_boca)

    def fechar(self) -> None:
        """Fecha o arquivo CSV."""
        self._arquivo.close()

    def linhas_resumo(self) -> list[dict]:
        """Resumo em formato longo: uma linha por (campo, rótulo)."""
        linhas = []
        for campo, contagem in self.contagens.items():
            for rotulo, quantidade in contagem.most_common():
                linhas.append({
                    "video": self.nome,
                    "campo": campo,
                    "rotulo": rotulo,
                    "quadros": quantidade,
                    "percentual": f"{100 * quantidade / max(self.total, 1):.1f}",
                })
        return linhas


def salvar_resumo(registros: list[RegistroVideo], pasta_saida: Path) -> Path:
    """Atualiza saidas/resumo.csv com a distribuição de rótulos dos vídeos processados.

    Linhas de vídeos que não foram processados agora são mantidas, então rodar
    um único vídeo não apaga o resumo dos demais.

    Parâmetros:
        registros: registros dos vídeos processados nesta execução.
        pasta_saida: pasta do resumo.

    Retorna:
        Caminho de `resumo.csv`.
    """
    caminho = pasta_saida / "resumo.csv"
    colunas = ["video", "campo", "rotulo", "quadros", "percentual"]
    processados = {r.nome for r in registros}
    anteriores = []
    if caminho.exists():
        with open(caminho, newline="", encoding="utf-8") as arquivo:
            anteriores = [l for l in csv.DictReader(arquivo) if l["video"] not in processados]
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(anteriores)
        for registro in registros:
            escritor.writerows(registro.linhas_resumo())
    return caminho


def gerar_nota_resultado(registro: RegistroVideo, pasta_vault: Path = config.PASTA_RESULTADOS_VAULT) -> Path:
    """Cria docs/Resultados/<video>.md com o resumo, ligado às notas dos exercícios."""
    pasta_vault.mkdir(parents=True, exist_ok=True)
    total = max(registro.total, 1)
    media_boca = sum(registro.proporcoes) / len(registro.proporcoes) if registro.proporcoes else None
    partes = [
        "---",
        "tags: [resultado]",
        f"video: {registro.nome}",
        "---",
        f"# Resultado — {registro.nome}",
        "",
        "Gerado automaticamente por [[registro]] ao rodar o [[pipeline]]. "
        "Veja também [[Resultados]] e o [[Protocolo de testes]].",
        "",
        f"- Quadros processados: **{registro.total}**",
        f"- Quadros com mão detectada: **{100 * registro.com_mao / total:.1f}%**",
        f"- Quadros com rosto detectado: **{100 * registro.com_rosto / total:.1f}%**",
        f"- Proporção média da boca: **{media_boca:.3f}**" if media_boca is not None else "- Proporção média da boca: —",
        f"- CSV por quadro: `saidas/{registro.nome}.csv`",
        "",
    ]
    for campo, nota in CAMPOS_RESUMO.items():
        contagem = registro.contagens.get(campo)
        if not contagem:
            continue
        partes += [f"## {campo} — [[{nota}]]", "", "| Rótulo | Quadros | % |", "|---|---:|---:|"]
        for rotulo, quantidade in contagem.most_common():
            partes.append(f"| {rotulo} | {quantidade} | {100 * quantidade / total:.1f} |")
        partes.append("")

    caminho = pasta_vault / f"{registro.nome}.md"
    caminho.write_text("\n".join(partes), encoding="utf-8")
    return caminho
