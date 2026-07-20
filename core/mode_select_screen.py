"""
Tela de escolha do modo de jogo: sozinho, hospedando uma partida
cooperativa em LAN, ou entrando na partida de outra pessoa na mesma
rede local.
"""

import pygame
from config import WIDTH, HEIGHT

BUTTON_COLOR = (70, 70, 95)
BUTTON_HOVER_COLOR = (105, 105, 145)
EXIT_COLOR = (150, 55, 55)
EXIT_HOVER_COLOR = (190, 75, 75)


class ModeSelectScreen:
    """Primeira tela do jogo: escolhe entre jogar sozinho ou cooperar
    com outra pessoa na mesma rede local (hospedando ou entrando numa
    partida já aberta)."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho e prepara as fontes."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 60)
        self.font_button = pygame.font.SysFont(None, 28)
        self.font_hint = pygame.font.SysFont(None, 24)

    def _draw_button(self, rect, text_surface, base_color, hover_color, hovered):
        """Desenha um botão arredondado com destaque ao passar o mouse."""
        color = hover_color if hovered else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def run(self):
        """Exibe a tela em loop até o jogador escolher um modo ou sair.
        Retorna "solo", "host" ou "join"."""
        splash = pygame.image.load("assets/imagens/telas/splash.jpg").convert_alpha()
        splash = pygame.transform.scale(splash, (WIDTH, HEIGHT))

        title_text = self.font_title.render("Como você quer jogar?", True, (255, 255, 255))
        hint_text = self.font_hint.render(
            "Hospedar/Entrar exige que os jogadores estejam na mesma rede local",
            True, (200, 200, 200),
        )

        solo_text = self.font_button.render("JOGAR SOZINHO", True, (255, 255, 255))
        host_text = self.font_button.render("HOSPEDAR PARTIDA (LAN)", True, (255, 255, 255))
        join_text = self.font_button.render("ENTRAR EM PARTIDA (LAN)", True, (255, 255, 255))
        exit_text = self.font_button.render("SAIR", True, (255, 255, 255))

        button_width, button_height, gap = 360, 60, 22
        start_y = HEIGHT // 2 - 110
        solo_button = pygame.Rect(0, 0, button_width, button_height)
        solo_button.center = (WIDTH // 2, start_y)
        host_button = pygame.Rect(0, 0, button_width, button_height)
        host_button.center = (WIDTH // 2, start_y + (button_height + gap))
        join_button = pygame.Rect(0, 0, button_width, button_height)
        join_button.center = (WIDTH // 2, start_y + 2 * (button_height + gap))
        exit_button = pygame.Rect(0, 0, button_width, button_height)
        exit_button.center = (WIDTH // 2, start_y + 3 * (button_height + gap) + 20)

        waiting = True
        result = None
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(splash, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 140))
            self.screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, 210))

            self._draw_button(solo_button, solo_text, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                               solo_button.collidepoint(mouse_pos))
            self._draw_button(host_button, host_text, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                               host_button.collidepoint(mouse_pos))
            self._draw_button(join_button, join_text, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                               join_button.collidepoint(mouse_pos))
            self._draw_button(exit_button, exit_text, EXIT_COLOR, EXIT_HOVER_COLOR,
                               exit_button.collidepoint(mouse_pos))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if solo_button.collidepoint(event.pos):
                        result = "solo"
                        waiting = False
                    elif host_button.collidepoint(event.pos):
                        result = "host"
                        waiting = False
                    elif join_button.collidepoint(event.pos):
                        result = "join"
                        waiting = False
                    elif exit_button.collidepoint(event.pos):
                        pygame.quit()
                        exit()

        return result
