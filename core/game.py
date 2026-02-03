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



class Game:
    def __init__(self):
        pygame.init()
        #Controle de níveis
        self.level = 1
        self.level_up = False
        self.level_message_time = 0
        self.level_pause_duration = 3000  # 3 segundos sem spawn

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
       
            
    def spawn_enemy(self):
        x = random.randint(40, WIDTH-40)
        y = -40  # começa fora da tela
        health = random.choice([30, 50, 80])  # inimigos com vida diferente
        weapon_type = random.randint(1, 5)
    
        enemy = Enemy(x=x, y=y, health=health, weapon_type=weapon_type)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

        
    
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
            if self.score >= 50 and self.level == 1:
                self.level = 2
                self.spawn_interval = 4000
                self.level_up = True
                self.level_message_time = pygame.time.get_ticks()

            elif self.score >= 80 and self.level == 2:
                self.level = 3
                self.spawn_interval = 3000
                self.level_up = True
                self.level_message_time = pygame.time.get_ticks()

            elif self.score >= 100 and self.level == 3:
                self.level = 4
                self.spawn_interval = 2000
                self.level_up = True
                self.level_message_time = pygame.time.get_ticks()
            elif self.score >= 120 and self.level == 3:
                self.level = 5
                self.spawn_interval = 1000
                self.level_up = True
                self.level_message_time = pygame.time.get_ticks()
            elif self.score >= 150 and self.level == 3:
                self.level = 5
                self.spawn_interval = 800
                self.level_up = True
                self.level_message_time = pygame.time.get_ticks()

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
            if not self.level_up and now - self.last_spawn > self.spawn_interval:
                self.spawn_enemy()
                self.last_spawn = now

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
            if self.level_up:
                font = pygame.font.SysFont(None, 48)
                level_text = font.render(f"LEVEL UP! Nível {self.level}", True, (255, 215, 0))
                self.screen.blit(level_text, (WIDTH//2 - 100, HEIGHT//2 - 50))

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

