"""
Classes de inimigos: nave inimiga genérica (Enemy) e suas variações
(BasicEnemy, ShooterEnemy, FastEnemy, TankEnemy, SpreaderEnemy), cada uma
com vida, dano, arma e perfil de movimento (velocidade + aleatoriedade)
próprios.
"""

import pygame
import random
from config import WIDTH, HEIGHT
from core.weapons.weapon1 import Weapon1
from core.weapons.weapon2 import Weapon2
from core.weapons.weapon3 import Weapon3
from core.weapons.weapon4 import Weapon4
from core.weapons.weapon5 import Weapon5


def _tinted(image, color):
    """Retorna uma cópia da imagem multiplicada pela cor informada, usada
    para diferenciar visualmente cada tipo de inimigo sem precisar de
    sprites extras."""
    tinted_image = image.copy()
    tinted_image.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image


class Enemy(pygame.sprite.Sprite):
    """Nave inimiga base. Controla vida, movimento (com componente
    aleatório configurável por subclasse), arma equipada e pontuação
    concedida ao jogador quando destruída."""

    def __init__(self, x=100, y=100, health=50, weapon_type=1):
        """Carrega o sprite do inimigo, define vida/pontuação, escolhe a
        arma equipada de acordo com `weapon_type` (1 a 5) e sorteia um
        movimento inicial dentro do perfil padrão de movimento."""
        super().__init__()
        # Carrega sprite do avião
        self.image = pygame.image.load("assets/imagens/naves/inimigos/aviao.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.image = pygame.transform.rotate(self.image, 180)  # aponta para baixo

        self.base_damage = 10  # dano base do inimigo
        self.max_health = health

        # atributos de vida
        self.health = health
        self.weapon_type = weapon_type
        self.alive = True
        if health == 30:
            self.score_value = 1
        elif health == 50:
            self.score_value = 2
        elif health == 80:
            self.score_value = 3
        else:
            self.score_value = 1  # valor padrão

        # Posição inicial (topo da tela, posição aleatória no eixo X)
        self.rect = self.image.get_rect(
            center=(random.randint(50, WIDTH - 50), 0)
        )

        # Escolhe a arma de acordo com o tipo (cada uma com seu próprio
        # padrão de disparo: tiro único, laser, órbita, leque ou teleguiado)
        if weapon_type == 1:
            self.weapon = Weapon1(self)
        elif weapon_type == 2:
            self.weapon = Weapon2(self)
        elif weapon_type == 3:
            self.weapon = Weapon3(self)
        elif weapon_type == 4:
            self.weapon = Weapon4(self)
        elif weapon_type == 5:
            self.weapon = Weapon5(self)

        # Perfil de movimento: subclasses sobrescrevem estes valores para
        # dar a cada tipo de inimigo uma "personalidade" de deslocamento.
        # speed_y_range: faixa (min, max) sorteada para a velocidade vertical
        # speed_x_choices: valores possíveis de velocidade horizontal
        # redirect_chance: chance por quadro de trocar de direção horizontal
        #                  (dá um movimento mais errático a certos tipos)
        self.speed_y_range = (2, 5)
        self.speed_x_choices = [-2, -1, 0, 1, 2]
        self.redirect_chance = 0.0
        self._randomize_movement()

    def _randomize_movement(self):
        """Sorteia uma nova velocidade vertical/horizontal dentro do
        perfil de movimento do inimigo. Chamado ao nascer e sempre que o
        inimigo reaparece no topo da tela."""
        self.base_speed_y = random.randint(*self.speed_y_range)
        self.speed_y = self.base_speed_y
        self.speed_x = random.choice(self.speed_x_choices)

    def update(self, player, projectiles_group, game, speed=None, damage=None):
        """Move o inimigo, resolve colisões com projéteis do jogador,
        reposiciona a nave ao sair da tela por baixo e atualiza a arma
        equipada. `speed` soma um bônus de dificuldade (definido pelo
        nível atual) sobre a velocidade base própria do inimigo, para que
        cada tipo continue distinguível mesmo com o avanço de nível;
        `damage` ajusta o dano da arma equipada."""
        if speed is not None:
            self.speed_y = self.base_speed_y + max(0, speed - 2)
        if damage is not None:
            self.base_damage = damage  # você pode usar esse atributo no ataque

        # Movimento vertical + horizontal
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # Chance de trocar de direção horizontal aleatoriamente, dando um
        # comportamento mais errático a certos tipos de inimigo
        if self.redirect_chance and random.random() < self.redirect_chance:
            self.speed_x = random.choice(self.speed_x_choices)

        # colisão com projéteis
        hits = pygame.sprite.spritecollide(self, projectiles_group, False)
        for proj in hits:
            if proj.owner == "player":
                self.take_damage(proj.damage, game)
                proj.kill()

        # se morrer, remove do grupo
        if not self.alive:
            self.kill()

        # Rebater nas laterais
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

        # Reiniciar inimigo quando sair da tela
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(50, WIDTH - 50), 0)
            self._randomize_movement()

        # Atualizar arma (disparo), repassando o dano atual configurado
        if hasattr(self, "weapon"):
            self.weapon.damage = self.base_damage
            self.weapon.update(player, projectiles_group)

    def draw_shadow(self, screen):
        """Desenha uma sombra elíptica semitransparente abaixo do inimigo."""
        shadow = pygame.Surface((40, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 200), shadow.get_rect())
        screen.blit(shadow, (self.rect.centerx - 20, self.rect.bottom + 50))

    def take_damage(self, amount, game=None):
        """Reduz a vida do inimigo; ao chegar a zero, soma a pontuação
        correspondente ao placar do jogo, exibe uma explosão e remove
        o inimigo da tela."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            print(" Inimigo destruído!")
            if game:  # soma pontos e mostra explosão antes de remover
                game.score += self.score_value
                game.spawn_explosion(self.rect.center)
            self.kill()

    def draw_health_bar(self, surface):
        """Desenha a barra de vida do inimigo logo acima do seu sprite."""
        bar_width = 40
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), outline_rect)  # fundo vermelho
        pygame.draw.rect(surface, (0, 255, 0), fill_rect)  # vida verde


class BasicEnemy(Enemy):
    """Inimigo padrão: estatísticas medianas, tiro único simples
    (Weapon1) e deslocamento lateral discreto e previsível."""

    def __init__(self):
        super().__init__(weapon_type=1)
        self.health = 50
        self.max_health = self.health
        self.damage = 5

        self.speed_y_range = (2, 4)
        self.speed_x_choices = [-2, -1, 1, 2]
        self.redirect_chance = 0.0
        self._randomize_movement()


class ShooterEnemy(Enemy):
    """Inimigo atirador: dispara feixes de laser periódicos (Weapon2),
    mais resistente e com pouco deslocamento horizontal (fica quase
    parado para mirar)."""

    def __init__(self):
        super().__init__(weapon_type=2)
        self.health = 70
        self.max_health = self.health
        self.damage = 7
        self.image = _tinted(self.image, (150, 255, 255))  # tom ciano

        self.speed_y_range = (1, 3)
        self.speed_x_choices = [-1, 0, 0, 1]
        self.redirect_chance = 0.01
        self._randomize_movement()


class FastEnemy(Enemy):
    """Inimigo veloz: usa um tiro teleguiado (Weapon5) e se move de
    forma rápida e errática pela tela."""

    def __init__(self):
        super().__init__(weapon_type=5)
        self.health = 40
        self.max_health = self.health
        self.damage = 6
        self.image = _tinted(self.image, (255, 150, 255))  # tom magenta

        self.speed_y_range = (5, 7)
        self.speed_x_choices = [-3, -2, 2, 3]
        self.redirect_chance = 0.03
        self._randomize_movement()


class TankEnemy(Enemy):
    """Inimigo tanque: muita vida, avança bem devagar e se protege com
    um escudo de projéteis orbitais ao redor do próprio corpo (Weapon3)."""

    def __init__(self):
        super().__init__(weapon_type=3)
        self.health = 200
        self.max_health = self.health
        self.damage = 12
        self.image = _tinted(self.image, (255, 220, 130))  # tom dourado

        self.speed_y_range = (1, 2)
        self.speed_x_choices = [-1, 0, 1]
        self.redirect_chance = 0.0
        self._randomize_movement()


class SpreaderEnemy(Enemy):
    """Inimigo que dispara em leque de três projéteis (Weapon4) e se
    move em zigue-zague errático pela tela."""

    def __init__(self):
        super().__init__(weapon_type=4)
        self.health = 55
        self.max_health = self.health
        self.damage = 8
        self.image = _tinted(self.image, (255, 190, 120))  # tom laranja

        self.speed_y_range = (3, 5)
        self.speed_x_choices = [-3, -2, -1, 1, 2, 3]
        self.redirect_chance = 0.04
        self._randomize_movement()
