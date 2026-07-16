# Meu Jogo Topdown

Jogo de nave estilo *top-down shooter* desenvolvido em Python com [Pygame](https://www.pygame.org/). O jogador controla uma nave, enfrenta ondas de inimigos com dificuldade crescente, alterna entre diferentes armas e tenta alcançar a maior pontuação possível antes de perder toda a vida.

## Como executar

### Pré-requisitos

- Python 3.10+
- [Pygame](https://www.pygame.org/)

Instale a dependência:

```bash
pip install pygame
```

### Rodando o jogo

```bash
python motor.py
```

## Controles

| Tecla       | Ação                          |
|-------------|-------------------------------|
| `W` `A` `S` `D` | Mover a nave                |
| `Espaço`    | Atirar                        |
| `F`         | Trocar de arma                |
| `ESC`       | Pausar/retomar o jogo          |

## Como jogar

1. Na tela inicial, escolha sua nave de combate no carrossel (use as setas `<`/`>` na tela, ou as teclas `←`/`→` do teclado), informe um nome e clique em **JOGAR**.
2. Leia as instruções e clique em **INICIAR**.
3. Destrua os inimigos para ganhar pontos e evite colisões com naves e projéteis inimigos.
4. A cada onda (*wave*) vencida ou marco de pontuação atingido, o jogo sobe de nível: inimigos ficam mais rápidos, mais fortes e aparecem com mais frequência.
5. Ao perder toda a vida, a tela de **Game Over** mostra a pontuação final, o recorde e permite reiniciar a partida ou voltar ao menu.

O recorde (maior pontuação já alcançada) fica salvo em `highscore.txt`, na raiz do projeto, e é exibido durante a partida e na tela de game over.

## Estrutura do projeto

```
game_py/
├── motor.py                        # Ponto de entrada: inicia o jogo
├── config.py                       # Configurações globais (tela, cores, HUD)
├── background.py                   # Rolagem contínua do plano de fundo
│
├── assets/                         # Imagens e sons usados pelo jogo
│   ├── imagens/
│   │   ├── fundos/                 # Planos de fundo (rolagem)
│   │   ├── naves/
│   │   │   ├── inimigos/           # Sprite das naves inimigas
│   │   │   └── player/             # Skins selecionáveis da nave do jogador (player_1, player_2, ...)
│   │   └── telas/                  # Artes de tela (splash do menu inicial)
│   └── sons/                       # Efeitos sonoros
│
└── core/                           # Lógica principal do jogo
    ├── game.py                     # Classe Game: loop principal, níveis e ondas
    ├── player.py                   # Classe Player: nave do jogador
    ├── enemy.py                    # Classe Enemy e variações (Basic/Shooter/Fast/Tank/Spreader)
    ├── effects.py                  # Efeitos visuais (explosão ao destruir inimigo)
    ├── highscore.py                # Persistência do recorde em highscore.txt
    ├── startScreen.py              # Tela inicial (menu)
    ├── instructions_screen.py      # Tela de instruções
    ├── game_over_screen.py         # Tela de fim de jogo
    │
    └── weapons/                    # Sistema de armas
        ├── base_weapon.py          # Classe base de todas as armas
        ├── basic_weapon.py         # Armas do jogador (Basic, DoubleShot, TripolShot, HeavyLaser)
        ├── projectile.py           # Classe do projétil genérico
        ├── weapon1.py ... weapon5.py  # Armas usadas pelos diferentes tipos de inimigo
        └── player_weapon.py        # Implementação alternativa (não utilizada atualmente)
```

## Principais classes

- **`Game`** (`core/game.py`) — orquestra telas, loop principal, sistema de níveis/ondas e colisões.
- **`Player`** (`core/player.py`) — nave do jogador: movimento, troca de armas, vida e HUD.
- **`Enemy`** e subclasses (`core/enemy.py`) — cada tipo tem vida, dano, arma e um perfil de movimento (velocidade + aleatoriedade) próprios:

  | Inimigo | Arma | Velocidade vertical | Movimento horizontal |
  |---|---|---|---|
  | `BasicEnemy` | Weapon1 — tiro único | 2–4 | discreto, direção estável |
  | `ShooterEnemy` | Weapon2 — feixe de laser | 1–3 | quase parado (mira) |
  | `FastEnemy` | Weapon5 — tiro teleguiado | 5–7 | rápido e errático |
  | `TankEnemy` | Weapon3 — escudo orbital | 1–2 | praticamente parado |
  | `SpreaderEnemy` | Weapon4 — disparo em leque | 3–5 | zigue-zague errático |

  Cada inimigo também recebe um leve tingimento de cor para se diferenciar visualmente do sprite padrão.
- **`BaseWeapon`** e subclasses (`core/weapons/`) — cadência de tiro, munição/recarga e padrões de disparo (tiro único, rajada, laser, órbita, mira teleguiada).
- **`Projectile`** (`core/weapons/projectile.py`) — projétil genérico usado por todas as armas.
- **`Background`** (`background.py`) — rolagem infinita do cenário.
- **`StartScreen`**, **`InstructionsScreen`**, **`GameOverScreen`** (`core/`) — telas de menu, instruções e fim de jogo. `StartScreen` descobre automaticamente as skins de nave disponíveis em `assets/imagens/naves/player/` e exibe um carrossel (uma nave grande por vez, navegável pelas setas) para escolher antes de jogar.

## Sistema de progressão

O jogo combina dois sistemas de dificuldade, controlados em `Game`:

- **Níveis** (`self.levels`): a cada marco de pontuação, aumentam a velocidade/dano dos inimigos e reduzem o intervalo de spawn.
- **Ondas** (`self.waves`): definem quantos inimigos de cada tipo aparecem antes de avançar para a próxima onda (atualmente 5 ondas, introduzindo um novo tipo de inimigo a cada uma).

## Build (executável)

O projeto inclui um `motor.spec` para gerar um executável com [PyInstaller](https://pyinstaller.org/):

```bash
pyinstaller motor.spec
```

O executável gerado fica em `dist/`.
