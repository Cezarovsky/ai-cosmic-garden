#!/usr/bin/env python3
"""
Nova RPG — versiune grafică Pygame, fără input text deloc.
Mișcare: săgeți, punctul sare direct în centrul celulei vecine.
Luptă: runda 1 automată la intrare. De la runda 2 — ENTER continuă lupta,
orice SĂGEATĂ încearcă să fugă. Cufăr: ENTER deschide, SĂGEATĂ pleacă.
"""

import sys
import random
import pygame

from rpg import (
    Player, GRID, GRID_SIZE, DIRECTIONS, EMPTY_ZONE, WEAPONS, D12,
    available_directions, power_ratio, describe_ratio, elemental_multiplier,
    roll_loot,
)

CELL_SIZE = 72
PANEL_HEIGHT = 180
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + PANEL_HEIGHT

COLOR_BG = (20, 20, 25)
COLOR_GRID = (60, 60, 70)
COLOR_EMPTY = (35, 35, 40)
COLOR_CHEST = (150, 120, 40)
COLOR_ENEMY = (140, 30, 30)
COLOR_PLAYER = (60, 200, 255)
COLOR_TEXT = (230, 230, 230)
COLOR_PANEL = (15, 15, 20)
COLOR_HINT = (140, 200, 140)

ARROW_KEYS = {
    pygame.K_UP: "N",
    pygame.K_DOWN: "S",
    pygame.K_RIGHT: "E",
    pygame.K_LEFT: "V",
}

COLOR_INVENTORY_SELECTED = (90, 220, 120)


class CombatState:
    def __init__(self, enemy):
        self.enemy = enemy
        self.round = 0
        self.log = []
        self.over = False
        self.result = None

    def say(self, msg):
        self.log.append(msg)
        self.log = self.log[-6:]


class ChestState:
    def __init__(self, zone):
        self.zone = zone
        self.over = False
        self.log = [f"Cufăr: {zone['description']}", "ENTER = deschide   SĂGEATĂ = pleacă"]


def resolve_round(player, combat):
    combat.round += 1
    enemy = combat.enemy
    mult = elemental_multiplier(player.weapon["element"], enemy)
    dmg_to_enemy = round(player.roll_damage() * mult)
    enemy.hp -= dmg_to_enemy
    combat.say(f"Runda {combat.round}: lovești {enemy.name} cu {dmg_to_enemy} ({max(0, enemy.hp)}/{enemy.hp_max} HP)")

    if not enemy.alive:
        combat.say(f"{enemy.name} a murit. Ai câștigat.")
        player.register_kill(enemy)
        combat.say(f"HP {player.hp}/{player.hp_max} — Nivel {player.level} ({player.xp} XP)")
        drop = roll_loot(combat.zone_loot) if hasattr(combat, "zone_loot") else None
        if drop:
            item = WEAPONS[drop]
            if item not in player.inventory:
                player.inventory.append(item)
            combat.say(f"A lăsat: {item['name']} ({item['dmg_min']}-{item['dmg_max']} dmg, {item['element']})")
        else:
            combat.say(f"{enemy.name} nu a lăsat nimic.")
        combat.over = True
        combat.result = "won"
        return

    dmg_to_player = enemy.roll_damage()
    player.hp -= dmg_to_player
    combat.say(f"{enemy.name} te lovește cu {dmg_to_player} ({max(0, player.hp)}/{player.hp_max} HP)")
    if not player.alive:
        combat.say("Ai murit.")
        combat.over = True
        combat.result = "dead"


def attempt_flee(player, combat):
    enemy = combat.enemy
    roll = random.randint(1, D12)
    if roll > 4:
        combat.say(f"(zar={roll}) Ai scăpat.")
        combat.over = True
        combat.result = "fled"
        return
    combat.say(f"(zar={roll}) Fuga a eșuat — lovitură gratis.")
    dmg = enemy.roll_damage()
    player.hp -= dmg
    combat.say(f"Ai pierdut {dmg} HP ({max(0, player.hp)}/{player.hp_max}).")
    if not player.alive:
        combat.say("Ai murit fugind.")
        combat.over = True
        combat.result = "dead"


def start_combat(player, zone):
    enemy = zone["spawn"]()
    combat = CombatState(enemy)
    combat.zone_loot = zone.get("loot_table")
    ratio = power_ratio(player, enemy)
    mult = elemental_multiplier(player.weapon["element"], enemy)
    combat.say(f"{enemy.name} ({enemy.hp} HP) — raport putere {ratio:.2f}: {describe_ratio(ratio)}")
    if mult != 1.0:
        combat.say(f"Multiplicator elemental: x{mult}")
    resolve_round(player, combat)  # runda 1, forțată
    return combat


def open_chest(player, chest):
    zone = chest.zone
    for key in zone["contents"]:
        item = WEAPONS[key]
        if item not in player.inventory:
            player.inventory.append(item)
        chest.log.append(f"Ai primit: {item['name']} ({item['dmg_min']}-{item['dmg_max']} dmg, {item['element']})")
    zone["contents"] = []
    chest.over = True


def leave_chest(chest):
    chest.log.append("Ai plecat, cufărul rămâne neatins.")
    chest.over = True


