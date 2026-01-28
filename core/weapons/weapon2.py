import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon2(BaseWeapon):
    def __init__(self, owner, damage=20, fire_rate=2000):
        """
        owner: inimigo que possui a arma
        damage: dano causado pelo laser
        fire_rate: intervalo entre disparos (ms)
        """
        super().__init__(owner, damage, fire_rate)

    def update(self, player, projectiles_group):
        now = pygame.time.get_ticks()

        # Dispara apenas se passou o intervalo
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now

            # Cria um projétil "laser" que se move para baixo
            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.bottom,
                velocity=(0, 10),  # velocidade vertical para baixo
                damage=self.damage,
                color=(0, 255, 255),  # ciano
                size=(6, 180)  # formato de feixe
            )
            projectiles_group.add(projectile)
