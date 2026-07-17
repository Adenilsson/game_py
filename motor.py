"""
Ponto de entrada do jogo.

Executa este arquivo para iniciar a aplicação: `python motor.py`.
Toda a lógica de inicialização e o loop principal ficam em core/game.py.
"""

from core.app_paths import chdir_to_app_dir

# Garante que caminhos relativos de assets (ex.: "assets/imagens/...")
# funcionem mesmo quando rodando como executável empacotado, não importa
# como ele foi iniciado (duplo-clique, atalho, etc.).
chdir_to_app_dir()

from core.game import Game

if __name__ == "__main__":
    jogo = Game()
    jogo.run()
