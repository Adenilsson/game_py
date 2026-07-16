"""
Efeitos visuais transitórios (atualmente, a explosão exibida quando um
inimigo é destruído).
"""

import pygame


class Explosion(pygame.sprite.Sprite):
    """Círculo que se expande e desaparece gradualmente ao longo do
    tempo, usado para marcar visualmente a destruição de um inimigo."""

    def __init__(self, center, duration=300, max_radius=35, color=(255, 140, 0)):
        """Cria o efeito centralizado em `center` (tupla x, y), com
        duração em milissegundos e raio máximo configuráveis."""
        super().__init__()
        self.duration = duration
        self.max_radius = max_radius
        self.color = color
        self.start_time = pygame.time.get_ticks()
        self.image = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)

    def update(self):
        """Avança a animação: cresce o círculo e reduz sua opacidade
        conforme o tempo passa, removendo o efeito ao final da duração."""
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return

        progress = elapsed / self.duration
        radius = max(1, int(self.max_radius * progress))
        alpha = int(255 * (1 - progress))

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*self.color, alpha), (self.max_radius, self.max_radius), radius)
