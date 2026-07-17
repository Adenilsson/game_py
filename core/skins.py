"""
Descoberta e ordenação das skins de nave do jogador disponíveis em
`assets/imagens/naves/player/`, e o cálculo do "tier" (nível) de cada
uma — usado tanto pelo sistema de desbloqueio por recorde (`StartScreen`)
quanto pelo arsenal de armas do jogador (`core/weapon_loadouts.py`).
"""

import os
import re

PLAYER_SKINS_DIR = "assets/imagens/naves/player"


def skin_sort_key(name):
    """Ordena as skins pelo número ao final do nome da pasta (ex.:
    "player_1" -> 1, "aviao_5" -> 5), em vez de ordem alfabética, para
    que a ordem de desbloqueio/arsenal siga a numeração e não o nome.
    Pastas sem número ao final vão para o fim, em ordem alfabética."""
    match = re.search(r"(\d+)$", name)
    if match:
        return (0, int(match.group(1)), name)
    return (1, 0, name)


def discover_skins():
    """Lista as subpastas de naves disponíveis em `PLAYER_SKINS_DIR`,
    ordenadas por `skin_sort_key`. Se a pasta não existir ou estiver
    vazia, retorna apenas "player_1" como padrão."""
    if not os.path.isdir(PLAYER_SKINS_DIR):
        return ["player_1"]
    skins = sorted(
        (name for name in os.listdir(PLAYER_SKINS_DIR)
         if os.path.isdir(os.path.join(PLAYER_SKINS_DIR, name))),
        key=skin_sort_key,
    )
    return skins or ["player_1"]


def skin_tier(skin):
    """Retorna a posição (0-indexada) da skin na lista ordenada de naves
    disponíveis: 0 é a nave inicial (arsenal mais simples), e cada tier
    seguinte tem mais opções de arma. Skins desconhecidas caem no tier 0."""
    skins = discover_skins()
    if skin in skins:
        return skins.index(skin)
    return 0
