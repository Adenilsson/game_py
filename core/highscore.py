"""
Persistência simples do recorde (high score) do jogo em um arquivo de
texto na raiz do projeto.
"""

import os

HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "highscore.txt")


def load_high_score():
    """Lê o recorde salvo em disco. Retorna 0 se o arquivo ainda não
    existir ou tiver conteúdo inválido."""
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    """Salva o recorde em disco, sobrescrevendo o valor anterior."""
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))
