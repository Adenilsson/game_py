"""
Arma de inimigo: tiro único simples, disparado para baixo em direção
ao jogador.
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon1(BaseWeapon):
    """Dispara periodicamente um único projétil amarelo para baixo,
    tocando um efeito sonoro a cada disparo."""

    def __init__(self, owner):
        """Carrega o som de disparo uma única vez (evita reler o arquivo
        do disco a cada quadro dentro de `update`)."""
        super().__init__(owner)
        self.shoot_sound = pygame.mixer.Sound("assets/sons/disparo_base.ogg")

    def update(self, player, projectiles_group):
        """Verifica se o intervalo de disparo (`fire_rate`) já passou e,
        em caso positivo, toca o som de tiro e cria um novo projétil."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.shoot_sound.play()
            self.last_shot = now
            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.bottom,
                damage=self.damage,
                velocity=(0, 5),
                color=(255, 255, 0),  # amarelo
                size=(10, 20),
                owner="enemy",
            )
            projectiles_group.add(projectile)
