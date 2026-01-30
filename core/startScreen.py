import pygame
from config import WIDTH, HEIGHT

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_button = pygame.font.SysFont(None, 48)
        self.font_input = pygame.font.SysFont(None, 36)

        self.player_name = ""  # nome digitado

    def run(self):
        splash = pygame.image.load("assets/splash.jpg").convert_alpha()
        splash = pygame.transform.scale(splash, (WIDTH, HEIGHT))

        title_text = self.font_title.render("Meu Jogo Topdown", True, (255,255,255))
        play_text = self.font_button.render("JOGAR", True, (0,0,0))

        play_button = play_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
        button_bg = pygame.Rect(play_button.x-20, play_button.y-10,
                                play_button.width+40, play_button.height+20)

        # Campo de texto
        input_box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False

        # Label pedindo nome
        label_text = self.font_input.render("Informe seu nome:", True, (255,255,255))

        waiting = True
        action = None

        while waiting:
            self.screen.blit(splash, (0,0))
            self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))

            # label acima do campo
            self.screen.blit(label_text, (WIDTH//2 - label_text.get_width()//2, HEIGHT//2 - 40))

            # campo de texto
            pygame.draw.rect(self.screen, color, input_box, 2)
            txt_surface = self.font_input.render(self.player_name, True, (255,255,255))
            self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))

            # botão jogar (desabilitado se nome vazio)
            if self.player_name.strip() != "":
                pygame.draw.rect(self.screen, (255,255,255), button_bg)
                self.screen.blit(play_text, play_button)
            else:
                # botão cinza desabilitado
                pygame.draw.rect(self.screen, (150,150,150), button_bg)
                disabled_text = self.font_button.render("JOGAR", True, (50,50,50))
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
                    if button_bg.collidepoint(event.pos) and self.player_name.strip() != "":
                        print("================")
                        action = "play"
                        waiting = False
                elif event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            active = False
                            color = color_inactive
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        else:
                            self.player_name += event.unicode

        return action
