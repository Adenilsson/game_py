"""
Sprites "fantasmas" usados apenas pelo cliente do modo cooperativo em
LAN: representam inimigos e projéteis que são simulados de verdade só
no host, e que o cliente apenas desenha na posição informada pelo
snapshot recebido pela rede — sem nenhuma lógica própria (sem arma, sem
IA, sem colisão). Evitam instanciar as classes reais (`Enemy`, que criaria
armas e carregaria sons à toa só para desenhar um inimigo alheio).
"""

import os
import pygame
from core.enemy import ENEMY_TINTS
from core.powerup import LIFE_BOX_IMAGE_PATH
from core.ammo_box import AMMO_BOX_DIR

ENEMY_BASE_IMAGE_PATH = "assets/imagens/naves/inimigos/aviao.png"


def _tinted(image, color):
    """Mesma lógica de tingimento usada em `core/enemy.py`, duplicada
    aqui para não acoplar este módulo a detalhes internos da classe
    Enemy além da tabela de cores (`ENEMY_TINTS`)."""
    if color is None:
        return image
    tinted_image = image.copy()
    tinted_image.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image


class EnemyGhost(pygame.sprite.Sprite):
    """Representação puramente visual de um inimigo simulado no host.
    `sync()` é chamado a cada snapshot recebido para atualizar posição e
    vida; nunca chama `update()`/lógica de combate própria."""

    _base_image = None
    _tinted_cache = {}

    @classmethod
    def _get_image(cls, enemy_type):
        if cls._base_image is None:
            image = pygame.image.load(ENEMY_BASE_IMAGE_PATH).convert_alpha()
            image = pygame.transform.scale(image, (70, 70))
            image = pygame.transform.rotate(image, 180)
            cls._base_image = image
        if enemy_type not in cls._tinted_cache:
            color = ENEMY_TINTS.get(enemy_type)
            cls._tinted_cache[enemy_type] = _tinted(cls._base_image, color)
        return cls._tinted_cache[enemy_type]

    def __init__(self, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = self._get_image(enemy_type)
        self.rect = self.image.get_rect()
        self.health = 0
        self.max_health = 1

    def sync(self, data):
        """Atualiza posição e vida a partir dos dados recebidos do host
        para este inimigo neste quadro."""
        self.rect.center = (data["x"], data["y"])
        self.health = data["health"]
        self.max_health = data["max_health"]

    def draw_shadow(self, screen):
        """Mesmo desenho de `Enemy.draw_shadow`, para que a cena do
        cliente pareça idêntica à do host."""
        shadow = pygame.Surface((40, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 200), shadow.get_rect())
        screen.blit(shadow, (self.rect.centerx - 20, self.rect.bottom + 50))

    def draw_health_bar(self, surface):
        """Mesmo desenho de `Enemy.draw_health_bar`."""
        bar_width = 40
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width if self.max_health else 0
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect)
        pygame.draw.rect(surface, (0, 255, 0), fill_rect)


class ProjectileGhost(pygame.sprite.Sprite):
    """Representação puramente visual de um projétil simulado no host:
    um retângulo colorido, recriado a cada snapshot (projéteis não
    precisam de identidade persistente entre quadros)."""

    def __init__(self, data):
        super().__init__()
        size = tuple(data["size"])
        self.image = pygame.Surface(size)
        self.image.fill(tuple(data["color"]))
        self.rect = self.image.get_rect(center=(data["x"], data["y"]))


class PowerUpGhost(pygame.sprite.Sprite):
    """Representação puramente visual de uma caixa de vida extra
    simulada no host (mesma imagem de `LifeBox`, sem a própria lógica
    de queda — a posição vem sempre do snapshot)."""

    _image = None

    @classmethod
    def _get_image(cls):
        if cls._image is None:
            image = pygame.image.load(LIFE_BOX_IMAGE_PATH).convert_alpha()
            cls._image = pygame.transform.scale(image, (50, 60))
        return cls._image

    def __init__(self):
        super().__init__()
        self.image = self._get_image()
        self.rect = self.image.get_rect()

    def sync(self, data):
        """Atualiza a posição a partir dos dados recebidos do host para
        esta caixa neste quadro."""
        self.rect.center = (data["x"], data["y"])


class AmmoBoxGhost(pygame.sprite.Sprite):
    """Representação puramente visual de uma caixa de munição simulada
    no host (mesma imagem de `AmmoBox`, sem a própria lógica de queda —
    a posição vem sempre do snapshot)."""

    _image_cache = {}

    @classmethod
    def _get_image(cls, color):
        if color not in cls._image_cache:
            path = os.path.join(AMMO_BOX_DIR, f"municao_{color}.png")
            image = pygame.image.load(path).convert_alpha()
            cls._image_cache[color] = pygame.transform.scale(image, (46, 55))
        return cls._image_cache[color]

    def __init__(self, color):
        super().__init__()
        self.image = self._get_image(color)
        self.rect = self.image.get_rect()

    def sync(self, data):
        """Atualiza a posição a partir dos dados recebidos do host para
        esta caixa neste quadro."""
        self.rect.center = (data["x"], data["y"])
