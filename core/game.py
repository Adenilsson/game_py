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



class Game:
    def __init__(self):
        pygame.init()
        self.score = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Meu Jogo Estruturado")
        self.clock = pygame.time.Clock()
        self.background = Background("assets/bf3.png", speed=3)
        
        self.last_spawn = pygame.time.get_ticks()
        self.spawn_interval = 2000  # spawn a cada 2 segundos
        
        self.start_screen = StartScreen(self.screen)
        self.instructions_screen = InstructionsScreen(self.screen)
        
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
        enemy = Enemy(x=x, y=y, health=health)
        enemy = Enemy(weapon_type=random.randint(1,5))
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
    def show_start_screen(self):
        # Carregar splash art
        splash = pygame.image.load("assets/splash.jpg").convert_alpha()
        splash = pygame.transform.scale(splash, (WIDTH, HEIGHT))

        # Fonte para o título e botão
        font_title = pygame.font.SysFont(None, 72)
        font_button = pygame.font.SysFont(None, 48)

        title_text = font_title.render("Meu Jogo Topdown", True, (255,255,255))
        play_text = font_button.render("JOGAR", True, (0,0,0))

        # Retângulo do botão
        play_button = play_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        button_bg = pygame.Rect(play_button.x-20, play_button.y-10, play_button.width+40, play_button.height+20)

        waiting = True
        while waiting:
            self.screen.blit(splash, (0,0))
            self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))

            # desenhar botão
            pygame.draw.rect(self.screen, (255,255,255), button_bg)  # fundo branco
            self.screen.blit(play_text, play_button)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_bg.collidepoint(event.pos):
                        waiting = False

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
           
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            # HUD das armas
            
            

            if keys[pygame.K_SPACE]:
                self.player.shoot(self.projectiles_group)

            now = pygame.time.get_ticks()
            if now - self.last_spawn > self.spawn_interval:
                self.spawn_enemy()
                self.last_spawn = now


            # Atualizações
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            self.background.update()
            self.enemies.update(self.player, self.projectiles_group,self)
            self.enemies.draw(self.screen)
            for enemy in list(self.enemies):  # usar list() para evitar problemas ao remover
                if not enemy.alive:
                    self.score += enemy.score_value
                    enemy.kill()

            for enemy in self.enemies:
                enemy.draw_shadow(self.screen)
            self.projectiles_group.update()
            #self.enemies.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.player.change_weapon()


            # Colisão
            if pygame.sprite.spritecollideany(self.player, self.enemies):
                self.player.take_damage(10)  # dano fixo ao colidir com inimigo
            
            

            if not self.player.alive: 
                running = False        
               
            # Colisão com projéteis 
            hits = pygame.sprite.spritecollide(self.player, self.projectiles_group, True) 
            for proj in hits:     
                if proj.owner == "enemy":
                    self.player.take_damage(proj.damage)
                
            # Renderização
            
            self.screen.fill(BLACK)
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen) 
            self.enemies.draw(self.screen) 
            self.projectiles_group.draw(self.screen)
            self.player.draw_weapons_hud(self.screen)
            
            font = pygame.font.SysFont(None, 36) 
            score_text = font.render(f"Score: {self.score}", True, (255,255,255)) 
            self.screen.blit(score_text, (WIDTH - 150, 10))
            
            self.all_sprites.draw(self.screen)
            # Barra de vida 
            self.player.draw_health_bar(self.screen)
            pygame.display.flip()

        pygame.quit()