def cell_color(x, y):
    zone = GRID.get((x, y), EMPTY_ZONE)
    if zone["type"] == "chest":
        return COLOR_CHEST
    if zone["type"] == "enemy":
        return COLOR_ENEMY
    return COLOR_EMPTY


def draw(screen, font, player, combat, chest, inventory_open, inventory_cursor):
    screen.fill(COLOR_BG)
    for gx in range(GRID_SIZE):
        for gy in range(GRID_SIZE):
            rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, cell_color(gx, gy), rect)
            pygame.draw.rect(screen, COLOR_GRID, rect, 1)

    px = player.x * CELL_SIZE + CELL_SIZE // 2
    py = player.y * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, COLOR_PLAYER, (px, py), CELL_SIZE // 4)

    panel_rect = pygame.Rect(0, GRID_SIZE * CELL_SIZE, WIDTH, PANEL_HEIGHT)
    pygame.draw.rect(screen, COLOR_PANEL, panel_rect)

    y = GRID_SIZE * CELL_SIZE + 8

    if inventory_open:
        screen.blit(font.render("Inventar — SUS/JOS alege, ENTER echipează, I închide", True, COLOR_HINT), (10, y))
        y += 24
        for i, w in enumerate(player.inventory):
            marker = "> " if i == inventory_cursor else "  "
            equipped = " (echipată)" if w is player.weapon else ""
            color = COLOR_INVENTORY_SELECTED if i == inventory_cursor else COLOR_TEXT
            line = f"{marker}{w['name']} — {w['dmg_min']}-{w['dmg_max']} dmg, {w['element']}{equipped}"
            screen.blit(font.render(line, True, color), (10, y))
            y += 20
        return

    if combat is not None:
        for line in combat.log:
            screen.blit(font.render(line, True, COLOR_TEXT), (10, y))
            y += 20
        if not combat.over:
            hint = "ENTER = continuă lupta   SĂGEATĂ = încearcă să fugi"
            screen.blit(font.render(hint, True, COLOR_HINT), (10, GRID_SIZE * CELL_SIZE + PANEL_HEIGHT - 24))
    elif chest is not None:
        for line in chest.log:
            screen.blit(font.render(line, True, COLOR_TEXT), (10, y))
            y += 20
    else:
        status = (f"HP {max(0, player.hp)}/{player.hp_max}   Nivel {player.level}   "
                  f"Armă: {player.weapon['name']}   XP: {player.xp}   "
                  f"Poziție: ({player.x},{player.y})")
        screen.blit(font.render(status, True, COLOR_TEXT), (10, y))
        screen.blit(font.render("Mișcă-te cu săgețile.", True, COLOR_HINT), (10, y + 24))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Nova RPG")
    font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()

    player = Player()
    combat = None
    chest = None
    inventory_open = False
    inventory_cursor = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and player.alive:
                print(f"[LOG] tastă apăsată: {pygame.key.name(event.key)!r} (cod {event.key}), inventory_open={inventory_open}")
                # --- Inventar (prioritate peste orice altceva, nu modifică starea jocului) ---
                if inventory_open:
                    if event.key == pygame.K_i:
                        print("[LOG] închid inventarul")
                        inventory_open = False
                    elif event.key == pygame.K_UP:
                        inventory_cursor = (inventory_cursor - 1) % len(player.inventory)
                        print(f"[LOG] cursor inventar -> {inventory_cursor}")
                    elif event.key == pygame.K_DOWN:
                        inventory_cursor = (inventory_cursor + 1) % len(player.inventory)
                        print(f"[LOG] cursor inventar -> {inventory_cursor}")
                    elif event.key == pygame.K_RETURN:
                        player.equip(player.inventory[inventory_cursor])
                        inventory_open = False
                    continue  # ignoră orice altă tastă cât inventarul e deschis

                if event.key == pygame.K_i:
                    inventory_open = True
                    inventory_cursor = player.inventory.index(player.weapon) if player.weapon in player.inventory else 0
                    print(f"[LOG] deschid inventarul, {len(player.inventory)} arme, cursor={inventory_cursor}")
                    continue

                # --- Luptă activă ---
                if combat is not None and not combat.over:
                    if event.key == pygame.K_RETURN:
                        resolve_round(player, combat)
                    elif event.key in ARROW_KEYS:
                        attempt_flee(player, combat)

                # --- Cufăr activ ---
                elif chest is not None and not chest.over:
                    if event.key == pygame.K_RETURN:
                        open_chest(player, chest)
                    elif event.key in ARROW_KEYS:
                        leave_chest(chest)

                # --- Mișcare liberă ---
                elif event.key in ARROW_KEYS:
                    combat = None
                    chest = None
                    direction = ARROW_KEYS[event.key]
                    if direction in available_directions(player.x, player.y):
                        dx, dy = DIRECTIONS[direction]
                        player.x += dx
                        player.y += dy
                        zone = GRID.get((player.x, player.y), EMPTY_ZONE)
                        if zone["type"] == "chest":
                            chest = ChestState(zone)
                        elif zone["type"] == "enemy":
                            combat = start_combat(player, zone)

        if not player.alive:
            print(f"[LOG] ai murit — nivel {player.level}, XP {player.xp}. Restart automat.")
            player = Player()
            combat = None
            chest = None
            inventory_open = False
            inventory_cursor = 0

        draw(screen, font, player, combat, chest, inventory_open, inventory_cursor)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
