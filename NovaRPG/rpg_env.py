#!/usr/bin/env python3
"""
Nova RPG — mediu de antrenare, stil Gym (reset/step), fără text, fără taste.
Observație structurată in, acțiune in, recompensă out.

Recompensă: naturalistă, nu ponderi multiple calculate manual.
- Inamic mort -> recompensă = hp_max al inamicului (prada mai mare, carne mai multă).
- Jucător mort -> penalizare mare, fixă.
- Fugă (reușită sau eșuată, fără moarte) -> 0. Supraviețuirea nu se recompensează separat.
"""

import random

from rpg import (
    Player, GRID, GRID_SIZE, DIRECTIONS, EMPTY_ZONE, WEAPONS, D12,
    available_directions, power_ratio, elemental_multiplier, roll_loot,
)

DEATH_PENALTY = -100.0
MOVE_ACTIONS = ("N", "S", "E", "V")
COMBAT_ACTIONS = ("CONTINUE", "FLEE")


class _CombatState:
    def __init__(self, enemy, zone):
        self.enemy = enemy
        self.zone = zone
        self.round = 0


class NovaRPGEnv:
    def __init__(self):
        self.player = None
        self.combat = None
        self.done = False

    def reset(self):
        self.player = Player()
        self.combat = None
        self.done = False
        return self._observation()

    def _observation(self):
        p = self.player
        obs = {
            "hp_frac": max(0.0, p.hp / p.hp_max),
            "level": p.level,
            "weapon_element": p.weapon["element"],
            "x": p.x,
            "y": p.y,
            "available_directions": available_directions(p.x, p.y) if self.combat is None else [],
            "in_combat": self.combat is not None,
            "enemy_hp_frac": 0.0,
            "power_ratio": 0.0,
            "elemental_mult": 1.0,
            "round": 0,
        }
        if self.combat is not None:
            enemy = self.combat.enemy
            obs["enemy_hp_frac"] = max(0.0, enemy.hp / enemy.hp_max)
            obs["power_ratio"] = power_ratio(p, enemy)
            obs["elemental_mult"] = elemental_multiplier(p.weapon["element"], enemy)
            obs["round"] = self.combat.round
        return obs

    def _resolve_round(self):
        """O rundă de luptă. Întoarce reward-ul produs de runda asta (0, kill, sau penalizare)."""
        p = self.player
        combat = self.combat
        enemy = combat.enemy
        combat.round += 1

        mult = elemental_multiplier(p.weapon["element"], enemy)
        dmg_to_enemy = round(p.roll_damage() * mult)
        enemy.hp -= dmg_to_enemy

        if not enemy.alive:
            reward = float(enemy.hp_max)  # carnea prăzii = recompensa (semnal RL, separat de starea jucătorului)
            p.register_kill(enemy)  # HP max/curent + XP/nivel cresc, dar NU afectează reward-ul
            loot_table = combat.zone.get("loot_table")
            if loot_table:
                drop = roll_loot(loot_table)
                if drop:
                    p.add_item(WEAPONS[drop])
            self.combat = None
            return reward

        dmg_to_player = enemy.roll_damage()
        p.hp -= dmg_to_player

        if not p.alive:
            self.combat = None
            self.done = True
            return DEATH_PENALTY

        return 0.0

    def _attempt_flee(self):
        p = self.player
        enemy = self.combat.enemy
        roll = random.randint(1, D12)
        if roll > 4:
            self.combat = None
            return 0.0

        dmg = enemy.roll_damage()
        p.hp -= dmg
        if not p.alive:
            self.combat = None
            self.done = True
            return DEATH_PENALTY
        return 0.0

    def step(self, action):
        if self.done:
            raise RuntimeError("Episodul s-a terminat — apelează reset().")

        reward = 0.0
        p = self.player

        if self.combat is not None:
            if action == "FLEE":
                reward = self._attempt_flee()
            elif action == "CONTINUE":
                reward = self._resolve_round()
            else:
                raise ValueError(f"Acțiune invalidă în luptă: {action!r} (așteptat {COMBAT_ACTIONS})")
        else:
            if action not in MOVE_ACTIONS:
                raise ValueError(f"Acțiune invalidă în explorare: {action!r} (așteptat {MOVE_ACTIONS})")
            if action in available_directions(p.x, p.y):
                dx, dy = DIRECTIONS[action]
                p.x += dx
                p.y += dy
                zone = GRID.get((p.x, p.y), EMPTY_ZONE)
                if zone["type"] == "chest":
                    for key in zone["contents"]:
                        p.add_item(WEAPONS[key])
                    zone["contents"] = []
                elif zone["type"] == "enemy":
                    enemy = zone["spawn"]()
                    self.combat = _CombatState(enemy, zone)
                    reward = self._resolve_round()  # runda 1, forțată
            # mutare blocată de margine -> no-op, reward 0

        return self._observation(), reward, self.done, {}


if __name__ == "__main__":
    # Smoke test: joc aleator, ca să verificăm că nu crapă nimic.
    env = NovaRPGEnv()
    obs = env.reset()
    total_reward = 0.0
    for step_num in range(200):
        if obs["in_combat"]:
            action = random.choice(COMBAT_ACTIONS)
        else:
            action = random.choice(MOVE_ACTIONS)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        if reward != 0:
            print(f"pas {step_num}: acțiune={action}, reward={reward}, hp={obs['hp_frac']:.2f}")
        if done:
            print(f"Episod terminat la pasul {step_num}. Reward total: {total_reward}")
            break
    else:
        print(f"200 de pași fără moarte. Reward total: {total_reward}")
