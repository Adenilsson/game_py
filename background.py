"""
Plano de fundo do jogo com efeito de rolagem infinita (parallax simples).
"""

import pygame
from config import WIDTH, HEIGHT, FPS, BLACK


class Background:
    """Desenha e move uma imagem de fundo que se repete verticalmente,
    criando a sensação de deslocamento contínuo da nave pelo cenário."""

    def __init__(self, image_path, speed=5):
        """Carrega a imagem de fundo e posiciona duas cópias empilhadas:
        uma visível na tela (y1) e outra logo acima (y2), prontas para
        alternar conforme a rolagem avança.
        """
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.y1 = 0
        self.y2 = -HEIGHT
        self.speed = speed

    def update(self):
        """Move as duas cópias da imagem para baixo e reposiciona
        qualquer uma delas no topo assim que sai completamente da tela,
        mantendo o ciclo de rolagem contínuo."""
        # Move para baixo
        self.y1 += self.speed
        self.y2 += self.speed

        # Reset quando sair da tela
        if self.y1 >= HEIGHT:
            self.y1 = -HEIGHT
        if self.y2 >= HEIGHT:
            self.y2 = -HEIGHT

    def draw(self, screen):
        """Desenha as duas cópias do fundo na tela, na posição atual."""
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
