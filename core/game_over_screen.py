"""
Tela de fim de jogo: exibe a pontuação final e os botões para
reiniciar a partida ou voltar ao menu principal.
"""

import pygame
from config import WIDTH, HEIGHT

class GameOverScreen:
    """Tela exibida quando o jogador morre, com opções de reiniciar
    a partida ou retornar ao menu inicial."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho e prepara as fontes."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_text = pygame.font.SysFont(None, 48)
        self.font_button = pygame.font.SysFont(None, 48)

    def run(self, final_score, high_score=None):
        """Exibe a tela de game over em loop até o jogador clicar em
        REINICIAR ou MENU, retornando a ação escolhida ("restart"/"menu").
        Se `high_score` for informado, mostra também o recorde atual e
        destaca quando a pontuação da partida é um novo recorde."""
        waiting = True
        action = None

        # Renderizar textos
        title_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font_text.render(f"Pontuação: {final_score}", True, (255,255,255))

        high_score_text = None
        if high_score is not None:
            if final_score >= high_score and final_score > 0:
                high_score_text = self.font_text.render(f"Novo recorde: {high_score}!", True, (255, 215, 0))
            else:
                high_score_text = self.font_text.render(f"Recorde: {high_score}", True, (200, 200, 200))

        # Botões
        restart_text = self.font_button.render("REINICIAR", True, (0,0,0))
        menu_text = self.font_button.render("MENU", True, (0,0,0))

        restart_button = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        menu_button = menu_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 180))

        restart_bg = pygame.Rect(restart_button.x-20, restart_button.y-10,
                                 restart_button.width+40, restart_button.height+20)
        menu_bg = pygame.Rect(menu_button.x-20, menu_button.y-10,
                              menu_button.width+40, menu_button.height+20)

        while waiting:
            self.screen.fill((0,0,0))

            # Título e pontuação
            self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
            self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            if high_score_text is not None:
                self.screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 45))

            # Botões
            pygame.draw.rect(self.screen, (255,255,255), restart_bg)
            self.screen.blit(restart_text, restart_button)

            pygame.draw.rect(self.screen, (255,255,255), menu_bg)
            self.screen.blit(menu_text, menu_button)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_bg.collidepoint(event.pos):
                        action = "restart"
                        waiting = False
                    elif menu_bg.collidepoint(event.pos):
                        action = "menu"
                        waiting = False

        return action
