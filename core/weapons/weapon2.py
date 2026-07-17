"""
Arma de inimigo: feixe de laser vertical, longo e contínuo.
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile
from core.settings import settings

class Weapon2(BaseWeapon):
    """Dispara periodicamente um feixe de laser (projétil alto e fino)
    para baixo, tocando um efeito sonoro a cada disparo."""

    def __init__(self, owner, damage=20, fire_rate=2800):
        """
        owner: inimigo que possui a arma
        damage: dano causado pelo laser
        fire_rate: intervalo entre disparos (ms)
        """
        super().__init__(owner, damage, fire_rate)
        # Carrega o som uma única vez (evita reler o arquivo do disco a
        # cada quadro dentro de `update`); o volume é aplicado no
        # momento de tocar, para respeitar ajustes feitos depois
        self.shoot_sound = settings.load_sound("assets/sons/doble_shoot.mp3")

    def update(self, player, projectiles_group):
        """Verifica se o intervalo de disparo já passou e, em caso
        positivo, toca o som e cria o feixe de laser."""
        now = pygame.time.get_ticks()
        # Dispara apenas se passou o intervalo
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            settings.play_sound(self.shoot_sound)
            # Cria um projétil "laser" que se move para baixo
            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.bottom,
                damage=self.damage,
                velocity=(0, 10),  # velocidade vertical para baixo
                color=(0, 255, 255),  # ciano
                size=(6, 180),  # formato de feixe
                owner="enemy",
            )
            projectiles_group.add(projectile)
