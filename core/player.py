import pygame
from config import WIDTH, HEIGHT
from core.weapons.player_weapon import PlayerWeapon
from core.weapons.basic_weapon import BasicWeapon
from core.weapons.projectile import Projectile
from config import WEAPON_COLORS
from core.weapons.basic_weapon import HeavyLaser,DoubleShot,TripolShot


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #self.image = pygame.Surface((50, 50))
        #self.image.fill((0, 255, 0))  # verde
        # Carrega sprite da nave 
        self.image_idle = pygame.image.load("assets/aviao_0.png").convert_alpha() 
        self.image_idle = pygame.transform.scale(self.image_idle, (70, 70)) 
        
        self.image_right = pygame.image.load("assets/aviao_d.png").convert_alpha() 
        self.image_right = pygame.transform.scale(self.image_right, (70, 70)) 
        
        self.image_left = pygame.image.load("assets/aviao_e.png").convert_alpha() 
        self.image_left = pygame.transform.scale(self.image_left, (70, 70)) 
        
        self.weapon = BasicWeapon(self) # começa com arma básica
        # Lista de armas disponíveis 
        self.weapons = [ 
            BasicWeapon(self), 
            DoubleShot(self),
            TripolShot(self),
            HeavyLaser(self) 
        ]
        self.current_weapon_index = 0 
        self.weapon = self.weapons[self.current_weapon_index]
        # Começa com a imagem padrão 
        self.image = self.image_idle
        
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))

        self.speed = 5
        

        # Vida do jogador
        self.max_health = 100
        self.health = self.max_health
    
    def shoot(self, projectiles_group):
        self.weapon.shoot(projectiles_group)
        
        
        
    def change_weapon(self):
        #self.weapon = new_weapon_class(self)
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons) 
        self.weapon = self.weapons[self.current_weapon_index]
            
    def update(self, keys):
        
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.image = self.image_left
        elif keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.image = self.image_right
        else: 
            self.image = self.image_idle
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        # Atualizar arma (disparo)
        self.current_weapon.update()

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print("💀 Player morreu!")
            self.alive = False
       
    
    def draw_health_bar(self, surface):
        # Barra de vida simples
        bar_width = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(surface, (255,0,0), outline_rect)   # vermelho (fundo)
        pygame.draw.rect(surface, (0,255,0), fill_rect)      # verde (vida atual)
   
    def draw_weapons_hud(self, surface):
        x_offset = 20
        y_offset = HEIGHT - 60
        radius = 20

        for i, weapon in enumerate(self.weapons):
            from config import WEAPON_COLORS
            color = WEAPON_COLORS.get(weapon.__class__.__name__, (200,200,200))
            pos = (x_offset + i*60, y_offset)

            pygame.draw.circle(surface, color, pos, radius)

            # borda branca na arma ativa
            if i == self.current_weapon_index:
                pygame.draw.circle(surface, (255,255,255), pos, radius, 3)

            # munição
            font = pygame.font.SysFont(None, 24)
            ammo_text = "∞" if weapon.ammo is None else str(weapon.ammo)
            text_surface = font.render(ammo_text, True, (0,0,0))
            text_rect = text_surface.get_rect(center=pos)
            surface.blit(text_surface, text_rect)
    
    @property
    def current_weapon(self):
        return self.weapons[self.current_weapon_index]


