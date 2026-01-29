import pygame
from config import WIDTH, HEIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #self.image = pygame.Surface((50, 50))
        #self.image.fill((0, 255, 0))  # verde
        # Carrega sprite da nave 
        self.image_idle = pygame.image.load("assets/aviao_0.png").convert_alpha() 
        self.image_idle = pygame.transform.scale(self.image_idle, (50, 50)) 
        
        self.image_right = pygame.image.load("assets/aviao_d.png").convert_alpha() 
        self.image_right = pygame.transform.scale(self.image_right, (50, 50)) 
        
        self.image_left = pygame.image.load("assets/aviao_e.png").convert_alpha() 
        self.image_left = pygame.transform.scale(self.image_left, (50, 50)) 
        
        # Começa com a imagem padrão 
        self.image = self.image_idle
        
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))

        self.speed = 5

        # Vida do jogador
        self.max_health = 100
        self.health = self.max_health

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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print("💀 Player morreu!")
            self.alive = False
            # Aqui você pode encerrar o jogo ou reiniciar
       
    
    def draw_health_bar(self, surface):
        # Barra de vida simples
        bar_width = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(surface, (255,0,0), outline_rect)   # vermelho (fundo)
        pygame.draw.rect(surface, (0,255,0), fill_rect)      # verde (vida atual)
