import pygame
import time
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class Weapon1(BaseWeapon):
    
    def update(self, player, projectiles_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            projectile = Projectile( 
                x=self.owner.rect.centerx, 
                y=self.owner.rect.bottom,
                damage=self.damage, 
                 velocity=(0, 5), 
                color=(255,255,0), # amarelo
                size=(10,20),
                owner="enemy",
               
                
                
                
            ) 
            projectiles_group.add(projectile)
