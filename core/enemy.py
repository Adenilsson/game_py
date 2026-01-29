import pygame, random
from config import WIDTH, HEIGHT
from core.weapons.weapon1 import Weapon1
from core.weapons.weapon2 import Weapon2
from core.weapons.weapon3 import Weapon3
from core.weapons.weapon4 import Weapon4
from core.weapons.weapon5 import Weapon5

class Enemy(pygame.sprite.Sprite):
    def __init__(self, weapon_type=1):
        super().__init__()
        # Carrega sprite do avião
        self.image = pygame.image.load("assets/aviao_0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image = pygame.transform.rotate(self.image, 180)  # aponta para baixo

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

    def update(self, player, projectiles_group):
        # Movimento
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

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
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())
        screen.blit(shadow, (self.rect.centerx - 20, self.rect.bottom - 5))
