"""
Armas equipáveis pelo jogador: BasicWeapon (tiro único infinito),
DoubleShot e TripolShot (rajadas com munição limitada e recarga) e
HeavyLaser (tiro forte e lento com munição limitada).
"""

import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class BasicWeapon(BaseWeapon):
    """Arma inicial do jogador: tiro único, munição infinita, cadência alta."""

    def __init__(self, owner):
        super().__init__(owner, damage=30, fire_rate=100, ammo=None, burst=1)

    def update(self, player=None, projectiles_group=None):
        """Sem lógica contínua (munição infinita, não precisa recarregar)."""
        pass

    def shoot(self, projectiles_group):
        """Dispara um único projétil verde para cima."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -10),
            damage=self.damage,
            color=(0, 255, 0),   # verde
            size=(5, 15),
            owner="player",
        )
        projectiles_group.add(projectile)


class DoubleShot(BaseWeapon):
    """Arma com munição limitada que dispara múltiplos projéteis
    deslocados horizontalmente e recarrega automaticamente ao zerar."""

    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2)
        # Definições específicas da DoubleShot
        self.ammo_max = 20
        # quantidade máxima de munição
        self.ammo = self.ammo_max
        # começa cheia
        self.burst = 2
        # quantos tiros por disparo
        self.reload_time = 2000
        # tempo de recarga em ms (2 segundos)
        self.reloading = False
        self.reload_start = 0

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group):
        """Dispara uma leque de projéteis azuis deslocados horizontalmente
        e inicia a recarga automática assim que a munição zera."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        # dois projéteis, um pouco deslocados
        if self.ammo == 0:
            self.start_reload()

        self.last_shot = pygame.time.get_ticks()

        offsets = [-30, -15, 0, 15, 23]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18),
                owner="player",
            )
            projectiles_group.add(projectile)
        if self.ammo == 0:
            self.start_reload()
        return True

    def update(self, player=None, projectiles_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False
                print("Recarga concluída! Munição:", self.ammo)


class TripolShot(BaseWeapon):
    """Variante de rajada tripla (três projéteis deslocados) com
    munição limitada e recarga automática."""

    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2)

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group):
        """Dispara três projéteis azuis (esquerda, centro, direita) e
        inicia a recarga automática assim que a munição zera."""
        if not self.can_shoot():
            return
        if self.ammo == 0:
            self.start_reload()
        self.last_shot = pygame.time.get_ticks()
        # três projéteis, um pouco deslocados
        if self.ammo == 0:
            self.start_reload()

        offsets = [-20, 0, 20]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18),
                owner="player"
            )
            projectiles_group.add(projectile)


class HeavyLaser(BaseWeapon):
    """Arma pesada: dano alto, cadência lenta e munição limitada,
    disparando um único projétil grande."""

    def __init__(self, owner):
        super().__init__(owner, damage=50, fire_rate=500, ammo=10, burst=1)

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group):
        """Dispara um único projétil vermelho de grande porte."""
        if not self.can_shoot():
            return
        if self.ammo == 0:
            self.start_reload()

        self.last_shot = pygame.time.get_ticks()

        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -20),
            damage=self.damage,
            color=(255, 0, 0),   # vermelho
            size=(10, 40),       # bem maior
            owner="player",
        )
        projectiles_group.add(projectile)
