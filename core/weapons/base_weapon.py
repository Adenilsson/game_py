import pygame
from core.weapons.projectile import Projectile

class BaseWeapon:
    def __init__(self, owner, damage=10, fire_rate=300, ammo=None, ammo_max =20, burst=1,duration=None, reload_time=200):
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
        self.duration = duration 
        self.last_shot = 0
        self.reload_time = reload_time
        self.last_reload = 0
        self.reloading = True
        self.reload_start = 0
        
    def update(self, player=None, projectiles_group=None):
        # por padrão não faz nada 
        pass
    def shoot(self, projectiles_group):
        now = pygame.time.get_ticks()

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
                velocity=(0, -10),  
                damage=self.damage,
                color=(255, 255, 0),
                size=(6, 15),
                owner= "enemy"
                
                
            )
            projectiles_group.add(projectile)

        # Consome munição
        if self.ammo is not None:
            self.ammo -= self.burst
    def can_shoot(self): 
        now = pygame.time.get_ticks() 
        if now - self.last_shot < self.fire_rate: 
            return False 
        if self.ammo is not None and self.ammo <= 0: 
            return False 
        if self.ammo is not None: 
            self.ammo -= 1 
        return True