"""
Arma de granada do jogador: dispara um único projétil que viaja em
linha reta e, após um curto período no ar, explode em vários
fragmentos disparados em todas as direções.
"""

import math
import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

FRAGMENT_COLOR = (255, 140, 0)  # laranja, para diferenciar da granada


class Grenade(Projectile):
    """A granada em si: se move como um projétil comum, mas carrega um
    "pavio" — ao expirar (ou ao sair da tela, o que vier primeiro), se
    autodestrói e, se ainda estava em jogo, espalha fragmentos ao redor
    do ponto onde explodiu."""

    def __init__(self, x, y, damage, velocity, owner, projectiles_group,
                 fuse_ms, fragment_count, fragment_speed, fragment_damage,
                 color, size):
        """Guarda o grupo de projéteis (para poder adicionar os
        fragmentos quando explodir) e os parâmetros da explosão: tempo
        até explodir, quantidade de fragmentos, velocidade e dano de
        cada um."""
        super().__init__(x, y, damage, color=color, size=size, velocity=velocity, owner=owner)
        self.projectiles_group = projectiles_group
        self.spawn_time = pygame.time.get_ticks()
        self.fuse_ms = fuse_ms
        self.fragment_count = fragment_count
        self.fragment_speed = fragment_speed
        self.fragment_damage = fragment_damage

    def update(self):
        """Move a granada normalmente (herdado de `Projectile`, que já
        remove a granada sozinha se ela sair da tela); se o pavio já
        estourou e ela ainda está em jogo, explode."""
        super().update()
        if not self.alive():
            return  # já foi removida por sair da tela: não explode
        if pygame.time.get_ticks() - self.spawn_time >= self.fuse_ms:
            self._explode()

    def _explode(self):
        """Cria `fragment_count` projéteis partindo do centro da
        granada, distribuídos uniformemente em círculo (360°), e
        remove a granada original."""
        for i in range(self.fragment_count):
            angle = (2 * math.pi / self.fragment_count) * i
            velocity = (math.cos(angle) * self.fragment_speed, math.sin(angle) * self.fragment_speed)
            fragment = Projectile(
                x=self.rect.centerx,
                y=self.rect.centery,
                damage=self.fragment_damage,
                velocity=velocity,
                color=FRAGMENT_COLOR,
                size=(8, 8),
                owner=self.owner,
            )
            self.projectiles_group.add(fragment)
        self.kill()


class GrenadeWeapon(BaseWeapon):
    """Arma do jogador que dispara uma granada de cada vez: munição
    limitada com recarga automática, cadência lenta (é uma arma de
    munição pesada) e dano dividido entre os fragmentos da explosão."""

    def __init__(self, owner, damage=12, fire_rate=900, ammo_max=6,
                 fuse_ms=1400, fragment_count=8, fragment_speed=6):
        """Configura munição, cadência, tempo de recarga e os parâmetros
        da explosão (tempo até estourar, quantidade e velocidade dos
        fragmentos); começa com a munição cheia e fora do estado de
        recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=1)
        self.ammo_max = ammo_max
        self.ammo = self.ammo_max
        self.reload_time = 3000
        self.reloading = False
        self.reload_start = 0
        self.fuse_ms = fuse_ms
        self.fragment_count = fragment_count
        self.fragment_speed = fragment_speed

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group, enemies_group=None):
        """Lança uma granada verde para cima e inicia a recarga
        automática assim que a munição zera. A explosão acontece
        depois, dentro do próprio `update` da granada (ver `Grenade`)."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        if self.ammo == 0:
            self.start_reload()

        grenade = Grenade(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            damage=self.damage,
            velocity=(0, -6),
            owner="player",
            projectiles_group=projectiles_group,
            fuse_ms=self.fuse_ms,
            fragment_count=self.fragment_count,
            fragment_speed=self.fragment_speed,
            fragment_damage=self.damage,
            color=(60, 160, 60),   # verde-oliva
            size=(12, 12),
        )
        projectiles_group.add(grenade)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False
