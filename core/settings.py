"""
Configurações do jogador (volume dos efeitos sonoros e cor de destaque
da interface), persistidas em `settings.json` na raiz do projeto (ou ao
lado do executável, quando empacotado) e compartilhadas por todo o
jogo através da instância `settings`.
"""

import json
import os
import weakref
import pygame
from core.app_paths import get_app_dir

SETTINGS_FILE = os.path.join(get_app_dir(), "settings.json")

DEFAULT_VOLUME = 0.7
DEFAULT_ACCENT_COLOR = (60, 190, 100)  # verde

# Paleta de cores de destaque que o jogador pode escolher na tela de
# configurações (usada nos botões e realces da interface)
ACCENT_COLOR_OPTIONS = [
    (60, 190, 100),   # verde
    (60, 140, 220),   # azul
    (200, 70, 70),    # vermelho
    (150, 90, 220),   # roxo
    (230, 150, 40),   # laranja
    (60, 190, 190),   # ciano
]


class Settings:
    """Mantém em memória as preferências do jogador (volume e cor de
    destaque) e sincroniza com o arquivo `settings.json` em disco."""

    def __init__(self):
        self.volume = DEFAULT_VOLUME
        self.accent_color = DEFAULT_ACCENT_COLOR
        # Referências fracas para os sons já carregados, usadas para
        # reaplicar o volume em sons que possam estar tocando no exato
        # momento em que o jogador arrasta o slider (ex.: a música de
        # introdução, que dura vários segundos). WeakSet evita manter
        # sons "mortos" na memória para sempre.
        self._loaded_sounds = weakref.WeakSet()
        self.load()

    def load(self):
        """Carrega as configurações salvas em disco, se existirem. Em
        caso de arquivo ausente ou inválido, mantém os valores padrão."""
        if not os.path.isfile(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            self.volume = max(0.0, min(1.0, float(data.get("volume", DEFAULT_VOLUME))))
            color = data.get("accent_color", DEFAULT_ACCENT_COLOR)
            self.accent_color = tuple(int(c) for c in color)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            pass

    def save(self):
        """Salva as configurações atuais em disco."""
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"volume": self.volume, "accent_color": list(self.accent_color)}, f)

    def load_sound(self, path):
        """Carrega um efeito sonoro a partir do disco e o registra para
        receber atualizações de volume em tempo real (ver `set_volume`).
        Deve ser usado no lugar de `pygame.mixer.Sound(path)` diretamente
        em qualquer lugar do projeto."""
        sound = pygame.mixer.Sound(path)
        self._loaded_sounds.add(sound)
        return sound

    def play_sound(self, sound):
        """Toca um efeito sonoro aplicando o volume configurado no
        momento da chamada. Deve ser usado no lugar de `sound.play()`
        diretamente em qualquer lugar do projeto, para que um ajuste de
        volume feito pelo jogador tenha efeito imediato, mesmo em sons
        que já estavam carregados antes do ajuste."""
        sound.set_volume(self.volume)
        sound.play()

    def set_volume(self, volume):
        """Define o volume atual e o aplica imediatamente a todos os
        sons já carregados, incluindo os que possam estar tocando neste
        exato momento (ex.: a música de introdução). Sem isso, um som
        longo já em execução continuaria no volume antigo até terminar,
        mesmo que o jogador tivesse acabado de arrastar o slider."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self._loaded_sounds:
            sound.set_volume(self.volume)


# Instância única compartilhada por todo o jogo
settings = Settings()
