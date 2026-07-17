"""
Persistência simples do recorde (high score) do jogo em um arquivo de
texto na raiz do projeto (ou ao lado do executável, quando empacotado).
"""

import os
from core.app_paths import get_app_dir

HIGH_SCORE_FILE = os.path.join(get_app_dir(), "highscore.txt")


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
