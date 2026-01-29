import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile
import math

class Weapon5(BaseWeapon):
    def __init__(self, owner, damage=15, fire_rate=1500):
        """
        owner: inimigo que possui a arma
        damage: dano do disparo
        fire_rate: intervalo entre disparos (ms)
        """
        super().__init__(owner, damage, fire_rate)

    def update(self, player, projectiles_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now

            # Calcula direção até o player
            dx = player.rect.centerx - self.owner.rect.centerx
            dy = player.rect.centery - self.owner.rect.centery
            length = math.hypot(dx, dy)
            if length == 0:
                length = 1
            velocity = (dx/length*5, dy/length*5)

            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.centery,
                velocity=velocity,
                damage=self.damage,
                color=(255, 0, 255),  # magenta
                size=(10, 10),
                owner= "enemy"
            )
            projectiles_group.add(projectile)
