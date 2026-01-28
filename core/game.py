import pygame
from config import WIDTH, HEIGHT, FPS, BLACK
from core.player import Player
from core.enemy import Enemy


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Meu Jogo Estruturado")
        self.clock = pygame.time.Clock()

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group() # <-- aqui criamos o grupo de projéteis
        # Criar jogador
        self.player = Player()
        self.all_sprites.add(self.player)

        # Criar inimigos
        for i in range(4):
            enemy = Enemy(weapon_type=i+1)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Atualizações
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            self.enemies.update(self.player, self.projectiles_group)
            self.projectiles_group.update()
            #self.enemies.update()
            

            # Colisão
            if pygame.sprite.spritecollideany(self.player, self.enemies):
                self.player.take_damage(20) # dano fixo ao colidir com inimigo
            # Colisão com projéteis 
            hits = pygame.sprite.spritecollide(self.player, self.projectiles_group, True) 
            for proj in hits: 
                self.player.take_damage(proj.damage)
            # Renderização
            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen) 
            self.enemies.draw(self.screen) 
            self.projectiles_group.draw(self.screen)
            
            self.all_sprites.draw(self.screen)
            # Barra de vida 
            self.player.draw_health_bar(self.screen)
            pygame.display.flip()

        pygame.quit()
