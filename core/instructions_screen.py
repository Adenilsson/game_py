import pygame
from config import WIDTH, HEIGHT

class InstructionsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_text = pygame.font.SysFont(None, 32)
        self.font_button = pygame.font.SysFont(None, 48)

        # Título
        self.title_text = self.font_title.render("Instruções & Regras", True, (255,255,255))

        # Lista de instruções
        self.instructions = [
            "Use W, A, S, D para mover a nave.",
            "Pressione ESPAÇO para atirar.",
            "Pressione F para trocar de arma.",
            "Evite colisões com inimigos e projéteis.",
            "Derrote inimigos para ganhar pontos.",
            "Se a vida chegar a zero, o jogo termina."
        ]

        # Botões
        self.start_text = self.font_button.render("INICIAR", True, (0,0,0))
        self.back_text = self.font_button.render("VOLTAR", True, (0,0,0))

        self.start_button = self.start_text.get_rect(center=(WIDTH//2, HEIGHT - 160))
        self.back_button = self.back_text.get_rect(center=(WIDTH//2, HEIGHT - 80))

        self.start_bg = pygame.Rect(self.start_button.x-20, self.start_button.y-10,
                                    self.start_button.width+40, self.start_button.height+20)
        self.back_bg = pygame.Rect(self.back_button.x-20, self.back_button.y-10,
                                   self.back_button.width+40, self.back_button.height+20)

    def run(self):
        waiting = True
        action = None
        while waiting:
            self.screen.fill((0,0,50))  # fundo azul escuro

            # título
            self.screen.blit(self.title_text, (WIDTH//2 - self.title_text.get_width()//2, 50))

            # instruções
            y_offset = 150
            for line in self.instructions:
                text_surface = self.font_text.render(line, True, (255,255,255))
                self.screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, y_offset))
                y_offset += 40

            # desenhar botões
            pygame.draw.rect(self.screen, (255,255,255), self.start_bg)
            self.screen.blit(self.start_text, self.start_button)

            pygame.draw.rect(self.screen, (255,255,255), self.back_bg)
            self.screen.blit(self.back_text, self.back_button)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_bg.collidepoint(event.pos):
                        action = "start"
                        waiting = False
                    elif self.back_bg.collidepoint(event.pos):
                        action = "back"
                        waiting = False
        return action
