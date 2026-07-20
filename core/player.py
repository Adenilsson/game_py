"""
Classe do jogador: nave controlada pelo usuário, com movimentação,
troca de armas, vida e elementos de HUD (barra de vida e munição).
"""

import pygame
from config import WIDTH, HEIGHT
from config import WEAPON_COLORS
from core.settings import settings
from core.skins import skin_tier
from core.weapon_loadouts import build_weapons

STARTING_LIVES = 2  # quantas vidas o jogador tem ao começar a partida
RESPAWN_INVULNERABILITY_MS = 2000  # tempo imune a dano logo apos reaparecer


class Player(pygame.sprite.Sprite):
    """Nave do jogador. Controla movimento, disparo, troca de armas,
    dano recebido e desenho dos elementos de HUD associados a ela."""

    def __init__(self, skin="player_1", name=""):
        """Carrega os sprites da nave (parado, virando à esquerda/direita)
        a partir da pasta de skin escolhida em `assets/imagens/naves/player/`,
        monta o arsenal de armas disponíveis e define posição inicial e vida.

        skin: nome da subpasta com os sprites da nave (ex.: "player_1",
        "player_2"), escolhida pelo jogador na tela inicial.
        name: nome digitado pelo jogador na tela inicial, usado para
        identificá-lo durante partidas cooperativas (ver `draw_name_tag`).
        """
        super().__init__()
        self.skin = skin  # guardado para o modo cooperativo em rede reconstruir a nave
        self.name = name

        # Carrega sprite da nave de acordo com a skin escolhida
        skin_dir = f"assets/imagens/naves/player/{skin}"
        self.image_idle = pygame.image.load(f"{skin_dir}/aviao_0.png").convert_alpha()
        self.image_idle = pygame.transform.scale(self.image_idle, (70, 70))

        self.image_right = pygame.image.load(f"{skin_dir}/aviao_d.png").convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (70, 70))

        self.image_left = pygame.image.load(f"{skin_dir}/aviao_e.png").convert_alpha()
        self.image_left = pygame.transform.scale(self.image_left, (70, 70))

        # Arsenal de armas disponíveis, definido pelo tier da nave escolhida
        # (quanto mais avançada a nave, mais opções de arma); o jogador
        # alterna entre elas com a tecla F.
        self.weapons = build_weapons(self, skin_tier(skin))
        self.current_weapon_index = 0
        self.weapon = self.weapons[self.current_weapon_index]

        # Começa com a imagem padrão
        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))

        self.speed = 5

        # Vida e vidas do jogador
        self.max_health = 100
        self.health = self.max_health
        self.lives = STARTING_LIVES
        self.invulnerable_until = 0  # timestamp (pygame.time.get_ticks()) até quando ignora dano

    def shoot(self, projectiles_group, enemies_group=None):
        """A arma básica (`weapons[0]`) dispara sempre. Se o jogador tiver
        selecionado outro tipo de munição com a tecla F (índice diferente
        de 0), ela dispara acumulada ao tiro básico — cada arma respeita
        seu próprio intervalo entre disparos e limite de munição, de
        forma independente. `enemies_group` é repassado para armas com
        mira automática (ex.: HomingShot)."""
        self.weapons[0].shoot(projectiles_group, enemies_group)
        if self.current_weapon_index != 0:
            self.weapon.shoot(projectiles_group, enemies_group)

    def change_weapon(self):
        """Avança para a próxima munição secundária da lista (troca
        cíclica); ao voltar ao índice 0 (a arma básica), nenhuma munição
        extra fica acumulada e o jogador dispara só o tiro básico."""
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
        self.weapon = self.weapons[self.current_weapon_index]

    def update(self, keys):
        """Atualiza a posição da nave conforme as teclas WASD pressionadas,
        troca o sprite conforme a direção horizontal e atualiza a arma atual
        (necessário para armas com recarga ou comportamento contínuo)."""
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.image = self.image_left
        elif keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.image = self.image_right
        else:
            self.image = self.image_idle
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        # Atualiza a arma (ex.: progresso de recarga)
        self.current_weapon.update()

        # Pisca a nave enquanto durar a invencibilidade pós-respawn
        now = pygame.time.get_ticks()
        if now < self.invulnerable_until:
            self.image.set_alpha(120 if (now // 150) % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)

    def take_damage(self, amount):
        """Reduz a vida do jogador (ignorando dano durante a breve
        invencibilidade pós-respawn). Ao chegar a zero, consome uma
        vida: se ainda restarem vidas, a nave reaparece com vida cheia;
        sem vidas restantes, marca a nave como destruída de vez (fim de
        jogo, para esse jogador)."""
        if pygame.time.get_ticks() < self.invulnerable_until:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.lives -= 1
            if self.lives > 0:
                self._respawn()
            else:
                print(" Player morreu!")
                self.alive = False

    def _respawn(self):
        """Restaura a vida cheia, reposiciona a nave no ponto inicial e
        concede uma breve invencibilidade — usado quando o jogador ainda
        tem vidas restantes após a nave ser destruída."""
        print(f" Nave destruída! Vidas restantes: {self.lives}")
        self.health = self.max_health
        self.rect.center = (WIDTH // 2, HEIGHT - 60)
        self.invulnerable_until = pygame.time.get_ticks() + RESPAWN_INVULNERABILITY_MS

    def draw_health_bar(self, surface):
        """Desenha a barra de vida (fundo vermelho + preenchimento na cor
        de destaque escolhida pelo jogador) no canto superior esquerdo
        da tela."""
        bar_width = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect)          # vermelho (fundo)
        pygame.draw.rect(surface, settings.accent_color, fill_rect)   # vida atual

    def draw_lives(self, surface):
        """Mostra a quantidade de vidas restantes, logo abaixo da barra
        de vida principal."""
        font = pygame.font.SysFont(None, 28)
        text = font.render(f"Vidas: {self.lives}", True, (255, 255, 255))
        surface.blit(text, (10, 26))

    def draw_mini_health_bar(self, surface):
        """Desenha uma barra de vida pequena logo acima da nave, no
        mesmo estilo usado por `Enemy.draw_health_bar`. Usada para
        mostrar a vida de outros jogadores no modo cooperativo, sem
        ocupar o HUD principal (reservado ao jogador local)."""
        bar_width = 50
        bar_height = 6
        fill = (self.health / self.max_health) * bar_width if self.max_health else 0
        outline_rect = pygame.Rect(self.rect.centerx - bar_width // 2, self.rect.top - 12, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.centerx - bar_width // 2, self.rect.top - 12, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect)
        pygame.draw.rect(surface, settings.accent_color, fill_rect)

    def draw_name_tag(self, surface, label=None, color=(255, 255, 255)):
        """Desenha uma etiqueta com o nome do jogador logo acima da nave
        (com um fundo escuro semitransparente, para ficar legível sobre
        qualquer cenário). Usada em partidas cooperativas para facilitar
        identificar qual nave é de qual jogador; `label` permite
        sobrescrever o texto exibido (ex.: "Você" para a nave local)."""
        text = label if label is not None else self.name
        if not text:
            return
        font = pygame.font.SysFont(None, 22)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - 14))

        background = pygame.Surface((text_rect.width + 10, text_rect.height + 4), pygame.SRCALPHA)
        background.fill((0, 0, 0, 140))
        surface.blit(background, (text_rect.x - 5, text_rect.y - 2))
        surface.blit(text_surface, text_rect)

    def draw_weapons_hud(self, surface):
        """Desenha um círculo colorido para cada arma do arsenal e exibe a
        munição restante (ou o símbolo de infinito quando a arma não
        consome munição). A arma básica (índice 0) sempre tem uma borda
        branca, por disparar em toda partida; a munição secundária
        selecionada com F (se houver) ganha uma borda na cor de destaque
        do jogador, indicando que dispara acumulada à básica."""
        x_offset = 20
        y_offset = HEIGHT - 60
        radius = 20

        for i, weapon in enumerate(self.weapons):
            color = WEAPON_COLORS.get(weapon.__class__.__name__, (200, 200, 200))
            pos = (x_offset + i * 60, y_offset)

            pygame.draw.circle(surface, color, pos, radius)

            if i == 0:
                # a arma básica dispara sempre, em toda partida
                pygame.draw.circle(surface, (255, 255, 255), pos, radius, 3)

            # borda na cor de destaque: munição secundária acumulada
            if i == self.current_weapon_index and i != 0:
                pygame.draw.circle(surface, settings.accent_color, pos, radius, 3)

            # munição
            font = pygame.font.SysFont(None, 24)
            ammo_text = "∞" if weapon.ammo is None else str(weapon.ammo)
            text_surface = font.render(ammo_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=pos)
            surface.blit(text_surface, text_rect)

    @property
    def current_weapon(self):
        """Retorna a instância da arma atualmente selecionada."""
        return self.weapons[self.current_weapon_index]
