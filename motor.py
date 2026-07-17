"""
Ponto de entrada do jogo.

Executa este arquivo para iniciar a aplicação: `python motor.py`.
Toda a lógica de inicialização e o loop principal ficam em core/game.py.

O loop é assíncrono (async/await) para permitir gerar uma build web via
pygbag (`python -m pygbag .`), que roda o jogo dentro do navegador
(WebAssembly) e pode ser instalada como PWA no Android.
"""

import asyncio

from core.game import Game


async def main():
    jogo = Game()
    await jogo.run()


if __name__ == "__main__":
    asyncio.run(main())
