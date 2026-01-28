import pygame
import time

class BaseWeapon:
    def __init__(self, owner, damage=10, fire_rate=200, duration=100):
        """
        owner: inimigo que possui a arma
        damage: dano causado
        fire_rate: intervalo entre disparos (ms)
        duration: duração do disparo contínuo (ms), se aplicável
        """
        self.owner = owner
        self.damage = damage
        self.fire_rate = fire_rate
        self.duration = duration
        self.last_shot = 5
        self.active = False

    def update(self, player, projectiles_group):
        """Método que cada arma deve implementar"""
        raise NotImplementedError
