"""
Tela de configurações: permite ajustar o volume dos efeitos sonoros
(slider arrastável) e escolher a cor de destaque da interface do jogo.
"""

import pygame
from config import WIDTH, HEIGHT
from core.settings import settings, ACCENT_COLOR_OPTIONS


def _lighten(color, amount=35):
    """Clareia uma cor RGB somando `amount` a cada canal, sem estourar 255."""
    return tuple(min(255, c + amount) for c in color)


class SettingsScreen:
    """Tela de ajustes acessível pelo botão de engrenagem na tela
    inicial. Altera o volume geral dos efeitos sonoros e a cor de
    destaque usada nos botões e realces da interface, salvando as
    mudanças imediatamente em `settings.json`."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho e prepara as fontes."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 56)
        self.font_label = pygame.font.SysFont(None, 32)
        self.font_button = pygame.font.SysFont(None, 40)

    def _volume_from_pos(self, x, slider_rect):
        """Converte a posição X do mouse em um valor de volume (0.0 a
        1.0) proporcional à posição dentro do slider."""
        ratio = (x - slider_rect.x) / slider_rect.width
        return round(max(0.0, min(1.0, ratio)), 2)

    def run(self):
        """Exibe a tela de configurações em loop até o jogador clicar em
        VOLTAR. Ajustes de volume e cor são aplicados e persistidos
        assim que o jogador solta o slider ou escolhe uma cor."""
        title_text = self.font_title.render("Configurações", True, (255, 255, 255))

        # --- Slider de volume ---
        slider_label = self.font_label.render("Volume dos efeitos sonoros", True, (255, 255, 255))
        slider_y = 260
        slider_rect = pygame.Rect(WIDTH // 2 - 150, slider_y, 300, 8)
        handle_radius = 13
        dragging_slider = False

        # --- Paleta de cores de destaque ---
        color_label = self.font_label.render("Cor de destaque", True, (255, 255, 255))
        color_y = 400
        swatch_size = 50
        swatch_gap = 20
        total_w = len(ACCENT_COLOR_OPTIONS) * swatch_size + (len(ACCENT_COLOR_OPTIONS) - 1) * swatch_gap
        swatches_start_x = WIDTH // 2 - total_w // 2
        swatch_rects = [
            pygame.Rect(swatches_start_x + i * (swatch_size + swatch_gap), color_y, swatch_size, swatch_size)
            for i in range(len(ACCENT_COLOR_OPTIONS))
        ]

        back_text = self.font_button.render("VOLTAR", True, (255, 255, 255))
        back_button = pygame.Rect(0, 0, 200, 56)
        back_button.center = (WIDTH // 2, HEIGHT - 110)

        waiting = True
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.fill((20, 20, 30))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 110))

            # --- Slider de volume ---
            self.screen.blit(slider_label, (WIDTH // 2 - slider_label.get_width() // 2, slider_y - 45))
            pygame.draw.rect(self.screen, (80, 80, 80), slider_rect, border_radius=4)
            fill_width = int(slider_rect.width * settings.volume)
            fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, fill_width, slider_rect.height)
            pygame.draw.rect(self.screen, settings.accent_color, fill_rect, border_radius=4)

            handle_pos = (slider_rect.x + fill_width, slider_rect.centery)
            pygame.draw.circle(self.screen, (255, 255, 255), handle_pos, handle_radius)
            pygame.draw.circle(self.screen, settings.accent_color, handle_pos, handle_radius, width=3)

            vol_text = self.font_label.render(f"{int(round(settings.volume * 100))}%", True, (255, 255, 255))
            self.screen.blit(vol_text, (slider_rect.right + 25, slider_rect.centery - vol_text.get_height() // 2))

            # --- Paleta de cores ---
            self.screen.blit(color_label, (WIDTH // 2 - color_label.get_width() // 2, color_y - 45))
            for rect, color in zip(swatch_rects, ACCENT_COLOR_OPTIONS):
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                if tuple(color) == tuple(settings.accent_color):
                    pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(8, 8), width=3, border_radius=10)
                elif rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(4, 4), width=2, border_radius=9)

            # --- Botão voltar ---
            back_color = _lighten(settings.accent_color) if back_button.collidepoint(mouse_pos) else (80, 80, 80)
            pygame.draw.rect(self.screen, back_color, back_button, border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), back_button, width=2, border_radius=14)
            self.screen.blit(back_text, back_text.get_rect(center=back_button.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    slider_hit_area = slider_rect.inflate(0, handle_radius * 2)
                    if slider_hit_area.collidepoint(event.pos):
                        dragging_slider = True
                        settings.set_volume(self._volume_from_pos(event.pos[0], slider_rect))

                    for rect, color in zip(swatch_rects, ACCENT_COLOR_OPTIONS):
                        if rect.collidepoint(event.pos):
                            settings.accent_color = color
                            settings.save()

                    if back_button.collidepoint(event.pos):
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging_slider:
                        dragging_slider = False
                        settings.save()
                elif event.type == pygame.MOUSEMOTION:
                    if dragging_slider:
                        settings.set_volume(self._volume_from_pos(event.pos[0], slider_rect))
