import pygame
from config import WIDTH, HEIGHT

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        # Carregar splash art
        self.splash = pygame.image.load("assets/splash.jpg").convert_alpha()
        self.splash = pygame.transform.scale(self.splash, (WIDTH, HEIGHT))

        # Fonte
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_button = pygame.font.SysFont(None, 48)

        # Textos
        self.title_text = self.font_title.render("Meu Jogo Topdown", True, (255,255,255))
        self.play_text = self.font_button.render("JOGAR", True, (0,0,0))

        # Botão
        self.play_button = self.play_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        self.button_bg = pygame.Rect(
            self.play_button.x-20, 
            self.play_button.y-10, 
            self.play_button.width+40, 
            self.play_button.height+20
        )

    def run(self):
        waiting = True
        while waiting:
            self.screen.blit(self.splash, (0,0))
            self.screen.blit(self.title_text, (WIDTH//2 - self.title_text.get_width()//2, HEIGHT//4))

            # desenhar botão
            pygame.draw.rect(self.screen, (255,255,255), self.button_bg)
            self.screen.blit(self.play_text, self.play_button)

            pygame.display.flip()

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    pygame.quit() 
                    exit() 
                elif event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.button_bg.collidepoint(event.pos): 
                        action = "play" # clicou em jogar 
                        waiting = False
        return action
