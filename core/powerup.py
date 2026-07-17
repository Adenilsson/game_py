"""
Itens que caem periodicamente durante a partida e dão bônus ao jogador
que encostar neles. Por enquanto o único tipo é a caixa de vida extra,
mas a estrutura (classe própria + grupo dedicado em `Game`) permite
adicionar outros bônus no futuro.
"""

import random
import pygame
from config import WIDTH, HEIGHT

LIFE_BOX_IMAGE_PATH = "assets/imagens/extras/vida_1.png"


class LifeBox(pygame.sprite.Sprite):
    """Caixa com paraquedas que desce lentamente pela tela a partir do
    topo; concede uma vida extra ao jogador que encostar nela antes que
    ela saia da tela por baixo."""

    _image = None

    @classmethod
    def _get_image(cls):
        """Carrega e escala a imagem uma única vez, reaproveitada por
        todas as caixas (evita reler o arquivo do disco a cada spawn)."""
        if cls._image is None:
            image = pygame.image.load(LIFE_BOX_IMAGE_PATH).convert_alpha()
            cls._image = pygame.transform.scale(image, (50, 60))
        return cls._image

    def __init__(self):
        super().__init__()
        self.image = self._get_image()
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40), -40))
        self.speed_y = 2

    def update(self):
        """Desce lentamente; remove-se sozinha quando sai da tela por
        baixo sem ter sido coletada."""
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()
