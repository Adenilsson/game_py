"""
Arsenal de armas do jogador por "tier" (nível da nave escolhida na tela
inicial — ver `core/skins.py`). Toda nave tem exatamente 3 armas: uma
munição básica (dispara em toda partida, munição ilimitada) e duas
munições secundárias (limitadas, ativadas com a tecla F — acumulam ao
tiro básico, ver `Player.shoot`).

A munição básica evolui com o tier da nave, entre as três únicas armas
capazes de disparo ilimitado: arma simples (tier 0), disparo duplo
(tier 1) e disparo triplo (tier 2 em diante — o teto da munição
básica). As duas munições secundárias são combinações das armas
especiais (HeavyLaser, QuadShot, HomingShot, GrenadeWeapon), cada nave
com uma dupla diferente, progressivamente mais rara/poderosa conforme
o tier sobe.
"""

from core.weapons.basic_weapon import (
    BasicWeapon,
    DoubleShot,
    TripolShot,
    HeavyLaser,
    QuadShot,
    HomingShot,
)
from core.weapons.player_weapon import GrenadeWeapon

MAX_TIER = 4

# Dupla de munições secundárias de cada tier de nave (as duas outras
# armas do arsenal, além da munição básica). Cada tier usa uma
# combinação própria; a nave de tier mais alto fica com a dupla mais
# forte (tiro teleguiado + granada).
_SECONDARY_WEAPONS_BY_TIER = {
    0: (HeavyLaser, QuadShot),
    1: (HeavyLaser, HomingShot),
    2: (QuadShot, HomingShot),
    3: (QuadShot, GrenadeWeapon),
    4: (HomingShot, GrenadeWeapon),
}


def _basic_weapon_for_tier(owner, tier):
    """Monta a munição básica da nave (dispara sempre, munição
    ilimitada): tiro simples na nave inicial (tier 0), disparo duplo a
    partir do tier 1 e disparo triplo a partir do tier 2 — o teto da
    munição básica, mesmo em tiers mais altos (que se diferenciam pelas
    munições secundárias, não pela básica)."""
    if tier <= 0:
        return BasicWeapon(owner, fire_rate=180)
    if tier == 1:
        # `ammo_max=None` = munição ilimitada, como pede a munição
        # básica (ao contrário do uso normal do disparo duplo como
        # munição secundária, com munição limitada e recarga).
        return DoubleShot(owner, fire_rate=400, ammo_max=None)
    return TripolShot(owner, fire_rate=450, ammo_max=None)


def build_weapons(owner, tier):
    """Monta o arsenal do jogador `owner`: sempre 3 armas — a munição
    básica (ver `_basic_weapon_for_tier`) na posição 0, seguida das
    duas munições secundárias da nave (ver `_SECONDARY_WEAPONS_BY_TIER`).
    Tiers acima do máximo configurado (`MAX_TIER`) usam a combinação da
    nave mais avançada, para não quebrar caso novas naves sejam
    adicionadas antes de seu tier de armas ser definido aqui."""
    tier = max(0, min(tier, MAX_TIER))

    basic_weapon = _basic_weapon_for_tier(owner, tier)
    secondary_a, secondary_b = _SECONDARY_WEAPONS_BY_TIER[tier]

    return [basic_weapon, secondary_a(owner), secondary_b(owner)]
