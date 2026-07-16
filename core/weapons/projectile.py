"""
Projétil genérico usado por todas as armas (do jogador e dos inimigos).
"""

import pygame

class Projectile(pygame.sprite.Sprite):
    """Representa um único projétil: um retângulo colorido que se move
    em linha reta na direção/velocidade definida e se autodestrói ao
    sair dos limites da tela."""

    def __init__(self, x, y, damage, color=(255, 255, 0), size=(10, 20), velocity=(0, -5), owner="player"):
        """Cria o projétil na posição (x, y) com a aparência, dano,
        velocidade e dono ("player" ou "enemy") informados. O dono é
        usado para decidir quem pode ser atingido por este projétil."""
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.damage = damage
        self.owner = owner  # "player" ou "enemy"

    def update(self):
        """Move o projétil conforme sua velocidade e o remove
        automaticamente quando sai completamente da área visível da tela."""
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Remove se sair da tela
        if (self.rect.top > 800 or self.rect.bottom < 0 or
            self.rect.left < 0 or self.rect.right > 800):
            self.kill()
