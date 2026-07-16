"""
Arma de inimigo: enxame de projéteis que orbitam ao redor do dono,
funcionando como um escudo giratório.
"""

import math
import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon3(BaseWeapon):
    """Cria projéteis que giram continuamente em órbita ao redor do
    inimigo, servindo tanto de ataque quanto de proteção."""

    def __init__(self, owner, damage=5, orbit_radius=60):
        """Cria 6 projéteis distribuídos uniformemente em círculo ao
        redor do dono, cada um guardando seu ângulo inicial de órbita."""
        super().__init__(owner, damage, fire_rate=0, duration=0)
        self.angle = 0
        self.orbit_radius = orbit_radius
        self.projectiles = []  # lista para armazenar os projéteis orbitais

        # Criar 6 projéteis que orbitam o inimigo
        for i in range(6):
            projectile = Projectile(
                x=owner.rect.centerx,
                y=owner.rect.centery,
                damage=damage,
                velocity=(0, 6),   # não se movem por conta própria
                color=(0, 200, 255),  # azul claro
                size=(15, 15),
                owner="enemy",
            )
            self.projectiles.append((projectile, i * 2 * math.pi / 3))  # guarda projétil + ângulo inicial

    def update(self, player, projectiles_group):
        """Avança o ângulo de rotação e reposiciona cada projétil na
        órbita ao redor do inimigo, garantindo que todos estejam no
        grupo de projéteis ativo."""
        self.angle += 0.05  # velocidade de rotação

        for projectile, offset in self.projectiles:
            # Calcula posição orbital
            x = self.owner.rect.centerx + self.orbit_radius * math.cos(self.angle + offset)
            y = self.owner.rect.centery + self.orbit_radius * math.sin(self.angle + offset)
            projectile.rect.center = (x, y)

            # Garante que os projéteis estão no grupo
            if projectile not in projectiles_group:
                projectiles_group.add(projectile)
