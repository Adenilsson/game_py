"""
Resolve o diretório usado para ler/salvar dados do jogador (recorde,
configurações) e garante que caminhos relativos de assets funcionem
independentemente de como o jogo foi iniciado.

Importante para o executável gerado com PyInstaller: em modo --onefile,
o código roda a partir de uma pasta temporária extraída a cada execução
(e apagada ao fechar) — usar `__file__` para localizar onde salvar
`highscore.txt`/`settings.json` acabaria gravando nessa pasta temporária,
perdendo os dados a cada execução. `sys.executable` aponta para o .exe
de verdade, cuja pasta persiste entre execuções.
"""

import os
import sys


def get_app_dir():
    """Retorna a pasta onde dados do jogador devem ser lidos/salvos: a
    pasta do executável quando rodando empacotado (`sys.frozen`), ou a
    raiz do projeto quando rodando via `python motor.py`."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def chdir_to_app_dir():
    """Muda o diretório de trabalho atual para a pasta do executável
    quando rodando empacotado, para que os caminhos relativos de assets
    (ex.: "assets/imagens/...") funcionem não importa como o .exe foi
    iniciado (duplo-clique, atalho, arrastar para a tela, etc.)."""
    if getattr(sys, "frozen", False):
        os.chdir(os.path.dirname(sys.executable))
