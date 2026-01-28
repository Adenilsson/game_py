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
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))    # vermelho
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH-50), 0)  # começa no topo
        )
       
        # Escolhe arma correta
        

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
        self.speed_y = random.randint(2, 5)   # velocidade vertical (descendo)
        self.speed_x = random.choice([-2, -1, 0, 1, 2])  # movimento horizontal aleatório

    def update(self, player, projectiles_group):
        # Movimento
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        self.weapon.update(player, projectiles_group)
        # Rebater nas laterais
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

        # Reiniciar inimigo quando sair da tela
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(50, WIDTH-50), 0)
            self.speed_y = random.randint(2, 5)
            self.speed_x = random.choice([-2, -1, 0, 1, 2])

        # Atualizar arma (disparos)
        self.weapon.update(player, projectiles_group)
