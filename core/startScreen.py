"""
Tela inicial (menu): exibe a splash art, permite escolher a nave de
combate em um painel de seleção grande (carrossel com uma nave por vez),
pede o nome do jogador e dá acesso ao botão para começar a partida.
"""

import math
import os
import pygame
from config import WIDTH, HEIGHT
from core.settings import settings
from core.settings_screen import SettingsScreen
from core.highscore import load_high_score
from core.skins import PLAYER_SKINS_DIR, discover_skins

# Cores usadas nos botões da tela inicial (a cor de destaque, usada no
# botão JOGAR e na seleção de nave, vem de `settings.accent_color` e é
# configurável pelo jogador na tela de configurações)
PANEL_COLOR = (20, 20, 30, 185)
PANEL_BORDER_COLOR = (255, 255, 255, 220)
ARROW_COLOR = (70, 70, 95)
ARROW_HOVER_COLOR = (105, 105, 145)
PLAY_DISABLED_COLOR = (90, 90, 90)
GEAR_COLOR = (70, 70, 95)
GEAR_HOVER_COLOR = (105, 105, 145)
EXIT_COLOR = (150, 55, 55)
EXIT_HOVER_COLOR = (190, 75, 75)
LOCKED_BORDER_COLOR = (140, 140, 140)
LOCKED_TEXT_COLOR = (255, 110, 110)

# Sistema de desbloqueio de naves por recorde: a primeira nave está
# sempre disponível; cada nave seguinte exige um recorde maior que a
# anterior, com incrementos crescentes (100, 250, 450, 700, 1000, ...)
UNLOCK_BASE_SCORE = 100
UNLOCK_SCORE_STEP = 50


def _lighten(color, amount=30):
    """Clareia uma cor RGB somando `amount` a cada canal, sem estourar 255."""
    return tuple(min(255, c + amount) for c in color)


def _unlock_score_for_index(index):
    """Retorna o recorde necessário para desbloquear a nave na posição
    `index` do carrossel (0 = primeira nave, sempre desbloqueada). Os
    incrementos crescem a cada nave: 100, 250, 450, 700, 1000, ..."""
    if index <= 0:
        return 0
    total = 0
    increment = UNLOCK_BASE_SCORE
    for _ in range(index):
        total += increment
        increment += UNLOCK_SCORE_STEP
    return total


