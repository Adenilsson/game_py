import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class BasicWeapon(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=10, fire_rate=300, ammo=None, burst=1)

    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -10),
            damage=self.damage,
            color=(0, 255, 0),   # verde
            size=(5, 15)
        )
        projectiles_group.add(projectile)


class DoubleShot(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2)

    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        # dois projéteis, um pouco deslocados
        offsets = [-10, 10]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18)
            )
            projectiles_group.add(projectile)

class TripolShot(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2)

    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        # dois projéteis, um pouco deslocados
        offsets = [-20,0, 20]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18)
            )
            projectiles_group.add(projectile)

class HeavyLaser(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=50, fire_rate=500, ammo=10, burst=1)

    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -20),
            damage=self.damage,
            color=(255, 0, 0),   # vermelho
            size=(10, 40)        # bem maior
        )
        projectiles_group.add(projectile)
