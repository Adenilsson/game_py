"""
Armas equipáveis pelo jogador: BasicWeapon (tiro único infinito),
DoubleShot e TripolShot (rajadas com munição limitada e recarga),
HeavyLaser (tiro forte e lento com munição limitada), QuadShot (rajada
de quatro projéteis) e HomingShot (tiro teleguiado que mira o inimigo
mais próximo). Cada uma aceita parâmetros opcionais de ajuste (dano,
cadência, munição) para que o arsenal por nave (`core/weapon_loadouts.py`)
possa configurar a mesma arma de forma diferente conforme o tier."""

import math
import pygame
from core.weapons.base_weapon import BaseWeapon
from core.weapons.projectile import Projectile

class BasicWeapon(BaseWeapon):
    """Arma inicial do jogador: tiro único, munição infinita. A cadência
    (`fire_rate`) é configurável para permitir naves com tiro mais ou
    menos rápido."""

    def __init__(self, owner, damage=30, fire_rate=100):
        """Configura dano e cadência da arma básica; munição sempre
        infinita (`ammo=None`) e um único projétil por disparo."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=None, burst=1)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Sem lógica contínua (munição infinita, não precisa recarregar)."""
        pass

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara um único projétil verde para cima."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -10),
            damage=self.damage,
            color=(0, 255, 0),   # verde
            size=(5, 15),
            owner="player",
        )
        projectiles_group.add(projectile)


class DoubleShot(BaseWeapon):
    """Dispara exatamente dois projéteis lado a lado, com munição
    limitada e recarga automática ao zerar."""

    def __init__(self, owner, damage=25, fire_rate=400, ammo_max=20):
        """Configura munição, cadência e tempo de recarga da rajada
        dupla; começa com a munição cheia e fora do estado de recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=2)
        self.ammo_max = ammo_max       # quantidade máxima de munição
        self.ammo = self.ammo_max      # começa cheia
        self.reload_time = 2000        # tempo de recarga em ms
        self.reloading = False
        self.reload_start = 0

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara dois projéteis azuis lado a lado e inicia a recarga
        automática assim que a munição zera."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        if self.ammo == 0:
            self.start_reload()

        offsets = [-15, 15]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18),
                owner="player",
            )
            projectiles_group.add(projectile)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False
                print("Recarga concluída! Munição:", self.ammo)


class TripolShot(BaseWeapon):
    """Rajada tripla (três projéteis deslocados) com munição limitada e
    recarga automática."""

    def __init__(self, owner, damage=25, fire_rate=400, ammo_max=20):
        """Configura munição, cadência e tempo de recarga da rajada
        tripla; começa com a munição cheia e fora do estado de recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=3)
        self.ammo_max = ammo_max
        self.ammo = self.ammo_max
        self.reload_time = 2000
        self.reloading = False
        self.reload_start = 0

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara três projéteis azuis (esquerda, centro, direita) e
        inicia a recarga automática assim que a munição zera."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        if self.ammo == 0:
            self.start_reload()

        offsets = [-20, 0, 20]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -12),
                damage=self.damage,
                color=(0, 0, 255),   # azul
                size=(6, 18),
                owner="player"
            )
            projectiles_group.add(projectile)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False


class HeavyLaser(BaseWeapon):
    """Arma pesada: dano alto, cadência lenta e munição limitada,
    disparando um único projétil grande."""

    def __init__(self, owner, damage=50, fire_rate=500, ammo_max=10):
        """Configura munição, cadência e tempo de recarga (o mais longo
        do arsenal, pelo dano elevado); começa com a munição cheia e
        fora do estado de recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=1)
        self.ammo_max = ammo_max
        self.ammo = self.ammo_max
        self.reload_time = 2500
        self.reloading = False
        self.reload_start = 0

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara um único projétil vermelho de grande porte."""
        if not self.can_shoot():
            return
        if self.ammo == 0:
            self.start_reload()

        self.last_shot = pygame.time.get_ticks()

        projectile = Projectile(
            x=self.owner.rect.centerx,
            y=self.owner.rect.top,
            velocity=(0, -20),
            damage=self.damage,
            color=(255, 0, 0),   # vermelho
            size=(10, 40),       # bem maior
            owner="player",
        )
        projectiles_group.add(projectile)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False