class StartScreen:
    """Primeira tela vista pelo jogador: permite escolher a nave em um
    painel de seleção destacado, coleta o nome e libera o botão JOGAR
    somente quando um nome válido é informado."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho, prepara as
        fontes e descobre quais naves (skins) estão disponíveis em
        `assets/imagens/naves/player/`."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_button = pygame.font.SysFont(None, 48)
        self.font_input = pygame.font.SysFont(None, 36)
        self.font_lock = pygame.font.SysFont(None, 22)

        self.player_name = ""  # nome digitado
        self.available_skins = discover_skins()
        self.selected_skin_index = 0
        self.selected_skin = self.available_skins[0]

        self.settings_screen = SettingsScreen(screen)

    def _skin_display_name(self, skin):
        """Converte o nome da pasta (ex.: "player_1") em um rótulo
        amigável (ex.: "Player 1") para exibir na tela."""
        return skin.replace("_", " ").title()

    def _draw_panel(self, panel_surface, panel_rect):
        """Desenha o painel de fundo semitransparente e arredondado que
        destaca toda a área de seleção de nave."""
        self.screen.blit(panel_surface, panel_rect.topleft)

    def _draw_arrow_button(self, rect, direction, hovered):
        """Desenha um botão de seta arredondado (esquerda/direita) com
        destaque ao passar o mouse por cima e um triângulo indicando a
        direção da navegação."""
        color = ARROW_HOVER_COLOR if hovered else ARROW_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)

        cx, cy = rect.center
        size = 16
        if direction == "left":
            points = [(cx + size // 2, cy - size), (cx + size // 2, cy + size), (cx - size // 2, cy)]
        else:
            points = [(cx - size // 2, cy - size), (cx - size // 2, cy + size), (cx + size // 2, cy)]
        pygame.draw.polygon(self.screen, (255, 255, 255), points)

    def _draw_play_button(self, rect, text_surface, enabled, hovered):
        """Desenha o botão JOGAR arredondado, usando a cor de destaque
        escolhida pelo jogador (mais clara ao passar o mouse) ou cinza
        quando o nome ainda está vazio."""
        if not enabled:
            color = PLAY_DISABLED_COLOR
        elif hovered:
            color = _lighten(settings.accent_color)
        else:
            color = settings.accent_color
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _draw_exit_button(self, rect, text_surface, hovered):
        """Desenha o botão SAIR, em vermelho para sinalizar que encerra
        o jogo, mais claro ao passar o mouse por cima."""
        color = EXIT_HOVER_COLOR if hovered else EXIT_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _draw_gear_button(self, rect, hovered):
        """Desenha o botão de configurações (engrenagem) no canto
        superior direito da tela, destacando-se ao passar o mouse."""
        bg_color = GEAR_HOVER_COLOR if hovered else GEAR_COLOR
        pygame.draw.circle(self.screen, bg_color, rect.center, rect.width // 2)
        pygame.draw.circle(self.screen, (255, 255, 255), rect.center, rect.width // 2, width=2)

        cx, cy = rect.center
        radius = rect.width // 2
        inner_radius = radius * 0.55
        teeth = 8
        for i in range(teeth):
            angle = (2 * math.pi / teeth) * i
            x1 = cx + math.cos(angle) * inner_radius
            y1 = cy + math.sin(angle) * inner_radius
            x2 = cx + math.cos(angle) * (radius - 2)
            y2 = cy + math.sin(angle) * (radius - 2)
            pygame.draw.line(self.screen, (255, 255, 255), (x1, y1), (x2, y2), width=3)
        pygame.draw.circle(self.screen, bg_color, rect.center, int(radius * 0.28))

    def run(self):
        """Exibe o menu inicial em loop, tratando a navegação pelo painel
        de seleção de naves (setas na tela ou teclas ←/→), a digitação do
        nome e o clique no botão JOGAR (habilitado apenas com nome não
        vazio). Retorna "play" quando o jogador confirma o início da
        partida; a nave escolhida fica disponível em `self.selected_skin`
        após o retorno."""
        splash = pygame.image.load("assets/imagens/telas/splash.jpg").convert_alpha()
        splash = pygame.transform.scale(splash, (WIDTH, HEIGHT))

        title_text = self.font_title.render("Meu Jogo Topdown", True, (255, 255, 255))
        play_text_enabled = self.font_button.render("JOGAR", True, (255, 255, 255))
        play_text_disabled = self.font_button.render("JOGAR", True, (160, 160, 160))
        exit_text = self.font_button.render("SAIR", True, (255, 255, 255))

        title_y = 55

        # --- Painel de seleção de nave (maior, com uma nave grande por vez) ---
        ship_label_text = self.font_input.render("Escolha sua nave:", True, (255, 255, 255))
        ship_label_y = 165
        carousel_y = ship_label_y + 45
        ship_image_size = 180

        arrow_width = 60
        arrow_gap = 25
        carousel_total_width = arrow_width * 2 + arrow_gap * 2 + ship_image_size
        carousel_start_x = WIDTH // 2 - carousel_total_width // 2

        left_arrow_rect = pygame.Rect(carousel_start_x, carousel_y, arrow_width, ship_image_size)
        ship_image_rect = pygame.Rect(left_arrow_rect.right + arrow_gap, carousel_y, ship_image_size, ship_image_size)
        right_arrow_rect = pygame.Rect(ship_image_rect.right + arrow_gap, carousel_y, arrow_width, ship_image_size)

        show_arrows = len(self.available_skins) > 1

        # --- Sistema de desbloqueio por recorde ---
        # A primeira nave (índice 0) está sempre disponível; as demais
        # exigem o recorde mínimo calculado por `_unlock_score_for_index`.
        self.high_score = load_high_score()
        unlock_thresholds = [_unlock_score_for_index(i) for i in range(len(self.available_skins))]
        unlocked_flags = [self.high_score >= threshold for threshold in unlock_thresholds]

        ship_images = []
        ship_images_locked = []
        for skin in self.available_skins:
            thumb_path = os.path.join(PLAYER_SKINS_DIR, skin, "aviao_0.png")
            img = pygame.image.load(thumb_path).convert_alpha()
            img = pygame.transform.scale(img, (ship_image_size, ship_image_size))
            ship_images.append(img)

            locked_path = os.path.join(PLAYER_SKINS_DIR, skin, "aviao_b.png")
            if os.path.isfile(locked_path):
                locked_img = pygame.image.load(locked_path).convert_alpha()
                locked_img = pygame.transform.scale(locked_img, (ship_image_size, ship_image_size))
            else:
                locked_img = img
            ship_images_locked.append(locked_img)

        skin_name_y = carousel_y + ship_image_size + 15
        # Altura reservada para a linha de nome (nave desbloqueada) ou as
        # duas linhas da mensagem de bloqueio (nave ainda trancada) — fixa,
        # para o painel não mudar de tamanho ao navegar entre naves.
        lock_line_height = 22
        skin_info_height = lock_line_height * 2 + 6

        panel_padding_x = 30
        panel_padding_top = 20
        panel_padding_bottom = 20
        panel_rect = pygame.Rect(
            WIDTH // 2 - carousel_total_width // 2 - panel_padding_x,
            ship_label_y - panel_padding_top,
            carousel_total_width + panel_padding_x * 2,
            (skin_name_y + skin_info_height + panel_padding_bottom) - (ship_label_y - panel_padding_top),
        )
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, PANEL_COLOR, panel_surface.get_rect(), border_radius=24)
        pygame.draw.rect(panel_surface, PANEL_BORDER_COLOR, panel_surface.get_rect(), width=2, border_radius=24)

        # --- Nome do jogador ---
        name_label_y = panel_rect.bottom + 25
        label_text = self.font_input.render("Informe seu nome:", True, (255, 255, 255))

        input_box = pygame.Rect(WIDTH // 2 - 150, name_label_y + 35, 300, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False

        play_button = pygame.Rect(0, 0, 200, 56)
        play_button.center = (WIDTH // 2, input_box.bottom + 60)

        # --- Botão SAIR (abaixo do botão JOGAR, encerra o jogo) ---
        exit_button = pygame.Rect(0, 0, 200, 56)
        exit_button.center = (WIDTH // 2, play_button.bottom + 45)

        # --- Botão de configurações (canto superior direito) ---
        gear_button = pygame.Rect(0, 0, 48, 48)
        gear_button.topright = (WIDTH - 20, 20)

        waiting = True
        action = None
        self.start_sound = settings.load_sound("assets/sons/introducao.mp3")
        settings.play_sound(self.start_sound)
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(splash, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, title_y))
            self._draw_gear_button(gear_button, gear_button.collidepoint(mouse_pos))

            # --- Painel de seleção de nave ---
            self._draw_panel(panel_surface, panel_rect)
            self.screen.blit(ship_label_text, (WIDTH // 2 - ship_label_text.get_width() // 2, ship_label_y))

            if show_arrows:
                self._draw_arrow_button(left_arrow_rect, "left", left_arrow_rect.collidepoint(mouse_pos))
                self._draw_arrow_button(right_arrow_rect, "right", right_arrow_rect.collidepoint(mouse_pos))

            skin_unlocked = unlocked_flags[self.selected_skin_index]

            image_bg = ship_image_rect.inflate(10, 10)
            pygame.draw.rect(self.screen, (40, 40, 40), image_bg, border_radius=10)
            border_color = settings.accent_color if skin_unlocked else LOCKED_BORDER_COLOR
            pygame.draw.rect(self.screen, border_color, image_bg, width=3, border_radius=10)
            image_to_show = ship_images[self.selected_skin_index] if skin_unlocked else ship_images_locked[self.selected_skin_index]
            self.screen.blit(image_to_show, ship_image_rect)

            if skin_unlocked:
                skin_name = self._skin_display_name(self.available_skins[self.selected_skin_index])
                if len(self.available_skins) > 1:
                    skin_name += f"  ({self.selected_skin_index + 1}/{len(self.available_skins)})"
                skin_name_text = self.font_input.render(skin_name, True, (255, 255, 255))
                self.screen.blit(skin_name_text, (WIDTH // 2 - skin_name_text.get_width() // 2, skin_name_y))
            else:
                needed = unlock_thresholds[self.selected_skin_index]
                lock_line1 = self.font_lock.render("Nave bloqueada", True, LOCKED_TEXT_COLOR)
                lock_line2 = self.font_lock.render(
                    f"Recorde necessário: {needed} (seu recorde: {self.high_score})",
                    True, LOCKED_TEXT_COLOR,
                )
                self.screen.blit(lock_line1, (WIDTH // 2 - lock_line1.get_width() // 2, skin_name_y))
                self.screen.blit(lock_line2, (WIDTH // 2 - lock_line2.get_width() // 2, skin_name_y + lock_line_height))

            # --- Nome do jogador ---
            self.screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, name_label_y))

            pygame.draw.rect(self.screen, (255, 255, 255), input_box, border_radius=8)
            pygame.draw.rect(self.screen, color, input_box, width=2, border_radius=8)
            txt_surface = self.font_input.render(self.player_name, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 8, input_box.y + 5))

            # botão jogar (desabilitado se nome vazio ou nave bloqueada)
            name_filled = self.player_name.strip() != ""
            can_play = name_filled and skin_unlocked
            play_text = play_text_enabled if can_play else play_text_disabled
            self._draw_play_button(play_button, play_text, can_play, play_button.collidepoint(mouse_pos))

            # botão sair (encerra o jogo)
            self._draw_exit_button(exit_button, exit_text, exit_button.collidepoint(mouse_pos))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if gear_button.collidepoint(event.pos):
                        self.settings_screen.run()
                        continue

                    if input_box.collidepoint(event.pos):
                        active = True
                        color = color_active
                    else:
                        active = False
                        color = color_inactive

                    if show_arrows and left_arrow_rect.collidepoint(event.pos):
                        self.selected_skin_index = (self.selected_skin_index - 1) % len(self.available_skins)
                    elif show_arrows and right_arrow_rect.collidepoint(event.pos):
                        self.selected_skin_index = (self.selected_skin_index + 1) % len(self.available_skins)

                    if play_button.collidepoint(event.pos) and can_play:
                        action = "play"
                        waiting = False

                    if exit_button.collidepoint(event.pos):
                        pygame.quit()
                        exit()
                elif event.type == pygame.KEYDOWN:
                    if show_arrows and event.key == pygame.K_LEFT:
                        self.selected_skin_index = (self.selected_skin_index - 1) % len(self.available_skins)
                    elif show_arrows and event.key == pygame.K_RIGHT:
                        self.selected_skin_index = (self.selected_skin_index + 1) % len(self.available_skins)
                    elif active:
                        if event.key == pygame.K_RETURN:
                            active = False
                            color = color_inactive
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            self.player_name += event.unicode

        self.selected_skin = self.available_skins[self.selected_skin_index]
        return action
