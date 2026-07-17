"""
Arma de inimigo: tiro único simples, disparado para baixo em direção
ao jogador.
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile
from core.settings import settings

class Weapon1(BaseWeapon):
    """Dispara periodicamente um único projétil amarelo para baixo,
    tocando um efeito sonoro a cada disparo."""

    def __init__(self, owner, damage=10, fire_rate=800):
        """Carrega o som de disparo uma única vez (evita reler o arquivo
        do disco a cada quadro dentro de `update`). O volume é aplicado
        no momento de tocar, para respeitar ajustes feitos depois.

        fire_rate: intervalo mínimo entre disparos (ms)."""
        super().__init__(owner, damage, fire_rate)
        self.shoot_sound = settings.load_sound("assets/sons/disparo_base.mp3")

    def update(self, player, projectiles_group):
        """Verifica se o intervalo de disparo (`fire_rate`) já passou e,
        em caso positivo, toca o som de tiro e cria um novo projétil."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            settings.play_sound(self.shoot_sound)
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
