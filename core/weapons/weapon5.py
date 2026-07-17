"""
Arma de inimigo: projétil teleguiado (mira em linha reta na direção
atual do jogador no momento do disparo).
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile
import math

class Weapon5(BaseWeapon):
    """Dispara periodicamente um projétil magenta calculando a direção
    exata até a posição atual do jogador."""

    def __init__(self, owner, damage=15, fire_rate=2200):
        """
        owner: inimigo que possui a arma
        damage: dano do disparo
        fire_rate: intervalo entre disparos (ms)
        """
        super().__init__(owner, damage, fire_rate)

    def update(self, player, projectiles_group):
        """Verifica se o intervalo de disparo já passou e, em caso
        positivo, calcula o vetor normalizado até o jogador e dispara
        um projétil nessa direção."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now

            # Calcula direção até o player
            dx = player.rect.centerx - self.owner.rect.centerx
            dy = player.rect.centery - self.owner.rect.centery
            length = math.hypot(dx, dy)
            if length == 0:
                length = 1
            velocity = (dx / length * 5, dy / length * 5)

            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.centery,
                velocity=velocity,
                damage=self.damage,
                color=(255, 0, 255),  # magenta
                size=(10, 10),
                owner="enemy"
            )
            projectiles_group.add(projectile)
