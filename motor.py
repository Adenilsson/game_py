"""
Ponto de entrada do jogo.

Executa este arquivo para iniciar a aplicação: `python motor.py`.
Toda a lógica de inicialização e o loop principal ficam em core/game.py.
"""

from core.game import Game

if __name__ == "__main__":
    jogo = Game()
    jogo.run()
