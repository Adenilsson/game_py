"""
Arsenal de armas do jogador por "tier" (nível da nave escolhida na tela
inicial — ver `core/skins.py`). Quanto maior o tier da nave, mais tipos
de arma o jogador tem à disposição:

- Tier 0 (nave inicial): apenas 2 armas, ambas de cadência bem alta.
- Tier 1: adiciona uma rajada tripla.
- Tier 2: adiciona um laser pesado.
- Tier 3: adiciona uma rajada de quatro projéteis.
- Tier 4+: adiciona um tiro teleguiado que mira o inimigo mais próximo.
"""

from core.weapons.basic_weapon import (
    BasicWeapon,
    DoubleShot,
    TripolShot,
    HeavyLaser,
    QuadShot,
    HomingShot,
)

MAX_TIER = 4


def build_weapons(owner, tier):
    """Monta a lista de armas do jogador `owner` de acordo com o tier da
    nave escolhida. Tiers acima do máximo configurado (`MAX_TIER`) usam
    o arsenal completo, para não quebrar caso novas naves sejam
    adicionadas antes de seu tier de armas ser definido aqui."""
    tier = max(0, min(tier, MAX_TIER))

    # Tier 0: arsenal enxuto (só 2 armas), mas com cadência bem mais
    # rápida que o padrão dessas mesmas armas nos tiers seguintes.
    weapons = [
        BasicWeapon(owner, fire_rate=75),
        DoubleShot(owner, fire_rate=250),
    ]

    if tier >= 1:
        weapons.append(TripolShot(owner))
    if tier >= 2:
        weapons.append(HeavyLaser(owner))
    if tier >= 3:
        weapons.append(QuadShot(owner))
    if tier >= 4:
        weapons.append(HomingShot(owner))

    return weapons
