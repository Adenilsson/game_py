import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color=(255,255,0), size=(10,20), velocity=(0, -5), owner="player"):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.damage = damage
        self.owner = owner  # "player" ou "enemy"
        #self.owner_entity = owner_entity # referência ao inimigo que disparou

    def update(self):
        # Movimento do projétil
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
        # Remove se sair da tela
        if (self.rect.top > 800 or self.rect.bottom < 0 or
            self.rect.left < 0 or self.rect.right > 800):
            self.kill()
