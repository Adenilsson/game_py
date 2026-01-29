import pygame
from config import WIDTH, HEIGHT, FPS, BLACK

class Background:
    def __init__(self, image_path, speed=5):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.y1 = 0
        self.y2 = -HEIGHT
        self.speed = speed

    def update(self):
        # Move para baixo
        self.y1 += self.speed
        self.y2 += self.speed

        # Reset quando sair da tela
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, screen):
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
