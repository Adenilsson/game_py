"""
Tela de fim de jogo: exibe a pontuação final em um painel destacado,
com um fundo em gradiente e botões arredondados para reiniciar a
partida ou voltar ao menu principal.
"""

import pygame
from config import WIDTH, HEIGHT
from core.settings import settings

PANEL_COLOR = (20, 20, 30, 190)
PANEL_BORDER_COLOR = (255, 255, 255, 200)
MENU_COLOR = (80, 80, 90)
MENU_HOVER_COLOR = (110, 110, 125)


def _lighten(color, amount=30):
    """Clareia uma cor RGB somando `amount` a cada canal, sem estourar 255."""
    return tuple(min(255, c + amount) for c in color)


class GameOverScreen:
    """Tela exibida quando o jogador morre, com opções de reiniciar
    a partida ou retornar ao menu inicial."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho, prepara as
        fontes e monta o fundo em gradiente (calculado uma única vez)."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 92)
        self.font_title.set_bold(True)
        self.font_text = pygame.font.SysFont(None, 40)
        self.font_button = pygame.font.SysFont(None, 44)
        self.background = self._build_gradient()

    def _build_gradient(self):
        """Cria uma superfície com um gradiente vertical (vinho escuro
        no topo, preto na base), dando um clima mais dramático à tela
        de derrota do que um preto liso."""
        gradient = pygame.Surface((WIDTH, HEIGHT))
        top_color = (55, 12, 18)
        bottom_color = (8, 8, 12)
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
            pygame.draw.line(gradient, color, (0, y), (WIDTH, y))
        return gradient

    def _draw_button(self, rect, text_surface, base_color, hover_color, hovered):
        """Desenha um botão arredondado com destaque ao passar o mouse."""
        color = hover_color if hovered else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def run(self, final_score, high_score=None):
        """Exibe a tela de game over em loop até o jogador clicar em
        REINICIAR ou MENU, retornando a ação escolhida ("restart"/"menu").
        Se `high_score` for informado, mostra também o recorde atual e
        destaca quando a pontuação da partida é um novo recorde."""
        waiting = True
        action = None

        title_text = self.font_title.render("GAME OVER", True, (220, 40, 40))
        title_shadow = self.font_title.render("GAME OVER", True, (0, 0, 0))
        score_text = self.font_text.render(f"Pontuação final: {final_score}", True, (255, 255, 255))

        high_score_text = None
        is_new_record = high_score is not None and final_score >= high_score and final_score > 0
        if high_score is not None:
            if is_new_record:
                high_score_text = self.font_text.render(f">> Novo recorde: {high_score} <<", True, (255, 215, 0))
            else:
                high_score_text = self.font_text.render(f"Recorde: {high_score}", True, (190, 190, 190))

        title_y = 90

        # --- Painel com a pontuação ---
        panel_width = 380
        panel_height = 130 if high_score_text is not None else 90
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (WIDTH // 2, 320)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, PANEL_COLOR, panel_surface.get_rect(), border_radius=20)
        border_color = (255, 215, 0, 220) if is_new_record else PANEL_BORDER_COLOR
        pygame.draw.rect(panel_surface, border_color, panel_surface.get_rect(), width=2, border_radius=20)

        restart_text = self.font_button.render("REINICIAR", True, (255, 255, 255))
        menu_text = self.font_button.render("MENU", True, (255, 255, 255))

        restart_button = pygame.Rect(0, 0, 220, 58)
        restart_button.center = (WIDTH // 2, panel_rect.bottom + 90)
        menu_button = pygame.Rect(0, 0, 220, 58)
        menu_button.center = (WIDTH // 2, restart_button.bottom + 35)

        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(self.background, (0, 0))

            # Título com sombra sutil, para dar profundidade
            self.screen.blit(title_shadow, (WIDTH // 2 - title_text.get_width() // 2 + 3, title_y + 3))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, title_y))

            # Painel com a pontuação
            self.screen.blit(panel_surface, panel_rect.topleft)
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, panel_rect.y + 20))
            if high_score_text is not None:
                self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, panel_rect.y + 70))

            # Botões
            self._draw_button(restart_button, restart_text, settings.accent_color,
                               _lighten(settings.accent_color), restart_button.collidepoint(mouse_pos))
            self._draw_button(menu_button, menu_text, MENU_COLOR, MENU_HOVER_COLOR,
                               menu_button.collidepoint(mouse_pos))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        action = "restart"
                        waiting = False
                    elif menu_button.collidepoint(event.pos):
                        action = "menu"
                        waiting = False

        return action
