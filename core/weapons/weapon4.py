"""
Arma de inimigo: disparo triplo em leque, com três projéteis saindo
em ângulos levemente diferentes.
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon4(BaseWeapon):
    """Dispara periodicamente três projéteis laranjas em leque
    (esquerda, centro, direita) na direção do jogador."""

    def __init__(self, owner, damage=10, fire_rate=1500):
        """
        owner: inimigo que possui a arma
        damage: dano de cada esfera
        fire_rate: intervalo entre disparos (ms)
        """
        super().__init__(owner, damage, fire_rate)

    def update(self, player, projectiles_group):
        """Verifica se o intervalo de disparo já passou e, em caso
        positivo, cria os três projéteis em leque."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            # Três ângulos diferentes (oblíquos)
            velocities = [(-2, 5), (0, 5), (2, 5)]
            for vel in velocities:
                projectile = Projectile(
                    x=self.owner.rect.centerx,
                    y=self.owner.rect.bottom,
                    velocity=vel,
                    damage=self.damage,
                    color=(255, 165, 0),  # laranja
                    size=(12, 12),
                    owner="enemy"
                )
                projectiles_group.add(projectile)
