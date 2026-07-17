"""
Ponto de entrada usado exclusivamente pelo build web (pygbag).

O pygbag tem um bug conhecido ao usar um script de entrada com nome
diferente de `main.py` (AttributeError: 'PosixPath' object has no
attribute 'rsplit' dentro do bootstrap dele). Por isso este arquivo
apenas reexporta o `main()` assíncrono definido em motor.py, que
continua sendo o ponto de entrada oficial para rodar o jogo localmente
(`python motor.py`) e para o executável desktop (motor.spec).
"""

import asyncio

# Garante que o pacote pygame (incluindo submódulos como pygame.sprite)
# termine de ser baixado/instalado pelo runtime WASM antes que os módulos
# do jogo (core/*) sejam importados — evita uma corrida em que um módulo
# acessa pygame.sprite antes do pacote estar completamente pronto.
import pygame
pygame.init()

from motor import main

if __name__ == "__main__":
    asyncio.run(main())
