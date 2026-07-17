# =============================================================================
# config.py
# Configurações globais compartilhadas por todo o jogo: dimensões da janela,
# taxa de quadros e paletas de cores usadas na interface (HUD, textos, etc.).
# =============================================================================

# Dimensões da janela do jogo (em pixels)
WIDTH = 600
HEIGHT = 800

# Quadros por segundo (limita o clock do loop principal em core/game.py)
FPS = 60

# Cores básicas em RGB, reutilizadas em várias telas e HUDs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)


# Cor associada a cada tipo de arma do jogador, usada para desenhar os
# indicadores de munição no HUD (ver Player.draw_weapons_hud)
WEAPON_COLORS = {
    "BasicWeapon": (0, 255, 0),      # verde
    "DoubleShot": (0, 0, 255),       # azul
    "TripolShot": (128, 0, 128),     # roxo
    "HeavyLaser": (255, 0, 0),       # vermelho
    "QuadShot": (0, 220, 150),       # verde-água
    "HomingShot": (255, 60, 200),    # magenta
}