class QuadShot(BaseWeapon):
    """Arma avançada: dispara em leque com quatro projéteis simultâneos.
    Reservada às naves de tier mais alto (mais opções de arma)."""

    def __init__(self, owner, damage=20, fire_rate=450, ammo_max=16):
        """Configura munição, cadência e tempo de recarga do disparo em
        leque de quatro projéteis; começa com a munição cheia e fora do
        estado de recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=4)
        self.ammo_max = ammo_max
        self.ammo = self.ammo_max
        self.reload_time = 2200
        self.reloading = False
        self.reload_start = 0

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara quatro projéteis verde-água em leque e inicia a
        recarga automática assim que a munição zera."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        if self.ammo == 0:
            self.start_reload()

        offsets = [-30, -10, 10, 30]
        for offset in offsets:
            projectile = Projectile(
                x=self.owner.rect.centerx + offset,
                y=self.owner.rect.top,
                velocity=(0, -11),
                damage=self.damage,
                color=(0, 220, 150),   # verde-água
                size=(6, 16),
                owner="player",
            )
            projectiles_group.add(projectile)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False


class HomingShot(BaseWeapon):
    """Arma exclusiva das naves de tier mais alto: dispara três
    projéteis teleguiados simultâneos, em leque, mirados no inimigo
    mais próximo no momento do disparo. Sem inimigos por perto, dispara
    reto para cima."""

    def __init__(self, owner, damage=35, fire_rate=350, ammo_max=8):
        """Configura munição, cadência (mais rápida que o disparo único
        original, já que agora sai em leque de três), tempo de recarga
        e a velocidade dos projéteis teleguiados; começa com a munição
        cheia e fora do estado de recarga."""
        super().__init__(owner, damage=damage, fire_rate=fire_rate, ammo=ammo_max, burst=3)
        self.ammo_max = ammo_max
        self.ammo = self.ammo_max
        self.reload_time = 3000
        self.reloading = False
        self.reload_start = 0
        self.speed = 12
        self.spread_angles = (-14, 0, 14)  # graus de abertura do leque

    def start_reload(self):
        """Inicia o processo de recarga, zerando o cronômetro de recarga."""
        self.reloading = True
        self.reload_start = pygame.time.get_ticks()

    def _velocity_towards_nearest(self, enemies_group):
        """Calcula a velocidade na direção do inimigo mais próximo do
        dono da arma. Retorna None se não houver nenhum inimigo vivo."""
        if not enemies_group:
            return None
        nearest = min(
            enemies_group,
            key=lambda e: (e.rect.centerx - self.owner.rect.centerx) ** 2
            + (e.rect.centery - self.owner.rect.centery) ** 2,
            default=None,
        )
        if nearest is None:
            return None
        dx = nearest.rect.centerx - self.owner.rect.centerx
        dy = nearest.rect.centery - self.owner.rect.centery
        length = math.hypot(dx, dy) or 1
        return (dx / length * self.speed, dy / length * self.speed)

    @staticmethod
    def _rotate_velocity(velocity, degrees):
        """Rotaciona um vetor de velocidade pelo ângulo indicado (em
        graus), usado para abrir o leque de projéteis teleguiados em
        torno da direção mirada no alvo."""
        rad = math.radians(degrees)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        vx, vy = velocity
        return (vx * cos_a - vy * sin_a, vx * sin_a + vy * cos_a)

    def shoot(self, projectiles_group, enemies_group=None):
        """Dispara três projéteis magenta em leque, todos mirados no
        inimigo mais próximo (ou retos para cima, se não houver alvo) —
        a direção central mira o alvo, e as outras duas são a mesma
        direção rotacionada para cada lado — e inicia a recarga
        automática assim que a munição zera."""
        if not self.can_shoot():
            return
        self.last_shot = pygame.time.get_ticks()

        if self.ammo == 0:
            self.start_reload()

        aim_velocity = self._velocity_towards_nearest(enemies_group) or (0, -self.speed)

        for angle in self.spread_angles:
            velocity = self._rotate_velocity(aim_velocity, angle)
            projectile = Projectile(
                x=self.owner.rect.centerx,
                y=self.owner.rect.top,
                velocity=velocity,
                damage=self.damage,
                color=(255, 60, 200),   # magenta
                size=(9, 9),
                owner="player",
            )
            projectiles_group.add(projectile)

    def update(self, player=None, projectiles_group=None, enemies_group=None):
        """Enquanto a arma está recarregando, verifica se o tempo de
        recarga já passou e, nesse caso, restaura a munição cheia."""
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start >= self.reload_time:
                self.ammo = self.ammo_max
                self.reloading = False
