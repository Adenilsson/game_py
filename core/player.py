"""
Classe do jogador: nave controlada pelo usuário, com movimentação,
troca de armas, vida e elementos de HUD (barra de vida e munição).
"""

import pygame
from config import WIDTH, HEIGHT
from core.weapons.basic_weapon import BasicWeapon, HeavyLaser, DoubleShot, TripolShot
from config import WEAPON_COLORS


class Player(pygame.sprite.Sprite):
    """Nave do jogador. Controla movimento, disparo, troca de armas,
    dano recebido e desenho dos elementos de HUD associados a ela."""

    def __init__(self, skin="player_1"):
        """Carrega os sprites da nave (parado, virando à esquerda/direita)
        a partir da pasta de skin escolhida em `assets/imagens/naves/player/`,
        monta o arsenal de armas disponíveis e define posição inicial e vida.

        skin: nome da subpasta com os sprites da nave (ex.: "player_1",
        "player_2"), escolhida pelo jogador na tela inicial.
        """
        super().__init__()
        # Carrega sprite da nave de acordo com a skin escolhida
        skin_dir = f"assets/imagens/naves/player/{skin}"
        self.image_idle = pygame.image.load(f"{skin_dir}/aviao_0.png").convert_alpha()
        self.image_idle = pygame.transform.scale(self.image_idle, (70, 70))

        self.image_right = pygame.image.load(f"{skin_dir}/aviao_d.png").convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (70, 70))

        self.image_left = pygame.image.load(f"{skin_dir}/aviao_e.png").convert_alpha()
        self.image_left = pygame.transform.scale(self.image_left, (70, 70))

        # Lista de armas disponíveis; o jogador alterna entre elas com a tecla F
        self.weapons = [
            BasicWeapon(self),
            DoubleShot(self),
            TripolShot(self),
            HeavyLaser(self)
        ]
        self.current_weapon_index = 0
        self.weapon = self.weapons[self.current_weapon_index]

        # Começa com a imagem padrão
        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))

        self.speed = 5

        # Vida do jogador
        self.max_health = 100
        self.health = self.max_health

    def shoot(self, projectiles_group):
        """Aciona o disparo da arma atualmente equipada."""
        self.weapon.shoot(projectiles_group)

    def change_weapon(self):
        """Avança para a próxima arma da lista, voltando à primeira
        ao chegar no fim (troca cíclica)."""
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

    def take_damage(self, amount):
        """Reduz a vida do jogador e marca a nave como morta ao chegar a zero."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print(" Player morreu!")
            self.alive = False

    def draw_health_bar(self, surface):
        """Desenha a barra de vida (fundo vermelho + preenchimento verde
        proporcional à vida atual) no canto superior esquerdo da tela."""
        bar_width = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect)   # vermelho (fundo)
        pygame.draw.rect(surface, (0, 255, 0), fill_rect)      # verde (vida atual)

    def draw_weapons_hud(self, surface):
        """Desenha um círculo colorido para cada arma do arsenal, destacando
        a arma ativa com uma borda branca e exibindo a munição restante
        (ou o símbolo de infinito quando a arma não consome munição)."""
        x_offset = 20
        y_offset = HEIGHT - 60
        radius = 20

        for i, weapon in enumerate(self.weapons):
            color = WEAPON_COLORS.get(weapon.__class__.__name__, (200, 200, 200))
            pos = (x_offset + i * 60, y_offset)

            pygame.draw.circle(surface, color, pos, radius)

            # borda branca na arma ativa
            if i == self.current_weapon_index:
                pygame.draw.circle(surface, (255, 255, 255), pos, radius, 3)

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
