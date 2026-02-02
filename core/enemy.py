import pygame, random
from config import WIDTH, HEIGHT
from core.weapons.weapon1 import Weapon1
from core.weapons.weapon2 import Weapon2
from core.weapons.weapon3 import Weapon3
from core.weapons.weapon4 import Weapon4
from core.weapons.weapon5 import Weapon5

class Enemy(pygame.sprite.Sprite):
    #def __init__(self, weapon_type=1):
    def __init__(self, x=100, y=100, health=50, weapon_type=1):
        super().__init__()
        # Carrega sprite do avião
        self.image = pygame.image.load("assets/aviao.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.image = pygame.transform.rotate(self.image, 180)  # aponta para baixo
        
        # atributos de vida 
        self.health = health 
        self.weapon_type = weapon_type 
        self.alive = True
        if health == 30: 
            self.score_value = 1 
        elif health == 50: 
            self.score_value = 2 
        elif health == 80: 
            self.score_value = 3
        else: self.score_value = 1 # valor padrão
        
        # Posição inicial (topo da tela, posição aleatória no eixo X)
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH-50), 0)
        )

        # Escolhe arma
        if weapon_type == 1:
            self.weapon = Weapon1(self)
        elif weapon_type == 2:
            self.weapon = Weapon2(self)
        elif weapon_type == 3:
            self.weapon = Weapon3(self)
        elif weapon_type == 4:
            self.weapon = Weapon4(self)
        elif weapon_type == 5:
            self.weapon = Weapon5(self)

        # Movimento inicial
        self.speed_y = random.randint(2, 5)   # velocidade vertical
        self.speed_x = random.choice([-2, -1, 0, 1, 2])  # movimento horizontal

    def update(self, player, projectiles_group, game):
        # Movimento
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        # colisão com projéteis 
        hits = pygame.sprite.spritecollide(self, projectiles_group, False) 
        for proj in hits: 
           if proj.owner == "player": 
               self.take_damage(proj.damage, game)
               proj.kill()
        # se morrer, remove do grupo
        if not self.alive: 
            self.kill()
        # Rebater nas laterais
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

        # Reiniciar inimigo quando sair da tela
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(50, WIDTH-50), 0)
            self.speed_y = random.randint(2, 5)
            self.speed_x = random.choice([-2, -1, 0, 1, 2])

        # Atualizar arma (disparo)
        self.weapon.update(player, projectiles_group)

    def draw_shadow(self, screen):
        shadow = pygame.Surface((40, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 200), shadow.get_rect())
        screen.blit(shadow, (self.rect.centerx - 20, self.rect.bottom + 50))
        
        
    def take_damage(self, amount, game=None):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            print("💥 Inimigo destruído!")
            if game:  # soma pontos antes de remover
                game.score += self.score_value
            self.kill()

            


    def draw_health_bar(self, surface): 
        bar_width = 40
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, (255,0,0), outline_rect) # fundo vermelho
        pygame.draw.rect(surface, (0,255,0), fill_rect) # vida verde