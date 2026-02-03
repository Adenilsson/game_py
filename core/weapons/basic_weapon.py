import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class BasicWeapon(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=30, fire_rate=100, ammo=None, burst=1)
    def update(self, player=None, projectiles_group=None): 
        # por padrão não faz nada 
        pass
    
   

            
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
            size=(5, 15),
            owner="player",
            
        )
        projectiles_group.add(projectile)


class DoubleShot(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2 )
        # Definições específicas da DoubleShot 
        self.ammo_max = 20 
        # quantidade máxima de munição 
        self.ammo = self.ammo_max 
        # começa cheia
        self.burst = 2
        # quantos tiros por disparo
        self.reload_time = 2000 
        #tempo de recarga em ms (2 segundos) 
        self.reloading = False 
        self.reload_start = 0
    def start_reload(self): 
        self.reloading = True 
        self.reload_start = pygame.time.get_ticks() 
        
    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()
        
        # dois projéteis, um pouco deslocados
        if self.ammo == 0:
            self.start_reload()
        
        self.last_shot = pygame.time.get_ticks()
        
        offsets = [-30,-15,0,15, 23]
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
    def start_reload(self): 
        self.reloading = True 
        self.reload_start = pygame.time.get_ticks() 
        print("Recarga iniciada...")
        
    def update(self, player=None, projectiles_group=None): 
        if self.reloading: 
            now = pygame.time.get_ticks() 
            if now - self.reload_start >= self.reload_time: 
                self.ammo = self.ammo_max
                self.reloading = False
                print("Recarga concluída! Munição:", self.ammo)
        

class TripolShot(BaseWeapon):
    def __init__(self, owner):
        super().__init__(owner, damage=25, fire_rate=400, ammo=20, burst=2)
    def start_reload(self): 
        self.reloading = True 
        self.reload_start = pygame.time.get_ticks()  
        
    def shoot(self, projectiles_group):
        if not self.can_shoot():
            return
        if self.ammo == 0:
            self.start_reload()
        self.last_shot = pygame.time.get_ticks()
        # dois projéteis, um pouco deslocados
        if self.ammo == 0:
            self.start_reload()
        
       
        offsets = [-20,0, 20]
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
    def __init__(self, owner):
        super().__init__(owner, damage=50, fire_rate=500, ammo=10, burst=1)
    def start_reload(self): 
        self.reloading = True 
        self.reload_start = pygame.time.get_ticks() 
        
    def shoot(self, projectiles_group):
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
            size=(10, 40) ,       # bem maior
            owner="player",
           
        )
        projectiles_group.add(projectile)
