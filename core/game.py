"""
Classe principal do jogo: telas (menu, instruções, game over), loop
principal de jogo, sistema de níveis/ondas (waves) de inimigos,
resolução de colisões entre jogadores/inimigos/projéteis, e o modo
cooperativo em LAN (um host autoritativo simula tudo; clientes só
mandam input e desenham o que o host manda de volta).
"""

import pygame
import random
from config import WIDTH, HEIGHT, FPS, BLACK
from core.player import Player
from background import Background
from core.mode_select_screen import ModeSelectScreen
from core.join_screen import JoinScreen
from core.startScreen import StartScreen
from core.instructions_screen import InstructionsScreen
from core.game_over_screen import GameOverScreen
from core.enemy import BasicEnemy, ShooterEnemy, FastEnemy, TankEnemy, SpreaderEnemy
from core.effects import Explosion
from core.powerup import LifeBox
from core.ammo_box import AmmoBox, AMMO_BOX_WEAPON_MAP, available_ammo_colors
from core.highscore import load_high_score, submit_score, record_player_score
from core.settings import settings
from core.network.host import GameServer
from core.network.client import GameClient
from core.network.ghosts import EnemyGhost, ProjectileGhost, PowerUpGhost, AmmoBoxGhost

HOST_PLAYER_ID = "host"

# Intervalo (em ms) entre o aparecimento de caixas de vida extra: um
# valor aleatório é sorteado nesse intervalo a cada spawn, para que não
# apareçam num ritmo previsível nem com frequência demais.
POWERUP_MIN_INTERVAL_MS = 35000
POWERUP_MAX_INTERVAL_MS = 50000

# Mesma ideia para as caixas de munição, num ritmo um pouco mais frequente
# (munição acaba com mais regularidade do que vidas).
AMMO_BOX_MIN_INTERVAL_MS = 20000
AMMO_BOX_MAX_INTERVAL_MS = 30000


def _is_alive(player):
    """`Player.alive` só vira um booleano de verdade depois do primeiro
    dano fatal (ver `Player.take_damage`); antes disso, o atributo
    herdado de `pygame.sprite.Sprite` é o método `alive()` (sempre
    "verdadeiro" em teste booleano). Esta função normaliza os dois
    casos para um booleano real."""
    alive_attr = getattr(player, "alive", True)
    if callable(alive_attr):
        return True
    return bool(alive_attr)


