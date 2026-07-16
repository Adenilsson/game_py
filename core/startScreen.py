"""
Tela inicial (menu): exibe a splash art, permite escolher a nave de
combate (em um carrossel, uma nave grande por vez), pede o nome do
jogador e dá acesso ao botão para começar a partida.
"""

import os
import pygame
from config import WIDTH, HEIGHT

PLAYER_SKINS_DIR = "assets/imagens/naves/player"


class StartScreen:
    """Primeira tela vista pelo jogador: permite escolher a nave, coleta
    o nome e libera o botão JOGAR somente quando um nome válido é
    informado."""

    def __init__(self, screen):
        """Guarda a referência da superfície de desenho, prepara as
        fontes e descobre quais naves (skins) estão disponíveis em
        `assets/imagens/naves/player/`."""
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_button = pygame.font.SysFont(None, 48)
        self.font_input = pygame.font.SysFont(None, 36)
        self.font_arrow = pygame.font.SysFont(None, 64)

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

    def run(self):
        """Exibe o menu inicial em loop, tratando a navegação pelo
        carrossel de naves (setas na tela ou teclas ←/→), a digitação do
        nome e o clique no botão JOGAR (habilitado apenas com nome não
        vazio). Retorna "play" quando o jogador confirma o início da
        partida; a nave escolhida fica disponível em `self.selected_skin`
        após o retorno."""
        splash = pygame.image.load("assets/imagens/telas/splash.jpg").convert_alpha()
        splash = pygame.transform.scale(splash, (WIDTH, HEIGHT))

        title_text = self.font_title.render("Meu Jogo Topdown", True, (255, 255, 255))
        play_text = self.font_button.render("JOGAR", True, (0, 0, 0))

        title_y = int(HEIGHT * 0.12)

        # --- Seleção de nave: carrossel com uma nave grande por vez ---
        ship_label_text = self.font_input.render("Escolha sua nave:", True, (255, 255, 255))
        ship_label_y = title_y + 100
        ship_image_size = 120
        carousel_y = ship_label_y + 40

        left_arrow_text = self.font_arrow.render("<", True, (255, 255, 255))
        right_arrow_text = self.font_arrow.render(">", True, (255, 255, 255))

        arrow_width = 50
        arrow_gap = 20
        carousel_total_width = arrow_width * 2 + arrow_gap * 2 + ship_image_size
        carousel_start_x = WIDTH // 2 - carousel_total_width // 2

        left_arrow_rect = pygame.Rect(carousel_start_x, carousel_y, arrow_width, ship_image_size)
        ship_image_rect = pygame.Rect(left_arrow_rect.right + arrow_gap, carousel_y, ship_image_size, ship_image_size)
        right_arrow_rect = pygame.Rect(ship_image_rect.right + arrow_gap, carousel_y, arrow_width, ship_image_size)

        # Só há navegação se houver mais de uma nave disponível
        show_arrows = len(self.available_skins) > 1

        ship_images = []
        for skin in self.available_skins:
            thumb_path = os.path.join(PLAYER_SKINS_DIR, skin, "aviao_0.png")
            img = pygame.image.load(thumb_path).convert_alpha()
            img = pygame.transform.scale(img, (ship_image_size, ship_image_size))
            ship_images.append(img)

        skin_name_y = carousel_y + ship_image_size + 15

        # --- Nome do jogador ---
        name_label_y = skin_name_y + 45
        label_text = self.font_input.render("Informe seu nome:", True, (255, 255, 255))

        input_box = pygame.Rect(WIDTH // 2 - 150, name_label_y + 35, 300, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False

        play_button = play_text.get_rect(center=(WIDTH // 2, input_box.bottom + 60))
        button_bg = pygame.Rect(play_button.x - 20, play_button.y - 10,
                                play_button.width + 40, play_button.height + 20)

        waiting = True
        action = None
        self.start_sound = pygame.mixer.Sound("assets/sons/introducao.mp3")
        self.start_sound.play()
        while waiting:

            self.screen.blit(splash, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, title_y))

            # --- Carrossel de naves ---
            self.screen.blit(ship_label_text, (WIDTH // 2 - ship_label_text.get_width() // 2, ship_label_y))

            if show_arrows:
                pygame.draw.rect(self.screen, (40, 40, 40), left_arrow_rect)
                self.screen.blit(left_arrow_text, left_arrow_text.get_rect(center=left_arrow_rect.center))

                pygame.draw.rect(self.screen, (40, 40, 40), right_arrow_rect)
                self.screen.blit(right_arrow_text, right_arrow_text.get_rect(center=right_arrow_rect.center))

            image_bg = ship_image_rect.inflate(10, 10)
            pygame.draw.rect(self.screen, (40, 40, 40), image_bg)
            pygame.draw.rect(self.screen, (255, 255, 255), image_bg, 3)
            self.screen.blit(ship_images[self.selected_skin_index], ship_image_rect)

            skin_name = self._skin_display_name(self.available_skins[self.selected_skin_index])
            if len(self.available_skins) > 1:
                skin_name += f"  ({self.selected_skin_index + 1}/{len(self.available_skins)})"
            skin_name_text = self.font_input.render(skin_name, True, (255, 255, 255))
            self.screen.blit(skin_name_text, (WIDTH // 2 - skin_name_text.get_width() // 2, skin_name_y))

            # --- Nome do jogador ---
            self.screen.blit(label_text, (WIDTH // 2 - label_text.get_width() // 2, name_label_y))

            pygame.draw.rect(self.screen, color, input_box, 2)
            txt_surface = self.font_input.render(self.player_name, True, (255, 255, 255))
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

            # botão jogar (desabilitado se nome vazio)
            if self.player_name.strip() != "":
                pygame.draw.rect(self.screen, (255, 255, 255), button_bg)
                self.screen.blit(play_text, play_button)
            else:
                # botão cinza desabilitado
                pygame.draw.rect(self.screen, (150, 150, 150), button_bg)
                disabled_text = self.font_button.render("JOGAR", True, (50, 50, 50))
                self.screen.blit(disabled_text, play_button)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
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

                    if button_bg.collidepoint(event.pos) and self.player_name.strip() != "":
                        action = "play"
                        waiting = False
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
