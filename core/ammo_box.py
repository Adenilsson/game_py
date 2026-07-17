"""
Caixas de munição que caem periodicamente durante a partida e
recarregam a munição de um tipo específico de arma do jogador ao serem
tocadas. Cada cor de caixa corresponde a uma arma (ver
`AMMO_BOX_WEAPON_MAP`), seguindo a mesma paleta de `config.WEAPON_COLORS`
usada no HUD — para adicionar um novo tipo, basta soltar a imagem
"municao_<cor>.png" em `assets/imagens/extras/` e cadastrar a cor nesse
mapeamento.
"""

import os
import random
import pygame
from config import WIDTH, HEIGHT

AMMO_BOX_DIR = "assets/imagens/extras"

# Cor da caixa (usada no nome do arquivo "municao_<cor>.png") -> nome da
# classe de arma que ela recarrega. Acompanha as cores de
# `config.WEAPON_COLORS` para cada arma, para ficar intuitivo.
AMMO_BOX_WEAPON_MAP = {
    "blue": "DoubleShot",
    "red": "HeavyLaser",
    # Quando novas imagens forem adicionadas (ex.: "municao_purple.png"
    # para TripolShot, "municao_teal.png" para QuadShot, "municao_pink.png"
    # para HomingShot), basta cadastrar a cor aqui — nenhuma outra
    # mudança é necessária.
}


class AmmoBox(pygame.sprite.Sprite):
    """Caixa de munição de uma arma específica; cai lentamente pela tela
    e recarrega a munição correspondente do jogador que encostar nela
    antes que ela saia da tela por baixo."""

    _image_cache = {}

    @classmethod
    def _get_image(cls, color):
        """Carrega e escala a imagem de cada cor uma única vez,
        reaproveitada por todas as caixas dessa cor."""
        if color not in cls._image_cache:
            path = os.path.join(AMMO_BOX_DIR, f"municao_{color}.png")
            image = pygame.image.load(path).convert_alpha()
            cls._image_cache[color] = pygame.transform.scale(image, (46, 55))
        return cls._image_cache[color]

    def __init__(self, color):
        super().__init__()
        self.color = color
        self.weapon_name = AMMO_BOX_WEAPON_MAP[color]
        self.image = self._get_image(color)
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40), -40))
        self.speed_y = 2

    def update(self):
        """Desce lentamente; remove-se sozinha quando sai da tela por
        baixo sem ter sido coletada."""
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()


def available_ammo_colors():
    """Lista as cores de caixa de munição que têm tanto imagem em
    `assets/imagens/extras/` quanto uma arma correspondente cadastrada
    em `AMMO_BOX_WEAPON_MAP`. Uma imagem sem entrada no mapeamento (ou
    uma entrada sem imagem correspondente ainda) é ignorada."""
    if not os.path.isdir(AMMO_BOX_DIR):
        return []
    colors = []
    for filename in os.listdir(AMMO_BOX_DIR):
        if filename.startswith("municao_") and filename.endswith(".png"):
            color = filename[len("municao_"):-len(".png")]
            if color in AMMO_BOX_WEAPON_MAP:
                colors.append(color)
    return colors
