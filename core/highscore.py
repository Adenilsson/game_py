"""
Persistência do placar (top 10 pontuações, com nome do jogador) em um
arquivo JSON na pasta do jogo (ver `core/app_paths.py`).
"""

import json
import os
from core.app_paths import get_app_dir

LEADERBOARD_FILE = os.path.join(get_app_dir(), "leaderboard.json")
LEGACY_HIGH_SCORE_FILE = os.path.join(get_app_dir(), "highscore.txt")
PLAYER_BESTS_FILE = os.path.join(get_app_dir(), "player_bests.json")
MAX_ENTRIES = 10


def _migrate_legacy_high_score():
    """Versões antigas guardavam só um número em `highscore.txt`. Se o
    placar novo ainda não existir, aproveita esse valor como primeira
    entrada (em vez de zerar o recorde de quem já jogava antes)."""
    try:
        with open(LEGACY_HIGH_SCORE_FILE, "r") as f:
            score = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return []
    if score <= 0:
        return []
    return [{"name": "Jogador", "score": score}]


def load_leaderboard():
    """Lê o placar salvo em disco: lista de até 10 entradas
    `(nome, pontuação)`, uma por jogador (a maior pontuação dele), da
    maior para a menor. Retorna lista vazia se ainda não existir
    nenhuma pontuação registrada.

    Deduplica por nome mesmo que o arquivo em disco tenha entradas
    repetidas (de partidas jogadas antes dessa checagem existir): o
    mesmo jogador nunca ocupa duas posições do placar, só a sua maior
    pontuação conta."""
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            raw_entries = json.load(f)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        raw_entries = _migrate_legacy_high_score()

    best_by_name = {}
    for entry in raw_entries:
        try:
            name = str(entry["name"])
            score = int(entry["score"])
        except (KeyError, TypeError, ValueError):
            continue
        best_by_name[name] = max(best_by_name.get(name, 0), score)

    entries = sorted(best_by_name.items(), key=lambda e: e[1], reverse=True)
    return entries[:MAX_ENTRIES]


def save_leaderboard(entries):
    """Salva o placar em disco, mantendo só as 10 maiores pontuações."""
    top_entries = sorted(entries, key=lambda e: e[1], reverse=True)[:MAX_ENTRIES]
    data = [{"name": name, "score": score} for name, score in top_entries]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return top_entries


def submit_score(name, score):
    """Registra a pontuação de uma partida no placar (se ela entrar
    entre as 10 maiores) e retorna o placar atualizado, já ordenado da
    maior para a menor pontuação. Cada jogador ocupa uma única posição
    do placar: se ele já tinha uma pontuação registrada, só é
    atualizada quando a nova for maior — nunca cria uma entrada
    duplicada para o mesmo nome."""
    name = (name or "Jogador").strip() or "Jogador"
    best_by_name = dict(load_leaderboard())
    best_by_name[name] = max(best_by_name.get(name, 0), score)
    return save_leaderboard(list(best_by_name.items()))


def load_high_score():
    """Maior pontuação já registrada no placar (0 se ainda não houver
    nenhuma). Usado para o "Recorde" geral exibido durante a partida e
    na tela de game over."""
    entries = load_leaderboard()
    return entries[0][1] if entries else 0


def _load_player_bests():
    """Lê o dicionário `{nome: melhor pontuação}` salvo em disco.
    Retorna um dicionário vazio se o arquivo ainda não existir ou
    estiver corrompido."""
    try:
        with open(PLAYER_BESTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {str(name): int(score) for name, score in data.items()}
    except (FileNotFoundError, ValueError, json.JSONDecodeError, AttributeError):
        return {}


def _best_score_in_leaderboard(name):
    """Maior pontuação já registrada com esse nome no placar (top 10).
    Serve de respaldo para reconhecer jogadores que pontuaram antes de
    `player_bests.json` existir (ou cuja entrada em `player_bests.json`
    tenha se perdido por algum motivo) — sem isso, digitar um nome que
    já apareceu no placar não desbloquearia as naves que ele já
    conquistou."""
    return max((score for entry_name, score in load_leaderboard() if entry_name == name), default=0)


def get_player_best(name):
    """Retorna a maior pontuação já alcançada pelo jogador com esse
    nome (0 se o nome estiver vazio ou nunca tiver pontuado): o maior
    valor entre o registrado em `player_bests.json` e o encontrado no
    placar (top 10), para reconhecer também pontuações antigas que
    ainda não tinham sido migradas. Usado pelo sistema de desbloqueio
    de naves em `StartScreen`: cada nave liberada fica disponível
    apenas para quem realmente atingiu a pontuação necessária, não
    para qualquer jogador."""
    name = (name or "").strip()
    if not name:
        return 0
    return max(_load_player_bests().get(name, 0), _best_score_in_leaderboard(name))


def record_player_score(name, score):
    """Atualiza a melhor pontuação do jogador com esse nome, se a
    pontuação desta partida (ou alguma já registrada no placar) for
    maior que a anterior. Retorna a melhor pontuação (nova ou antiga)
    desse jogador."""
    name = (name or "").strip()
    if not name:
        return 0
    bests = _load_player_bests()
    best = max(bests.get(name, 0), _best_score_in_leaderboard(name), score)
    bests[name] = best
    with open(PLAYER_BESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(bests, f, ensure_ascii=False, indent=2)
    return best
