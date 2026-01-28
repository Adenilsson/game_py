import math
import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon3(BaseWeapon):
    def __init__(self, owner, damage=5, orbit_radius=50):
        super().__init__(owner, damage, fire_rate=0, duration=0)
        self.angle = 0
        self.orbit_radius = orbit_radius
        self.projectiles = []  # lista para armazenar os projéteis orbitais

        # Criar 3 projéteis que orbitam o inimigo
        for i in range(3):
            projectile = Projectile(
                x=owner.rect.centerx,
                y=owner.rect.centery,
                velocity=(0, 0),   # não se movem por conta própria
                damage=damage,
                color=(0, 200, 255),  # azul claro
                size=(15, 15)
            )
            self.projectiles.append((projectile, i * 2*math.pi/3))  # guarda projétil + ângulo inicial

    def update(self, player, projectiles_group):
        self.angle += 0.05  # velocidade de rotação

        for projectile, offset in self.projectiles:
            # Calcula posição orbital
            x = self.owner.rect.centerx + self.orbit_radius * math.cos(self.angle + offset)
            y = self.owner.rect.centery + self.orbit_radius * math.sin(self.angle + offset)
            projectile.rect.center = (x, y)

            # Garante que os projéteis estão no grupo
            if projectile not in projectiles_group:
                projectiles_group.add(projectile)
