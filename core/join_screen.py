"""
Tela para entrar em uma partida cooperativa hospedada por outra pessoa
na mesma rede local: pede o IP de quem hospeda e tenta conectar.
"""

import pygame
from config import WIDTH, HEIGHT
from core.network.protocol import DEFAULT_PORT
from core.network.client import GameClient


class JoinScreen:
    """Pede o IP de quem está hospedando a partida e tenta conectar ao
    clicar em CONECTAR."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho e prepara as fontes."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 56)
        self.font_label = pygame.font.SysFont(None, 30)
        self.font_button = pygame.font.SysFont(None, 38)

    def run(self):
        """Exibe a tela em loop até o jogador clicar em CONECTAR (com
        sucesso) ou em VOLTAR. Retorna um `GameClient` já conectado, ou
        None se o jogador desistir."""
        ip_text = ""
        error_message = ""
        active = True

        title_text = self.font_title.render("Entrar em partida", True, (255, 255, 255))
        label_text = self.font_label.render("IP de quem está hospedando:", True, (255, 255, 255))
        connect_text = self.font_button.render("CONECTAR", True, (255, 255, 255))
        back_text = self.font_button.render("VOLTAR", True, (255, 255, 255))

        input_box = pygame.Rect(WIDTH // 2 - 150, 300, 300, 40)
        connect_button = pygame.Rect(0, 0, 220, 56)
        connect_button.center = (WIDTH // 2, 400)
        back_button = pygame.Rect(0, 0, 220, 56)
        back_button.center = (WIDTH // 2, 470)

        color_active = pygame.Color('dodgerblue2')
        color_inactive = pygame.Color('lightskyblue3')

        waiting = True
        result = None
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.fill((15, 15, 25))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 140))
            self.screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, 260))

            pygame.draw.rect(self.screen, (255, 255, 255), input_box, border_radius=8)
            pygame.draw.rect(self.screen, color_active if active else color_inactive,
                              input_box, width=2, border_radius=8)
            txt_surface = self.font_label.render(ip_text, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 8, input_box.y + 8))

            connect_color = (85, 220, 125) if connect_button.collidepoint(mouse_pos) else (60, 190, 100)
            pygame.draw.rect(self.screen, connect_color, connect_button, border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), connect_button, width=2, border_radius=14)
            self.screen.blit(connect_text, connect_text.get_rect(center=connect_button.center))

            back_color = (110, 110, 125) if back_button.collidepoint(mouse_pos) else (80, 80, 90)
            pygame.draw.rect(self.screen, back_color, back_button, border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), back_button, width=2, border_radius=14)
            self.screen.blit(back_text, back_text.get_rect(center=back_button.center))

            if error_message:
                err_surface = self.font_label.render(error_message, True, (255, 90, 90))
                self.screen.blit(err_surface, (WIDTH // 2 - err_surface.get_width() // 2, 540))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    if back_button.collidepoint(event.pos):
                        waiting = False
                    elif connect_button.collidepoint(event.pos) and ip_text.strip():
                        client = GameClient()
                        try:
                            client.connect(ip_text.strip(), DEFAULT_PORT)
                            result = client
                            waiting = False
                        except OSError as exc:
                            error_message = f"Falha ao conectar: {exc}"
                elif event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    elif event.key != pygame.K_RETURN:
                        ip_text += event.unicode

        return result
