"""
Classe principal do jogo: telas (menu, instruções, game over), loop
principal de jogo, sistema de níveis/ondas (waves) de inimigos e
resolução de colisões entre jogador, inimigos e projéteis.
"""

import pygame
import random
from config import WIDTH, HEIGHT, FPS, BLACK
from core.player import Player
from core.enemy import Enemy
from background import Background
from core.weapons.basic_weapon import BasicWeapon, DoubleShot, HeavyLaser
from core.startScreen import StartScreen
from core.instructions_screen import InstructionsScreen
from core.game_over_screen import GameOverScreen
from core.enemy import BasicEnemy, ShooterEnemy, FastEnemy, TankEnemy, SpreaderEnemy
from core.effects import Explosion
from core.highscore import load_high_score, save_high_score


class Game:
    """Orquestra o ciclo de vida completo de uma partida: telas iniciais,
    progressão de níveis e ondas de inimigos, loop principal (input,
    atualização e renderização) e tela de fim de jogo."""

    def __init__(self):
        """Inicializa o pygame, a janela, os grupos de sprites e as
        estruturas de dados que controlam níveis e ondas de inimigos."""
        pygame.init()

        # Configuração dos níveis: cada entrada define o score necessário
        # para avançar e os novos parâmetros de dificuldade dos inimigos
        self.levels = [
            {"score": 50, "spawn_interval": 5000, "enemy_speed": 2, "enemy_damage": 5, "enemy_types": ["basic"]},
            {"score": 70, "spawn_interval": 3000, "enemy_speed": 3, "enemy_damage": 7, "enemy_types": ["basic", "shooter"]},
            {"score": 100, "spawn_interval": 2000, "enemy_speed": 4, "enemy_damage": 10, "enemy_types": ["basic", "shooter", "fast"]},
            {"score": 150, "spawn_interval": 1500, "enemy_speed": 5, "enemy_damage": 12, "enemy_types": ["basic", "shooter", "fast", "tank"]},
        ]
        # Configuração das ondas: quantidade de cada tipo de inimigo por onda
        self.waves = {
            1: {"basic": 5},
            2: {"basic": 5, "shooter": 2},
            3: {"basic": 3, "shooter": 3, "fast": 2},
            4: {"basic": 2, "shooter": 3, "fast": 3, "tank": 1},
            5: {"basic": 2, "shooter": 2, "fast": 2, "tank": 1, "spreader": 3},
        }
        self.current_wave = 1
        self.enemies_spawned = 0
        self.wave_active = False
        self.wave_config = {}  # configuração da wave atual

        self.current_level_index = 0
        self.level_up = False
        self.level_message_time = 0
        self.level_pause_duration = 3000
        self.enemy_speed = 2
        self.enemy_damage = 5

        self.score = 0
        self.high_score = load_high_score()
        self.paused = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Meu Jogo Estruturado")
        self.clock = pygame.time.Clock()
        self.background = Background("assets/imagens/fundos/bf3.png", speed=3)
        self.explosion_sound = pygame.mixer.Sound("assets/sons/explosion.mp3")

        self.last_spawn = pygame.time.get_ticks()
        self.spawn_interval = 6000  # spawn a cada 2 segundos

        self.start_screen = StartScreen(self.screen)
        self.instructions_screen = InstructionsScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.effects_group = pygame.sprite.Group()

        # O jogador só é criado após a escolha da nave na tela inicial (ver run())
        self.player = None

    def start_wave(self, wave_number):
        """Ativa a onda de inimigos indicada, carregando sua configuração
        de quantidade por tipo. Se não existir mais ondas cadastradas,
        marca a onda como inativa."""
        if wave_number in self.waves:
            self.wave_config = self.waves[wave_number].copy()
            self.wave_active = True
            self.enemies_spawned = 0
        else:
            self.wave_active = False

    def spawn_wave_enemy(self):
        """Cria um único inimigo da onda atual, escolhendo o próximo tipo
        com contagem disponível na configuração da onda."""
        for enemy_type, count in list(self.wave_config.items()):
            if count > 0:
                if enemy_type == "basic":
                    enemy = BasicEnemy()
                elif enemy_type == "shooter":
                    enemy = ShooterEnemy()
                elif enemy_type == "fast":
                    enemy = FastEnemy()
                elif enemy_type == "tank":
                    enemy = TankEnemy()
                elif enemy_type == "spreader":
                    enemy = SpreaderEnemy()

                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

                self.wave_config[enemy_type] -= 1
                self.enemies_spawned += 1
                break  # só um inimigo por vez

    def spawn_explosion(self, position):
        """Cria o efeito visual de explosão na posição indicada e toca o
        som de explosão (usado quando um inimigo é destruído)."""
        self.effects_group.add(Explosion(position))
        self.explosion_sound.play()

    def _draw_pause_overlay(self):
        """Desenha uma camada escura semitransparente com o texto
        PAUSADO por cima da cena, usada enquanto o jogo está pausado."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 64)
        text = font.render("PAUSADO", True, (255, 255, 255))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        hint_font = pygame.font.SysFont(None, 28)
        hint = hint_font.render("Pressione ESC para continuar", True, (200, 200, 200))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))

    def run(self):
        """Exibe a tela inicial (onde o jogador escolhe a nave e informa o
        nome) e, conforme a escolha do jogador, avança para as instruções
        e depois para o loop principal do jogo."""
        action = self.start_screen.run()
        if action == "play":
            if self.player is not None:  # remove a nave de uma tentativa anterior
                self.all_sprites.remove(self.player)
            self.player = Player(self.start_screen.selected_skin)
            self.all_sprites.add(self.player)

            instr_action = self.instructions_screen.run()
            if instr_action == "start":
                self.game_loop()  # inicia o jogo
            elif instr_action == "back":  # volta para tela inicial
                self.run()

    def game_loop(self):
        """Loop principal da partida: processa entrada do jogador, atualiza
        jogador/inimigos/projéteis, verifica progressão de nível e ondas,
        resolve colisões e renderiza a cena a cada quadro até o jogador
        morrer, quando então exibe a tela de game over. Pode ser pausado
        a qualquer momento com ESC."""
        running = True
        self.paused = False

        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            # --- Input ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_f and not self.paused:
                        self.player.change_weapon()

            if not self.paused:
                self.player.current_weapon.update(self.player, self.projectiles_group)

                # --- Progressão de nível por pontuação ---
                if self.current_level_index < len(self.levels):
                    next_level = self.levels[self.current_level_index]
                    if self.score >= next_level["score"]:
                        self.spawn_interval = next_level["spawn_interval"]
                        self.enemy_speed = next_level["enemy_speed"]
                        self.enemy_damage = next_level["enemy_damage"]

                        self.level_up = True
                        self.level_message_time = pygame.time.get_ticks()
                        self.current_level_index += 1

                # --- Update ---
                self.player.update(keys)
                if keys[pygame.K_SPACE]:
                    self.player.shoot(self.projectiles_group)

                now = pygame.time.get_ticks()
                self.enemies.update(self.player, self.projectiles_group, self, speed=self.enemy_speed, damage=self.enemy_damage)

                # --- Sistema de ondas ---
                if not self.wave_active:
                    self.start_wave(self.current_wave)

                if self.wave_active and now - self.last_spawn > self.spawn_interval:
                    self.spawn_wave_enemy()
                    self.last_spawn = now

                # quando todos os inimigos da wave forem criados e derrotados
                if self.wave_active and len(self.enemies) == 0 and all(v == 0 for v in self.wave_config.values()):
                    self.wave_active = False
                    self.current_wave += 1
                    self.level_up = True
                    self.level_message_time = pygame.time.get_ticks()

                # Se o player acabou de subir de nível, aguarda alguns segundos
                if self.level_up and now - self.level_message_time > self.level_pause_duration:
                    self.level_up = False

                self.background.update()
                self.effects_group.update()
                self.projectiles_group.update()

                # --- Collision ---
                if pygame.sprite.spritecollideany(self.player, self.enemies):
                    self.player.take_damage(10)

                hits = pygame.sprite.spritecollide(self.player, self.projectiles_group, True)
                for proj in hits:
                    if proj.owner == "enemy":
                        self.player.take_damage(proj.damage)

                if not self.player.alive:
                    running = False

            # --- Render (sempre, mesmo pausado, para manter a última cena visível) ---
            self.screen.fill(BLACK)
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.enemies.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw_shadow(self.screen)
            self.projectiles_group.draw(self.screen)
            self.effects_group.draw(self.screen)
            self.player.draw_weapons_hud(self.screen)

            if self.level_up:
                font = pygame.font.SysFont(None, 48)
                wave_text = font.render(f"Wave {self.current_wave} completa! LEVEL UP!", True, (255, 215, 0))
                self.screen.blit(wave_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (WIDTH - 150, 10))
            high_score_text = font.render(f"Recorde: {self.high_score}", True, (255, 215, 0))
            self.screen.blit(high_score_text, (WIDTH - 150, 45))

            self.player.draw_health_bar(self.screen)

            if self.paused:
                self._draw_pause_overlay()

            pygame.display.flip()

        # --- Game Over ---
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

        print(" Game Over! Pontuação final:", self.score)
        action = self.game_over_screen.run(self.score, self.high_score)
        if action == "restart":
            self.__init__()
            self.run()
        elif action == "menu":
            self.run()
