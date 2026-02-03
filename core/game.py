import pygame, random
from config import WIDTH, HEIGHT, FPS, BLACK
from core.player import Player
from core.enemy import Enemy
from background import Background
from core.weapons.basic_weapon import BasicWeapon
from core.weapons.basic_weapon import DoubleShot
from core.weapons.basic_weapon import HeavyLaser
from core.startScreen import StartScreen
from core.instructions_screen import InstructionsScreen
from core.game_over_screen import GameOverScreen
from core.enemy import BasicEnemy, ShooterEnemy, FastEnemy, TankEnemy



class Game:
    def __init__(self):
        pygame.init()
        #Controle de níveis
        self.levels = [
            {"score": 50, "spawn_interval": 5000, "enemy_speed": 2, "enemy_damage": 5, "enemy_types": ["basic"]},
            {"score": 70, "spawn_interval": 3000, "enemy_speed": 3, "enemy_damage": 7, "enemy_types": ["basic", "shooter"]},
            {"score": 100, "spawn_interval": 2000, "enemy_speed": 4, "enemy_damage": 10, "enemy_types": ["basic", "shooter", "fast"]},
            {"score": 150, "spawn_interval": 1500, "enemy_speed": 5, "enemy_damage": 12, "enemy_types": ["basic", "shooter", "fast", "tank"]},
        ]
        self.waves = {
            1: {"basic": 5},
            2: {"basic": 5, "shooter": 2},
            3: {"basic": 3, "shooter": 3, "fast": 2},
            4: {"basic": 2, "shooter": 3, "fast": 3, "tank": 1},
        }
        self.current_wave = 1
        self.enemies_spawned = 0
        self.wave_active = False
        self.wave_config = {}  # configuração da wave atual
        self.wave_active = False
        self.current_wave = 1


        self.current_level_index = 0
        self.level_up = False
        self.level_message_time = 0
        self.level_pause_duration = 3000
        self.enemy_speed = 2
        self.enemy_damage = 5

         
         
         
        self.score = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Meu Jogo Estruturado")
        self.clock = pygame.time.Clock()
        self.background = Background("assets/bf3.png", speed=3)
        
        self.last_spawn = pygame.time.get_ticks()
        
        self.spawn_interval = 6000  # spawn a cada 2 segundos
        
        self.start_screen = StartScreen(self.screen)
        self.instructions_screen = InstructionsScreen(self.screen)
        
        self.game_over_screen = GameOverScreen(self.screen)
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group() # <-- aqui criamos o grupo de projéteis
        # Criar jogador
        self.player = Player()
        self.all_sprites.add(self.player)

        # Criar inimigos
    def start_wave(self, wave_number):
        if wave_number in self.waves:
            self.wave_config = self.waves[wave_number].copy()
            self.wave_active = True
            self.enemies_spawned = 0
        else:
            self.wave_active = False

   
            
    def spawn_wave_enemy(self):
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

                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

                self.wave_config[enemy_type] -= 1
                self.enemies_spawned += 1
                break  # só um inimigo por vez

    
    def run(self):
        action  = self.start_screen.run()
        if action == "play": 
            instr_action = self.instructions_screen.run() 
            if instr_action == "start": 
                self.game_loop() # inicia o jogo 
            elif instr_action == "back": # volta para tela inicial 
                self.run()
        running = True
        
        
    def game_loop(self):
        running = True
        
        
        while running:
            self.player.current_weapon.update(self.player, self.projectiles_group)
            if self.current_level_index < len(self.levels):
                next_level = self.levels[self.current_level_index]
                if self.score >= next_level["score"]:
                    self.spawn_interval = next_level["spawn_interval"]

                    # aplicar atributos extras
                    self.enemy_speed = next_level["enemy_speed"]
                    self.enemy_damage = next_level["enemy_damage"]

                    self.level_up = True
                    self.level_message_time = pygame.time.get_ticks()
                    self.current_level_index += 1


            # --- Input ---
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.player.change_weapon()

            # --- Update ---
            self.player.update(keys)
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.projectiles_group)
            
            now = pygame.time.get_ticks()
            self.enemies.update(self.player, self.projectiles_group, self, speed=self.enemy_speed, damage=self.enemy_damage)

            print("Wave active:", self.wave_active)
            print("self.last_spawn:", self.last_spawn)
            print("self.spawn_interval:", self.spawn_interval)
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
            
                self.level_message_time = pygame.time.get_ticks()

            # Se o player acabou de subir de nível, aguarda alguns segundos
            if self.level_up and now - self.level_message_time > self.level_pause_duration:
                self.level_up = False


            """
            now = pygame.time.get_ticks()
            if now - self.last_spawn > self.spawn_interval:
                self.spawn_enemy()
                self.last_spawn = now
            """

            self.background.update()
            self.enemies.update(self.player, self.projectiles_group, self)
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

            # --- Render ---
            self.screen.fill(BLACK)
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.enemies.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw_shadow(self.screen)
            self.projectiles_group.draw(self.screen)
            self.player.draw_weapons_hud(self.screen)
            #if self.level_up:
            #    font = pygame.font.SysFont(None, 48)
            #    level_text = font.render(f"LEVEL UP! Nível {self.current_level_index}", True, (255, 215, 0))
            #    self.screen.blit(level_text, (WIDTH//2 - 150, HEIGHT//2 - 50))
            if self.level_up:
                font = pygame.font.SysFont(None, 48)
                wave_text = font.render(f"Wave {self.current_wave} completa! LEVEL UP!", True, (255, 215, 0))
                self.screen.blit(wave_text, (WIDTH//2 - 200, HEIGHT//2 - 50))


            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255,255,255))
            self.screen.blit(score_text, (WIDTH - 150, 10))

            self.player.draw_health_bar(self.screen)
            pygame.display.flip()

        # --- Game Over ---
        #pygame.quit()
        print(" Game Over! Pontuação final:", self.score)
        action = self.game_over_screen.run(self.score)
        if action == "restart":
            self.__init__()
            self.run()
        elif action == "menu":
            self.run()

