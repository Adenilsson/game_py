import pygame
from core.weapons.projectile import Projectile

class PlayerWeapon:
    def __init__(self, owner, damage=10, fire_rate=300, ammo=None, burst=1):
        """
        owner: referência ao player
        damage: dano por projétil
        fire_rate: intervalo mínimo entre disparos (ms)
        ammo: limite de munição (None = infinito)
        burst: número de disparos consecutivos por vez
        """
        self.owner = owner
        self.damage = damage
        self.fire_rate = fire_rate
        self.ammo = ammo
        self.burst = burst
        self.last_shot = 0

    def shoot(self, projectiles_group):
        now = pygame.time.get_ticks()
        if self.ammo > 0 and now - self.last_shot > self.fire_rate:
            self.ammo -= 1
            self.last_shot = now
            print("Disparo! Munição restante:", self.ammo)
            if self.ammo == 0:
                self.start_reload()
                
        # Verifica intervalo entre disparos
        if now - self.last_shot < self.fire_rate:
            
            return

        # Verifica munição
        if self.ammo is not None and self.ammo <= 0:
            return

        self.last_shot = now

        # Dispara projéteis consecutivos
        for i in range(self.burst):
            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.top,
                velocity=(0, -10),  # para cima
                damage=self.damage,
                color=(255, 255, 0),
                size=(6, 15),
                owner= "player"
                
            )
            projectiles_group.add(projectile)

        # Consome munição
        if self.ammo is not None:
            self.ammo -= self.burst
