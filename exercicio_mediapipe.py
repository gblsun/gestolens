"""GestoLens: reconhecimento de gestos e expressões em vídeos gravados ou na webcam.

Ponto de entrada (CLI). Rodando sem argumentos em um terminal, abre um menu
para escolher a fonte:

    1) Webcam (ao vivo, espelhada)
    2) Todos os vídeos gravados
    3) Escolher um vídeo

Com argumentos, o menu não aparece:

    python exercicio_mediapipe.py --webcam                 # webcam 0, espelhada, sem gravar
    python exercicio_mediapipe.py --webcam 1 --salvar-video
    python exercicio_mediapipe.py --entrada "Vídeos Exercício mediapipe"
    python exercicio_mediapipe.py --entrada "Vídeos Exercício mediapipe/IMG_7459.MOV" --sem-janela
    python exercicio_mediapipe.py --sem-janela --avaliar   # todos os vídeos + avaliação com rotulos.csv
    python exercicio_mediapipe.py --so-avaliar             # reavalia os CSVs já gerados

Teclas na janela: Esc pula para o próximo vídeo (ou encerra a webcam), q encerra tudo.

Documentação: README.md e docs/Módulos/exercicio_mediapipe.md
"""

import argparse
import sys
from pathlib import Path

import cv2

from gestos import config
from gestos.avaliacao import avaliar, gerar_relatorio
from gestos.fonte_video import listar_videos
from gestos.pipeline import Interrompido, OpcoesPipeline, processar_fonte
from gestos.registro import gerar_nota_resultado, salvar_resumo


def ler_argumentos() -> argparse.Namespace:
    """Define e lê as opções de linha de comando.

    Retorna:
        `argparse.Namespace` com as opções. `entrada` e `webcam` ficam `None`
        quando não são informadas, o que permite decidir se o menu deve aparecer.
    """
    parser = argparse.ArgumentParser(
        prog="GestoLens",
        description="Reconhecimento de gestos e expressões com MediaPipe (vídeos gravados ou webcam).",
    )
    fonte = parser.add_mutually_exclusive_group()
    fonte.add_argument("--entrada", type=Path, default=None,
                       help="arquivo de vídeo ou pasta com vídeos")
    fonte.add_argument("--webcam", type=int, nargs="?", const=0, default=None,
                       help="usa a webcam (índice opcional, padrão 0)")
    parser.add_argument("--saida", type=Path, default=config.PASTA_SAIDAS, help="pasta de saídas (padrão: saidas/)")
    parser.add_argument("--sem-janela", action="store_true", help="não abre a janela de visualização")
    parser.add_argument("--sem-video", action="store_true", help="não grava o vídeo anotado (arquivos)")
    parser.add_argument("--salvar-video", action="store_true", help="grava o vídeo anotado também na webcam")
    parser.add_argument("--espelhar", action="store_true", help="espelha os vídeos gravados (modo selfie)")
    parser.add_argument("--sem-espelho", action="store_true", help="não espelha a webcam")
    parser.add_argument("--avaliar", type=Path, nargs="?", const=config.ARQUIVO_ROTULOS, default=None,
                        help="avalia com o gabarito (padrão: rotulos.csv)")
    parser.add_argument("--so-avaliar", action="store_true", help="apenas avalia os CSVs já existentes")
    return parser.parse_args()


def _perguntar(texto: str, opcoes_validas: set[str], padrao: str) -> str:
    """Pergunta até receber uma das `opcoes_validas`. Enter devolve `padrao`."""
    while True:
        resposta = input(texto).strip() or padrao
        if resposta in opcoes_validas:
            return resposta
        print(f"  Opção inválida. Escolha entre: {', '.join(sorted(opcoes_validas))}")


def escolher_fonte_interativa() -> Path | int:
    """Menu de terminal para escolher entre webcam e vídeos gravados.

    Retorna:
        Um `int` (índice da webcam) ou um `Path` (pasta ou arquivo de vídeo).
    """
    videos = listar_videos(config.PASTA_VIDEOS) if config.PASTA_VIDEOS.exists() else []
    print("\nGestoLens — escolha a fonte de vídeo:")
    print("  1) Webcam (ao vivo, espelhada)")
    print(f"  2) Todos os vídeos gravados ({len(videos)} em '{config.PASTA_VIDEOS.name}')")
    print("  3) Escolher um vídeo")
    escolha = _perguntar("Opção [2]: ", {"1", "2", "3"}, "2")

    if escolha == "1":
        indice = _perguntar("Índice da câmera [0]: ", {str(i) for i in range(10)}, "0")
        return int(indice)
    if not videos:
        print("Nenhum vídeo encontrado; usando a webcam 0.")
        return 0
    if escolha == "2":
        return config.PASTA_VIDEOS

    for numero, video in enumerate(videos, start=1):
        print(f"  {numero}) {video.name}")
    numero = _perguntar("Vídeo [1]: ", {str(i) for i in range(1, len(videos) + 1)}, "1")
    return videos[int(numero) - 1]


def main() -> None:
    """Resolve a fonte, processa, grava o resumo e as notas e, se pedido, avalia."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # console do Windows (cp1252)
    args = ler_argumentos()

    if not args.so_avaliar:
        if args.webcam is not None:
            origem = args.webcam
        elif args.entrada is not None:
            origem = args.entrada
        elif sys.stdin.isatty():
            origem = escolher_fonte_interativa()
        else:
            origem = config.PASTA_VIDEOS

        webcam = isinstance(origem, int)
        opcoes = OpcoesPipeline(
            mostrar_janela=not args.sem_janela or webcam,  # a webcam sempre precisa de janela (Esc para sair)
            salvar_video=args.salvar_video if webcam else not args.sem_video,
            espelhar=not args.sem_espelho if webcam else args.espelhar,
            pasta_saidas=args.saida,
        )
        origens = [origem] if webcam else listar_videos(origem)

        registros = []
        try:
            for item in origens:
                try:
                    registros.append(processar_fonte(item, opcoes))
                except RuntimeError as erro:
                    # Fonte que não abre (câmera ausente, arquivo corrompido): avisa e segue.
                    print(f"Erro: {erro}")
        except Interrompido as parada:
            registros.append(parada.args[0])
            print("Processamento interrompido pelo usuário.")
        finally:
            cv2.destroyAllWindows()

        if registros:
            print(f"Resumo: {salvar_resumo(registros, opcoes.pasta_saidas)}")
            for registro in registros:
                gerar_nota_resultado(registro)
            print(f"Notas de resultado em {config.PASTA_RESULTADOS_VAULT}")

    caminho_rotulos = args.avaliar or (config.ARQUIVO_ROTULOS if args.so_avaliar else None)
    if caminho_rotulos:
        placares = avaliar(args.saida, caminho_rotulos)
        if not placares:
            print(f"Nenhum trecho rotulado em {caminho_rotulos}. Preencha o gabarito e rode novamente.")
        else:
            print(f"Avaliação: {gerar_relatorio(placares, args.saida)}")
            for ex, p in sorted(placares.items()):
                acc = "-" if p.acuracia is None else f"{100 * p.acuracia:.1f}%"
                print(f"  {ex}: {p.acertos} acertos, {p.erros} erros, {p.indefinidos} indefinidos, acurácia {acc}")


if __name__ == "__main__":
    main()