class Game:
    """Orquestra o ciclo de vida completo de uma partida: modo de jogo
    (solo ou cooperativo em LAN), telas iniciais, progressão de níveis e
    ondas de inimigos, loop principal (input, atualização e
    renderização) e tela de fim de jogo."""

    def __init__(self):
        """Inicializa o pygame, a janela, os grupos de sprites e as
        estruturas de dados que controlam níveis, ondas de inimigos e o
        modo de jogo (solo/host/cliente)."""
        pygame.init()

        # Configuração dos níveis: cada entrada define o score necessário
        # para avançar e os novos parâmetros de dificuldade dos inimigos
        self.levels = [
            {"score": 50, "spawn_interval": 5000, "enemy_speed": 2, "enemy_damage": 5, "enemy_types": ["basic"]},
            {"score": 70, "spawn_interval": 3000, "enemy_speed": 3, "enemy_damage": 7, "enemy_types": ["basic", "shooter"]},
            {"score": 100, "spawn_interval": 2000, "enemy_speed": 4, "enemy_damage": 10, "enemy_types": ["basic", "shooter", "fast"]},
            {"score": 150, "spawn_interval": 1500, "enemy_speed": 5, "enemy_damage": 12, "enemy_types": ["basic", "shooter", "fast", "tank"]},
        ]
        # Configuração das ondas: quantidade de cada tipo de inimigo por onda.
        # Cada tipo usa uma arma diferente (basic=Weapon1, shooter=Weapon2
        # laser, fast=Weapon5 teleguiado, tank=Weapon3 escudo orbital,
        # spreader=Weapon4 leque) — misturar tipos numa onda já garante
        # variedade de armas em tela, por isso toda onda combina pelo menos
        # dois tipos desde o início.
        self.waves = {
            1: {"basic": 10, "shooter": 5},
            2: {"basic": 10, "shooter": 6, "fast": 5},
            3: {"basic": 8, "shooter": 7, "fast": 6, "tank": 3},
            4: {"basic": 7, "shooter": 7, "fast": 7, "tank": 3, "spreader": 6},
            5: {"basic": 8, "shooter": 6, "fast": 6, "tank": 4, "spreader": 8},
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
        self.explosion_sound = settings.load_sound("assets/sons/explosion.mp3")

        self.last_spawn = pygame.time.get_ticks()
        self.spawn_interval = 6000  # spawn a cada 2 segundos

        # Caixa de vida extra: cai periodicamente, em intervalo aleatório
        self.last_powerup_spawn = pygame.time.get_ticks()
        self.powerup_spawn_interval = random.randint(POWERUP_MIN_INTERVAL_MS, POWERUP_MAX_INTERVAL_MS)

        # Caixa de munição: idem, mas recarrega uma arma específica
        self.last_ammo_box_spawn = pygame.time.get_ticks()
        self.ammo_box_spawn_interval = random.randint(AMMO_BOX_MIN_INTERVAL_MS, AMMO_BOX_MAX_INTERVAL_MS)

        self.mode_select_screen = ModeSelectScreen(self.screen)
        self.join_screen = JoinScreen(self.screen)
        self.start_screen = StartScreen(self.screen)
        self.instructions_screen = InstructionsScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.effects_group = pygame.sprite.Group()
        self.powerups_group = pygame.sprite.Group()
        self.ammo_boxes_group = pygame.sprite.Group()

        # --- Estado do modo cooperativo em LAN ---
        self.network_role = None       # None (solo), "host" ou "client"
        self.server = None             # GameServer, só quando network_role == "host"
        self.client = None             # GameClient, só quando network_role == "client"
        self.local_player_id = HOST_PLAYER_ID
        self._local_skin = "player_1"
        self._local_name = ""
        self._explosions_this_frame = []       # posições de explosões novas, pro host transmitir
        self.remote_enemy_ghosts = {}          # cliente: id -> EnemyGhost
        self.remote_powerup_ghosts = {}         # cliente: id -> PowerUpGhost
        self.remote_ammo_box_ghosts = {}        # cliente: id -> AmmoBoxGhost

        # Os jogadores só existem depois da escolha da nave na tela inicial
        # (ver run()). No modo solo/host, self.players[id] são Players de
        # verdade, simulados normalmente; no modo cliente, são "bonecos"
        # (Player) só posicionados a partir do snapshot recebido do host.
        self.players = {}

    def _generate_wave_config(self, wave_number):
        """Gera a configuração de uma onda além das cadastradas
        manualmente em `self.waves` (que só vai até a última onda
        definida): usa todos os tipos de inimigo, em quantidade cada vez
        maior conforme o número da onda, para que o jogo nunca pare de
        spawnar inimigos (isso ficava evidente principalmente em
        partidas cooperativas, onde as ondas são derrotadas mais rápido
        e essa situação era alcançada com mais frequência)."""
        extra = wave_number - max(self.waves.keys())
        return {
            "basic": 8 + extra,
            "shooter": 6 + extra // 2,
            "fast": 6 + extra // 2,
            "tank": 3 + extra // 3,
            "spreader": 6 + extra // 2,
        }

    def start_wave(self, wave_number):
        """Ativa a onda de inimigos indicada, carregando sua configuração
        de quantidade por tipo. Ondas além das cadastradas manualmente em
        `self.waves` são geradas automaticamente, cada vez mais difíceis
        (ver `_generate_wave_config`)."""
        if wave_number in self.waves:
            self.wave_config = self.waves[wave_number].copy()
        else:
            self.wave_config = self._generate_wave_config(wave_number)
        self.wave_active = True
        self.enemies_spawned = 0

    def _spawn_batch_size(self):
        """Quantos inimigos aparecem de uma só vez a cada spawn. Cresce
        conforme o nível de dificuldade atual, para que existam mais
        inimigos simultâneos em tela conforme a partida avança."""
        return 2 + self.current_level_index

    def spawn_wave_enemy(self):
        """Cria vários inimigos da onda atual de uma só vez (ver
        `_spawn_batch_size`), escolhendo os próximos tipos com contagem
        disponível na configuração da onda."""
        for _ in range(self._spawn_batch_size()):
            if not self._spawn_single_wave_enemy():
                break  # onda esgotada: nada mais a spawnar neste lote

    def _spawn_single_wave_enemy(self):
        """Cria um único inimigo da onda atual, escolhendo o próximo tipo
        com contagem disponível na configuração da onda. Retorna False
        se não houver mais inimigos a spawnar na onda atual."""
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
                return True
        return False

    def spawn_life_box(self):
        """Cria uma caixa de vida extra caindo do topo da tela e agenda
        o próximo spawn em um intervalo aleatório (efeito "de tempos em
        tempos", em vez de um ritmo previsível)."""
        box = LifeBox()
        self.powerups_group.add(box)
        self.all_sprites.add(box)
        self.last_powerup_spawn = pygame.time.get_ticks()
        self.powerup_spawn_interval = random.randint(POWERUP_MIN_INTERVAL_MS, POWERUP_MAX_INTERVAL_MS)

    def spawn_ammo_box(self):
        """Cria uma caixa de munição caindo do topo da tela e agenda o
        próximo spawn em um intervalo aleatório. A cor é sorteada entre
        as armas que algum jogador da partida realmente possui (não
        adianta soltar munição de uma arma que ninguém tem ainda)."""
        self.last_ammo_box_spawn = pygame.time.get_ticks()
        self.ammo_box_spawn_interval = random.randint(AMMO_BOX_MIN_INTERVAL_MS, AMMO_BOX_MAX_INTERVAL_MS)

        owned_weapon_names = {
            type(weapon).__name__
            for player in self.players.values()
            for weapon in player.weapons
        }
        relevant_colors = [
            color for color in available_ammo_colors()
            if AMMO_BOX_WEAPON_MAP[color] in owned_weapon_names
        ]
        if not relevant_colors:
            return  # nenhum jogador tem ainda uma arma com munição cadastrada

        box = AmmoBox(random.choice(relevant_colors))
        self.ammo_boxes_group.add(box)
        self.all_sprites.add(box)

    def spawn_explosion(self, position):
        """Cria o efeito visual de explosão na posição indicada e toca o
        som de explosão (usado quando um inimigo é destruído). No modo
        host, também registra a posição para transmitir aos clientes."""
        self.effects_group.add(Explosion(position))
        settings.play_sound(self.explosion_sound)
        if self.network_role == "host":
            self._explosions_this_frame.append(position)

    def _draw_pause_overlay(self):
        """Desenha uma camada escura semitransparente com o texto
        PAUSADO por cima da cena, usada enquanto o jogo está pausado
        (disponível apenas em partidas solo)."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 64)
        text = font.render("PAUSADO", True, (255, 255, 255))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        hint_font = pygame.font.SysFont(None, 28)
        hint = hint_font.render("Pressione ESC para continuar", True, (200, 200, 200))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))

    def _show_hosting_info(self):
        """Mostra o IP local que o outro jogador deve digitar em
        "Entrar em partida", até o host clicar/apertar uma tecla para
        continuar."""
        ip = self.server.local_ip()
        font_title = pygame.font.SysFont(None, 48)
        font_ip = pygame.font.SysFont(None, 64)
        font_hint = pygame.font.SysFont(None, 26)

        title = font_title.render("Hospedando partida", True, (255, 255, 255))
        ip_text = font_ip.render(ip, True, (255, 215, 0))
        hint = font_hint.render("Diga esse IP ao outro jogador. Clique para continuar.", True, (200, 200, 200))

        waiting = True
        while waiting:
            self.screen.fill((15, 15, 25))
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 250))
            self.screen.blit(ip_text, (WIDTH // 2 - ip_text.get_width() // 2, 330))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 420))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    waiting = False

    def run(self):
        """Ponto de entrada da partida: primeiro escolhe o modo (solo,
        hospedar ou entrar em uma partida cooperativa em LAN) e então
        segue o fluxo de sempre (nave, nome, instruções) até o loop
        principal do jogo."""
        mode = self.mode_select_screen.run()

        if mode == "host":
            self.network_role = "host"
            self.local_player_id = HOST_PLAYER_ID
            self.server = GameServer()
            self.server.start()
            self._show_hosting_info()
        elif mode == "join":
            client = self.join_screen.run()
            if client is None:
                self.run()
                return
            self.network_role = "client"
            self.client = client
            self.local_player_id = client.player_id
        else:
            self.network_role = None
            self.local_player_id = HOST_PLAYER_ID

        action = self.start_screen.run()
        if action == "play":
            selected_skin = self.start_screen.selected_skin
            self._local_skin = selected_skin
            self._local_name = self.start_screen.player_name.strip()

            # No modo cliente não existe um Player "de verdade" local: o
            # host que simula todo mundo, inclusive o boneco que
            # representa este jogador (ver _apply_snapshot).
            if self.network_role != "client":
                local_id = self.local_player_id
                if local_id in self.players:
                    self.all_sprites.remove(self.players[local_id])
                self.players[local_id] = Player(selected_skin, name=self._local_name)
                self.all_sprites.add(self.players[local_id])

            instr_action = self.instructions_screen.run()
            if instr_action == "start":
                self.game_loop()  # inicia o jogo
            elif instr_action == "back":  # volta para tela inicial
                self.run()

    def game_loop(self):
        """Direciona para o loop apropriado ao modo de jogo atual."""
        if self.network_role == "client":
            self._client_game_loop()
        else:
            self._host_or_solo_game_loop()

    def _host_or_solo_game_loop(self):
        """Loop principal usado nos modos solo e host: processa entrada
        de todos os jogadores (local via teclado; remotos via input de
        rede recebido do(s) cliente(s)), atualiza inimigos/projéteis,
        verifica progressão de nível e ondas, resolve colisões e
        renderiza a cena a cada quadro. No modo host, transmite um
        snapshot do mundo para os clientes ao final de cada quadro.
        Termina quando todos os jogadores morrem, quando então exibe a
        tela de game over. No modo solo, pode ser pausado com ESC."""
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
                    if event.key == pygame.K_ESCAPE and self.network_role is None:
                        # Pausar só faz sentido numa partida solo: pausar
                        # a tela do host não pausaria a do cliente.
                        self.paused = not self.paused
                    elif event.key == pygame.K_f and not self.paused:
                        local_player = self.players.get(self.local_player_id)
                        if local_player is not None:
                            local_player.change_weapon()

            if not self.paused:
                # --- Jogadores remotos que acabaram de escolher a nave ---
                if self.network_role == "host":
                    for client_id, input_data in self.server.get_inputs().items():
                        if client_id not in self.players and input_data.get("skin"):
                            new_player = Player(input_data["skin"], name=input_data.get("name", ""))
                            self.players[client_id] = new_player
                            self.all_sprites.add(new_player)

                for player in self.players.values():
                    player.current_weapon.update(player, self.projectiles_group)

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

                # --- Update do jogador local (teclado) ---
                local_player = self.players.get(self.local_player_id)
                if local_player is not None and _is_alive(local_player):
                    local_player.update(keys)
                    if keys[pygame.K_SPACE]:
                        local_player.shoot(self.projectiles_group, self.enemies)

                # --- Update dos jogadores remotos (input de rede) ---
                if self.network_role == "host":
                    for client_id, input_data in self.server.get_inputs().items():
                        remote_player = self.players.get(client_id)
                        if remote_player is None or not _is_alive(remote_player):
                            continue
                        fake_keys = {
                            pygame.K_a: input_data.get("left", False),
                            pygame.K_d: input_data.get("right", False),
                            pygame.K_w: input_data.get("up", False),
                            pygame.K_s: input_data.get("down", False),
                        }
                        remote_player.update(fake_keys)
                        if input_data.get("shoot"):
                            remote_player.shoot(self.projectiles_group, self.enemies)
                        if input_data.get("change_weapon"):
                            remote_player.change_weapon()

                alive_players = [p for p in self.players.values() if _is_alive(p)]

                now = pygame.time.get_ticks()
                self.enemies.update(alive_players, self.projectiles_group, self, speed=self.enemy_speed, damage=self.enemy_damage)

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

                # --- Caixa de vida extra ---
                if now - self.last_powerup_spawn > self.powerup_spawn_interval:
                    self.spawn_life_box()

                # --- Caixa de munição ---
                if now - self.last_ammo_box_spawn > self.ammo_box_spawn_interval:
                    self.spawn_ammo_box()

                self.background.update()
                self.effects_group.update()
                self.projectiles_group.update()
                self.powerups_group.update()
                self.ammo_boxes_group.update()

                # --- Collision ---
                for player in alive_players:
                    if pygame.sprite.spritecollideany(player, self.enemies):
                        player.take_damage(10)

                    hits = pygame.sprite.spritecollide(player, self.projectiles_group, True)
                    for proj in hits:
                        if proj.owner == "enemy":
                            player.take_damage(proj.damage)

                    collected_boxes = pygame.sprite.spritecollide(player, self.powerups_group, True)
                    for _ in collected_boxes:
                        player.lives += 1
                        print(f" {player.name or player.skin} pegou uma vida extra! Vidas: {player.lives}")

                    collected_ammo_boxes = pygame.sprite.spritecollide(player, self.ammo_boxes_group, True)
                    for ammo_box in collected_ammo_boxes:
                        for weapon in player.weapons:
                            if type(weapon).__name__ == ammo_box.weapon_name:
                                weapon.ammo = weapon.ammo_max
                                weapon.reloading = False
                                print(f" {player.name or player.skin} recarregou {ammo_box.weapon_name}!")
                                break

                if self.players and all(not _is_alive(p) for p in self.players.values()):
                    running = False

            # --- Render (sempre, mesmo pausado, para manter a última cena visível) ---
            self._render_frame()

            if self.network_role == "host":
                self.server.broadcast_snapshot(self._build_snapshot())

            pygame.display.flip()

        self._end_game()

    def _client_game_loop(self):
        """Loop usado pelo cliente no modo cooperativo: não simula nada
        (sem inimigos, sem colisão, sem ondas) — a cada quadro manda o
        input local para o host e desenha o snapshot mais recente
        recebido. Termina quando o host sinaliza fim de jogo ou a
        conexão cai."""
        running = True
        change_weapon_pending = False

        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        change_weapon_pending = True

            input_data = {
                "skin": self._local_skin,
                "name": self._local_name,
                "left": bool(keys[pygame.K_a]),
                "right": bool(keys[pygame.K_d]),
                "up": bool(keys[pygame.K_w]),
                "down": bool(keys[pygame.K_s]),
                "shoot": bool(keys[pygame.K_SPACE]),
                "change_weapon": change_weapon_pending,
            }
            self.client.send_input(input_data)
            change_weapon_pending = False  # só um pulso por tecla pressionada

            if not self.client.is_connected():
                running = False
                break

            snapshot = self.client.get_latest_snapshot()
            if snapshot is not None:
                self._apply_snapshot(snapshot)

            self.background.update()
            self.effects_group.update()

            self._render_frame()
            pygame.display.flip()

            if snapshot is not None and snapshot.get("game_over"):
                running = False

        self._end_game()

    def _build_snapshot(self):
        """Monta o estado do mundo simulado neste quadro (host), para
        transmitir a todos os clientes conectados."""
        players_data = {}
        for player_id, player in self.players.items():
            players_data[player_id] = {
                "skin": player.skin,
                "name": player.name,
                "x": player.rect.centerx,
                "y": player.rect.centery,
                "health": player.health,
                "max_health": player.max_health,
                "lives": player.lives,
                "current_weapon_index": player.current_weapon_index,
                "ammo": [w.ammo for w in player.weapons],
                "alive": _is_alive(player),
            }

        enemies_data = [
            {
                "id": str(id(enemy)),
                "type": type(enemy).__name__,
                "x": enemy.rect.centerx,
                "y": enemy.rect.centery,
                "health": enemy.health,
                "max_health": enemy.max_health,
            }
            for enemy in self.enemies
        ]

        projectiles_data = [
            {
                "x": proj.rect.centerx,
                "y": proj.rect.centery,
                "color": list(proj.image.get_at((0, 0)))[:3],
                "size": list(proj.rect.size),
            }
            for proj in self.projectiles_group
        ]

        powerups_data = [
            {
                "id": str(id(box)),
                "x": box.rect.centerx,
                "y": box.rect.centery,
            }
            for box in self.powerups_group
        ]

        ammo_boxes_data = [
            {
                "id": str(id(box)),
                "color": box.color,
                "x": box.rect.centerx,
                "y": box.rect.centery,
            }
            for box in self.ammo_boxes_group
        ]

        new_explosions = [list(pos) for pos in self._explosions_this_frame]
        self._explosions_this_frame = []

        return {
            "score": self.score,
            "current_wave": self.current_wave,
            "level_up": self.level_up,
            "players": players_data,
            "enemies": enemies_data,
            "projectiles": projectiles_data,
            "powerups": powerups_data,
            "ammo_boxes": ammo_boxes_data,
            "new_explosions": new_explosions,
            "game_over": bool(self.players) and all(not _is_alive(p) for p in self.players.values()),
        }

    def _apply_snapshot(self, snapshot):
        """Aplica o snapshot recebido do host: reposiciona/atualiza os
        "bonecos" que representam os jogadores (inclusive o local) e os
        inimigos/projéteis fantasmas, sem simular nenhuma lógica de jogo
        própria — o cliente só desenha o que o host manda."""
        self.score = snapshot.get("score", self.score)
        self.current_wave = snapshot.get("current_wave", self.current_wave)
        self.level_up = snapshot.get("level_up", False)

        # --- Jogadores (bonecos) ---
        seen_player_ids = set()
        for player_id, data in snapshot.get("players", {}).items():
            seen_player_ids.add(player_id)
            puppet = self.players.get(player_id)
            if puppet is None or puppet.skin != data.get("skin"):
                if puppet is not None:
                    self.all_sprites.remove(puppet)
                puppet = Player(data.get("skin", "player_1"))
                self.players[player_id] = puppet
                self.all_sprites.add(puppet)

            puppet.name = data.get("name", "")
            puppet.rect.center = (data["x"], data["y"])
            puppet.health = data["health"]
            puppet.max_health = data["max_health"]
            puppet.lives = data.get("lives", puppet.lives)
            puppet.current_weapon_index = min(data["current_weapon_index"], len(puppet.weapons) - 1)
            for weapon, ammo in zip(puppet.weapons, data.get("ammo", [])):
                weapon.ammo = ammo
            puppet.alive = data.get("alive", True)

        for stale_id in [pid for pid in self.players if pid not in seen_player_ids]:
            self.all_sprites.remove(self.players[stale_id])
            del self.players[stale_id]

        # --- Inimigos fantasmas ---
        seen_enemy_ids = set()
        for enemy_data in snapshot.get("enemies", []):
            enemy_id = enemy_data["id"]
            seen_enemy_ids.add(enemy_id)
            ghost = self.remote_enemy_ghosts.get(enemy_id)
            if ghost is None:
                ghost = EnemyGhost(enemy_data["type"])
                self.remote_enemy_ghosts[enemy_id] = ghost
                self.all_sprites.add(ghost)
                self.enemies.add(ghost)
            ghost.sync(enemy_data)

        for stale_id in [eid for eid in self.remote_enemy_ghosts if eid not in seen_enemy_ids]:
            self.remote_enemy_ghosts[stale_id].kill()
            del self.remote_enemy_ghosts[stale_id]

        # --- Projéteis fantasmas (recriados a cada snapshot) ---
        self.projectiles_group.empty()
        for proj_data in snapshot.get("projectiles", []):
            self.projectiles_group.add(ProjectileGhost(proj_data))

        # --- Caixas de vida extra fantasmas ---
        seen_powerup_ids = set()
        for powerup_data in snapshot.get("powerups", []):
            powerup_id = powerup_data["id"]
            seen_powerup_ids.add(powerup_id)
            ghost = self.remote_powerup_ghosts.get(powerup_id)
            if ghost is None:
                ghost = PowerUpGhost()
                self.remote_powerup_ghosts[powerup_id] = ghost
                self.all_sprites.add(ghost)
                self.powerups_group.add(ghost)
            ghost.sync(powerup_data)

        for stale_id in [pid for pid in self.remote_powerup_ghosts if pid not in seen_powerup_ids]:
            self.remote_powerup_ghosts[stale_id].kill()
            del self.remote_powerup_ghosts[stale_id]

        # --- Caixas de munição fantasmas ---
        seen_ammo_box_ids = set()
        for ammo_box_data in snapshot.get("ammo_boxes", []):
            ammo_box_id = ammo_box_data["id"]
            seen_ammo_box_ids.add(ammo_box_id)
            ghost = self.remote_ammo_box_ghosts.get(ammo_box_id)
            if ghost is None:
                ghost = AmmoBoxGhost(ammo_box_data["color"])
                self.remote_ammo_box_ghosts[ammo_box_id] = ghost
                self.all_sprites.add(ghost)
                self.ammo_boxes_group.add(ghost)
            ghost.sync(ammo_box_data)

        for stale_id in [pid for pid in self.remote_ammo_box_ghosts if pid not in seen_ammo_box_ids]:
            self.remote_ammo_box_ghosts[stale_id].kill()
            del self.remote_ammo_box_ghosts[stale_id]

        # --- Explosões novas neste quadro ---
        for pos in snapshot.get("new_explosions", []):
            self.effects_group.add(Explosion(tuple(pos)))

    def _render_frame(self):
        """Desenha a cena completa: fundo, jogadores, inimigos,
        projéteis, efeitos e HUD. Reaproveitado tanto no modo solo/host
        (sprites simulados de verdade) quanto no modo cliente (sprites
        "fantasma" posicionados a partir do snapshot)."""
        self.screen.fill(BLACK)
        self.background.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemies.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw_shadow(self.screen)
        self.projectiles_group.draw(self.screen)
        self.effects_group.draw(self.screen)

        local_player = self.players.get(self.local_player_id)
        for player_id, player in self.players.items():
            is_local = player_id == self.local_player_id
            if len(self.players) > 1:
                # As etiquetas só ajudam a diferenciar naves quando há
                # mais de um jogador (partidas cooperativas); em solo,
                # mostrar "Você" seria só poluição visual desnecessária.
                label = "Você" if is_local else (player.name or "Jogador")
                label_color = settings.accent_color if is_local else (255, 255, 255)
                player.draw_name_tag(self.screen, label=label, color=label_color)
            if not is_local:
                player.draw_mini_health_bar(self.screen)

        if local_player is not None:
            local_player.draw_weapons_hud(self.screen)
            local_player.draw_health_bar(self.screen)
            local_player.draw_lives(self.screen)

        if self.level_up:
            font = pygame.font.SysFont(None, 48)
            wave_text = font.render(f"Wave {self.current_wave} completa! LEVEL UP!", True, (255, 215, 0))
            self.screen.blit(wave_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (WIDTH - 150, 10))
        high_score_text = font.render(f"Recorde: {self.high_score}", True, (255, 215, 0))
        self.screen.blit(high_score_text, (WIDTH - 150, 45))

        if self.paused:
            self._draw_pause_overlay()

    def _end_game(self):
        """Encerra recursos de rede (se houver), registra a pontuação
        da partida no placar geral e no recorde pessoal do jogador local
        (usado pelo desbloqueio de naves), exibe a tela de game over e
        reage à escolha do jogador (reiniciar ou voltar ao menu reinicia
        todo o estado do jogo, incluindo o modo de rede)."""
        if self.network_role == "host" and self.server:
            self.server.stop()
        if self.network_role == "client" and self.client:
            self.client.disconnect()

        leaderboard = submit_score(self._local_name, self.score)
        self.high_score = leaderboard[0][1] if leaderboard else self.high_score
        # Recorde pessoal: usado pelo sistema de desbloqueio de naves,
        # que libera cada nave só para quem realmente atingiu a pontuação.
        record_player_score(self._local_name, self.score)

        print(" Game Over! Pontuação final:", self.score)
        action = self.game_over_screen.run(self.score, self.high_score, leaderboard)
        if action in ("restart", "menu"):
            # Ambas as opções encerram a partida atual; sem resetar aqui,
            # score, inimigos, ondas e projéteis da partida anterior
            # continuariam presentes na próxima vez que o jogador clicasse
            # em JOGAR.
            self.__init__()
            self.run()
