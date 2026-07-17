"""
Tela inicial (menu): exibe a splash art, permite escolher a nave de
combate em um painel de seleção grande (carrossel com uma nave por vez),
pede o nome do jogador e dá acesso ao botão para começar a partida.
"""

import asyncio
import os
import pygame
from config import WIDTH, HEIGHT

PLAYER_SKINS_DIR = "assets/imagens/naves/player"

# Cores usadas nos botões da tela inicial
PANEL_COLOR = (20, 20, 30, 185)
PANEL_BORDER_COLOR = (255, 255, 255, 220)
ARROW_COLOR = (70, 70, 95)
ARROW_HOVER_COLOR = (105, 105, 145)
PLAY_COLOR = (60, 190, 100)
PLAY_HOVER_COLOR = (85, 220, 125)
PLAY_DISABLED_COLOR = (90, 90, 90)
EXIT_COLOR = (190, 60, 60)
EXIT_HOVER_COLOR = (220, 85, 85)

# Teclado virtual desenhado na tela (usado no lugar do teclado do sistema,
# que não abre de forma confiável dentro do runtime web/WASM em celulares)
KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
MAX_NAME_LEN = 14


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

        self.font_key = pygame.font.SysFont(None, 30)

        self.player_name = ""  # nome digitado
        self.available_skins = self._discover_skins()
        self.selected_skin_index = 0
        self.selected_skin = self.available_skins[0]

    def _discover_skins(self):
        """Lista as subpastas de naves disponíveis em `PLAYER_SKINS_DIR`
        (ex.: "player_1", "player_2"), em ordem alfabética. Se a pasta não
        existir ou estiver vazia, assume apenas "player_1" como padrão."""
        if not os.path.isdir(PLAYER_SKINS_DIR):
            return ["player_1"]
        skins = sorted(
            name for name in os.listdir(PLAYER_SKINS_DIR)
            if os.path.isdir(os.path.join(PLAYER_SKINS_DIR, name))
        )
        return skins or ["player_1"]

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
        """Desenha o botão JOGAR arredondado, com cor esverdeada quando
        habilitado (mais clara ao passar o mouse) e cinza quando o nome
        ainda está vazio."""
        if not enabled:
            color = PLAY_DISABLED_COLOR
        elif hovered:
            color = PLAY_HOVER_COLOR
        else:
            color = PLAY_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _draw_exit_button(self, rect, text_surface, hovered):
        """Desenha o botão SAIR arredondado, abaixo do botão JOGAR, com
        destaque avermelhado ao passar o mouse por cima."""
        color = EXIT_HOVER_COLOR if hovered else EXIT_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=14)
        self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    async def run(self):
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

        ship_images = []
        for skin in self.available_skins:
            thumb_path = os.path.join(PLAYER_SKINS_DIR, skin, "aviao_0.png")
            img = pygame.image.load(thumb_path).convert_alpha()
            img = pygame.transform.scale(img, (ship_image_size, ship_image_size))
            ship_images.append(img)

        skin_name_y = carousel_y + ship_image_size + 15

        panel_padding_x = 30
        panel_padding_top = 20
        panel_padding_bottom = 20
        panel_rect = pygame.Rect(
            WIDTH // 2 - carousel_total_width // 2 - panel_padding_x,
            ship_label_y - panel_padding_top,
            carousel_total_width + panel_padding_x * 2,
            (skin_name_y + 30 + panel_padding_bottom) - (ship_label_y - panel_padding_top),
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

        # --- Teclado virtual (aparece no lugar do painel de naves/JOGAR/SAIR
        # enquanto o campo de nome está ativo) ---
        key_w, key_h, key_gap = 50, 42, 4

        def _build_row(chars, y):
            total_w = len(chars) * key_w + (len(chars) - 1) * key_gap
            start_x = WIDTH // 2 - total_w // 2
            return [
                (pygame.Rect(start_x + i * (key_w + key_gap), y, key_w, key_h), ch)
                for i, ch in enumerate(chars)
            ]

        keyboard_top = input_box.bottom + 15
        keyboard_keys = []
        for row_index, row_chars in enumerate(KEY_ROWS):
            keyboard_keys += _build_row(row_chars, keyboard_top + row_index * (key_h + key_gap))

        special_y = keyboard_top + len(KEY_ROWS) * (key_h + key_gap)
        space_rect = pygame.Rect(0, 0, 220, key_h)
        del_rect = pygame.Rect(0, 0, 140, key_h)
        ok_rect = pygame.Rect(0, 0, 140, key_h)
        total_special_w = space_rect.width + del_rect.width + ok_rect.width + 2 * key_gap
        special_start_x = WIDTH // 2 - total_special_w // 2
        space_rect.topleft = (special_start_x, special_y)
        del_rect.topleft = (space_rect.right + key_gap, special_y)
        ok_rect.topleft = (del_rect.right + key_gap, special_y)

        del_text = self.font_key.render("DEL", True, (255, 255, 255))
        ok_text = self.font_key.render("OK", True, (255, 255, 255))
        space_text = self.font_key.render("ESPAÇO", True, (255, 255, 255))

        play_button = pygame.Rect(0, 0, 200, 56)
        play_button.center = (WIDTH // 2, input_box.bottom + 60)

        exit_button = pygame.Rect(0, 0, 200, 56)
        exit_button.center = (WIDTH // 2, play_button.bottom + 30 + exit_button.height // 2)

        waiting = True
        action = None
        self.start_sound = pygame.mixer.Sound("assets/sons/introducao.ogg")
        self.start_sound.play()
        while waiting:
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(splash, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, title_y))

            name_filled = self.player_name.strip() != ""

            if not active:
                # --- Painel de seleção de nave ---
                self._draw_panel(panel_surface, panel_rect)
                self.screen.blit(ship_label_text, (WIDTH // 2 - ship_label_text.get_width() // 2, ship_label_y))

                if show_arrows:
                    self._draw_arrow_button(left_arrow_rect, "left", left_arrow_rect.collidepoint(mouse_pos))
                    self._draw_arrow_button(right_arrow_rect, "right", right_arrow_rect.collidepoint(mouse_pos))

                image_bg = ship_image_rect.inflate(10, 10)
                pygame.draw.rect(self.screen, (40, 40, 40), image_bg, border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), image_bg, width=3, border_radius=10)
                self.screen.blit(ship_images[self.selected_skin_index], ship_image_rect)

                skin_name = self._skin_display_name(self.available_skins[self.selected_skin_index])
                if len(self.available_skins) > 1:
                    skin_name += f"  ({self.selected_skin_index + 1}/{len(self.available_skins)})"
                skin_name_text = self.font_input.render(skin_name, True, (255, 255, 255))
                self.screen.blit(skin_name_text, (WIDTH // 2 - skin_name_text.get_width() // 2, skin_name_y))

            # --- Nome do jogador ---
            self.screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, name_label_y))

            pygame.draw.rect(self.screen, (255, 255, 255), input_box, border_radius=8)
            pygame.draw.rect(self.screen, color, input_box, width=2, border_radius=8)
            txt_surface = self.font_input.render(self.player_name, True, (0, 0, 0))
            self.screen.blit(txt_surface, (input_box.x + 8, input_box.y + 5))

            if active:
                # --- Teclado virtual ---
                for rect, ch in keyboard_keys:
                    hovered = rect.collidepoint(mouse_pos)
                    color_key = ARROW_HOVER_COLOR if hovered else ARROW_COLOR
                    pygame.draw.rect(self.screen, color_key, rect, border_radius=8)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, width=1, border_radius=8)
                    ch_surface = self.font_key.render(ch, True, (255, 255, 255))
                    self.screen.blit(ch_surface, ch_surface.get_rect(center=rect.center))

                space_hovered = space_rect.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, ARROW_HOVER_COLOR if space_hovered else ARROW_COLOR, space_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 255, 255), space_rect, width=1, border_radius=8)
                self.screen.blit(space_text, space_text.get_rect(center=space_rect.center))

                del_hovered = del_rect.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, EXIT_HOVER_COLOR if del_hovered else EXIT_COLOR, del_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 255, 255), del_rect, width=1, border_radius=8)
                self.screen.blit(del_text, del_text.get_rect(center=del_rect.center))

                ok_hovered = ok_rect.collidepoint(mouse_pos)
                pygame.draw.rect(self.screen, PLAY_HOVER_COLOR if ok_hovered else PLAY_COLOR, ok_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 255, 255), ok_rect, width=1, border_radius=8)
                self.screen.blit(ok_text, ok_text.get_rect(center=ok_rect.center))
            else:
                # botão jogar (desabilitado se nome vazio)
                play_text = play_text_enabled if name_filled else play_text_disabled
                self._draw_play_button(play_button, play_text, name_filled, play_button.collidepoint(mouse_pos))

                # botão sair
                self._draw_exit_button(exit_button, exit_text, exit_button.collidepoint(mouse_pos))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = True
                        color = color_active
                        # Também tenta abrir o teclado do sistema quando
                        # disponível (funciona no desktop; em navegadores
                        # móveis não é confiável, por isso o teclado virtual
                        # desenhado na tela é o caminho principal)
                        pygame.key.start_text_input()
                        pygame.key.set_text_input_rect(input_box)
                    elif active:
                        # --- cliques no teclado virtual ---
                        hit_letter = False
                        for rect, ch in keyboard_keys:
                            if rect.collidepoint(event.pos):
                                if len(self.player_name) < MAX_NAME_LEN:
                                    self.player_name += ch
                                hit_letter = True
                                break

                        close_keyboard = False
                        if hit_letter:
                            pass
                        elif space_rect.collidepoint(event.pos):
                            if len(self.player_name) < MAX_NAME_LEN:
                                self.player_name += " "
                        elif del_rect.collidepoint(event.pos):
                            self.player_name = self.player_name[:-1]
                        elif ok_rect.collidepoint(event.pos):
                            close_keyboard = True
                        else:
                            # toque fora do teclado: fecha
                            close_keyboard = True

                        if close_keyboard:
                            active = False
                            color = color_inactive
                            pygame.key.stop_text_input()
                    else:
                        # navegação normal (só quando o teclado não está aberto)
                        if show_arrows and left_arrow_rect.collidepoint(event.pos):
                            self.selected_skin_index = (self.selected_skin_index - 1) % len(self.available_skins)
                        elif show_arrows and right_arrow_rect.collidepoint(event.pos):
                            self.selected_skin_index = (self.selected_skin_index + 1) % len(self.available_skins)
                        elif play_button.collidepoint(event.pos) and name_filled:
                            action = "play"
                            waiting = False
                        elif exit_button.collidepoint(event.pos):
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
                            pygame.key.stop_text_input()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                elif event.type == pygame.TEXTINPUT:
                    # Caracteres digitados (teclado físico, virtual ou IME)
                    # chegam por aqui, não por KEYDOWN.
                    if active and len(self.player_name) < MAX_NAME_LEN:
                        self.player_name += event.text

            await asyncio.sleep(0)

        pygame.key.stop_text_input()
        self.selected_skin = self.available_skins[self.selected_skin_index]
        return action
