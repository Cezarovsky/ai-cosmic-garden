#!/usr/bin/env python3
"""
Nova RPG — prototip text-based, mediu de antrenare pentru Nova.
Zone cu putere FIXĂ (nu scalate după jucător) — scopul e varietate de
rapoarte de putere, nu progresie confortabilă. Zar d12, ca-n board games.
"""

import random

D12 = 12


class Character:
    def __init__(self, name, hp_max, dmg_min, dmg_max, defense=0, natural_attack=False,
                 weak_to=None, resist_to=None):
        self.name = name
        self.hp_max = hp_max
        self.hp = hp_max
        self.dmg_min = dmg_min
        self.dmg_max = dmg_max
        self.defense = defense
        # Atac natural (mușcătură, gheare): damage plafonat de HP-ul curent,
        # nu de un stat fix — o creatură rănită lovește mai slab.
        self.natural_attack = natural_attack
        # Tip elemental la care e vulnerabil/rezistent — motivul pentru care
        # o armă "mai slabă" rămâne în inventar, nu se aruncă niciodată.
        self.weak_to = weak_to
        self.resist_to = resist_to

    @property
    def alive(self):
        return self.hp > 0

    def roll_damage(self):
        if self.natural_attack:
            raw = random.randint(0, max(0, self.hp))
        else:
            raw = random.randint(self.dmg_min, self.dmg_max)
        return max(0, raw - self.defense)

    def effective_power(self):
        if self.natural_attack:
            avg_dmg = self.hp / 2  # plafonul curent de damage, nu unul fix
        else:
            avg_dmg = (self.dmg_min + self.dmg_max) / 2
        return (self.hp / self.hp_max) * avg_dmg


class Player(Character):
    def __init__(self):
        super().__init__("Tu", hp_max=20, dmg_min=1, dmg_max=3)  # pumni goi
        self.xp = 0
        self.level = 1
        self.weapon = {"name": "Pumni goi", "dmg_min": 1, "dmg_max": 3, "element": "fizic"}
        self.inventory = [self.weapon]  # armele NU se aruncă — rămân pentru matchup-ul potrivit
        self.x, self.y = GRID_SIZE // 2, GRID_SIZE // 2  # start în centrul grid-ului

    def register_kill(self, enemy):
        """Absoarbe vitalitatea prăzii — HP maxim și curent cresc cu HP_max al
        inamicului ucis. Nivelul crește automat la fiecare 100 XP acumulat."""
        self.hp_max += enemy.hp_max
        self.hp += enemy.hp_max
        self.xp += 10
        self.level = 1 + self.xp // 100

    def add_item(self, weapon):
        """Tot ce intri în posesie (drop de inamic sau conținut de cufăr) merge
        direct în inventar — fără acțiune separată de 'ridicare'. Nu se echipează
        automat; alegerea armei rămâne la choose_weapon(), înainte de luptă."""
        if weapon not in self.inventory:
            self.inventory.append(weapon)
        print(f"Ai primit: {weapon['name']} ({weapon['dmg_min']}-{weapon['dmg_max']} dmg, {weapon['element']})")

    def equip(self, weapon):
        self.weapon = weapon
        self.dmg_min, self.dmg_max = weapon["dmg_min"], weapon["dmg_max"]
        print(f"Echipat: {weapon['name']} ({weapon['dmg_min']}-{weapon['dmg_max']} dmg, {weapon['element']})")

    def choose_weapon(self):
        if not self.inventory:
            return
        options = self.inventory
        print("\nArme disponibile:")
        for i, w in enumerate(options, start=1):
            marker = " (echipată)" if w is self.weapon else ""
            print(f"  {i}. {w['name']} — {w['dmg_min']}-{w['dmg_max']} dmg, {w['element']}{marker}")
        choice = input(f"Schimbi arma? [1-{len(options)} / enter să rămâi cu curenta]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            self.equip(options[int(choice) - 1])


WEAPONS = {
    "sabie_ruginita": {"name": "Sabie ruginită", "dmg_min": 2, "dmg_max": 7, "element": "fizic"},
    "sabie_gheata": {"name": "Sabie de gheață", "dmg_min": 1, "dmg_max": 4, "element": "gheata"},
    "sulita_aur": {"name": "Suliță de aur", "dmg_min": 4, "dmg_max": 10, "element": "fizic"},
}

# Grid 8x8. (0,0) = colț nord-vest. x crește spre Est, y crește spre Sud.
GRID_SIZE = 8

EMPTY_ZONE = {"description": "Un câmp liniștit, nimic interesant.", "type": "empty"}

# Fabrici de inamici — creaturi refolosite în mai multe celule, pe o gamă largă
# de putere: de la musca trivială până la al doilea dragon, ca agentul să vadă
# tot spectrul de rapoarte pradă/prădător, nu doar extremele de acum.
def _musca():
    return Character("Muscă", hp_max=1, dmg_min=0, dmg_max=0, defense=0, natural_attack=True)

def _sobolan():
    return Character("Șoarece", hp_max=4, dmg_min=0, dmg_max=0, defense=0, natural_attack=True)

def _iepure():
    return Character("Iepure", hp_max=6, dmg_min=0, dmg_max=0, defense=0, natural_attack=True)

def _lup():
    return Character("Lup", hp_max=15, dmg_min=0, dmg_max=0, defense=1, natural_attack=True)

def _urs():
    return Character("Urs", hp_max=25, dmg_min=0, dmg_max=0, defense=2, natural_attack=True)

def _dragon():
    return Character("Dragon de foc", hp_max=40, dmg_min=0, dmg_max=0, defense=2,
                      natural_attack=True, weak_to="gheata", resist_to="fizic")


def _enemy_zone(desc, spawn_fn, loot_table):
    return {"description": desc, "type": "enemy", "spawn": spawn_fn, "loot_table": loot_table}


def _chest_zone(desc, contents):
    return {"description": desc, "type": "chest", "contents": list(contents)}


LOOT_TRIVIAL = [(95, None), (5, "sabie_ruginita")]
LOOT_MID = [(70, None), (30, "sabie_ruginita")]
LOOT_RARE = [(50, None), (30, "sabie_gheata"), (20, "sulita_aur")]

# Zone cu stats FIXE — deliberat, nu se scalează după nivelul jucătorului.
# type: "chest" (decizie explicită deschide/pleacă), "enemy" (luptă, loot la victorie), "empty".
# Grid 8x8 complet populat pe ~jumătate din celule (32/64) — restul rămân goale,
# ca mișcarea să aibă în continuare cost de explorare, nu doar întâlniri non-stop.
GRID = {
    (0, 0): _enemy_zone("O muscă bâzâie enervant în jurul tău.", _musca, LOOT_TRIVIAL),
    (2, 0): _chest_zone("Un cufăr mic, abandonat lângă un copac uscat.", ["sabie_ruginita"]),
    (4, 0): _enemy_zone("Altă muscă. Nu pare să te considere o amenințare.", _musca, LOOT_TRIVIAL),
    (6, 0): _enemy_zone("Un șoarece șuieră slab din iarbă.", _sobolan, LOOT_TRIVIAL),

    (0, 1): _enemy_zone("Un șoarece fuge dintr-o grămadă de moloz.", _sobolan, LOOT_TRIVIAL),
    (2, 1): _enemy_zone("Un iepure înghețat de frică te privește.", _iepure, LOOT_TRIVIAL),
    (5, 1): _chest_zone("Un cufăr acoperit de brumă.", ["sabie_gheata"]),
    (7, 1): _enemy_zone("O muscă bâzâie leneș pe lângă tine.", _musca, LOOT_TRIVIAL),

    (1, 2): _enemy_zone("Un iepure sare brusc din tufiș.", _iepure, LOOT_TRIVIAL),
    (3, 2): _chest_zone("Găsești un cufăr vechi, pe jumătate îngropat.", ["sabie_ruginita"]),
    (5, 2): _enemy_zone("Un șoarece se oprește, te adulmecă, apoi fuge.", _sobolan, LOOT_TRIVIAL),
    (7, 2): _enemy_zone("O muscă persistentă te urmărește de câțiva pași.", _musca, LOOT_TRIVIAL),

    (0, 3): _enemy_zone("Un iepure doarme, dar se trezește la pasul tău.", _iepure, LOOT_TRIVIAL),
    (2, 3): _enemy_zone("O muscă bâzâie în jurul unei grote goale.", _musca, LOOT_TRIVIAL),
    (4, 3): _chest_zone("În iarbă, aproape ascunsă, un cufăr mic, acoperit de mușchi.", ["sabie_gheata"]),
    (6, 3): _chest_zone("Un cufăr greu, legat în lanțuri ruginite.", ["sulita_aur"]),

    (1, 4): _chest_zone("Un cufăr de lemn, pe jumătate putrezit.", ["sabie_ruginita"]),
    (3, 4): _enemy_zone("Un lup te privește fix, de la 10 pași.", _lup, LOOT_MID),
    (5, 4): _enemy_zone("Un șoarece traversează grăbit poiana.", _sobolan, LOOT_TRIVIAL),
    (7, 4): _enemy_zone("Un iepure se oprește, apoi fuge câțiva pași, apoi se oprește iar.", _iepure, LOOT_TRIVIAL),

    (0, 5): _enemy_zone("Un iepure pândește de după o buturugă.", _iepure, LOOT_TRIVIAL),
    (2, 5): _enemy_zone("Un iepure scurmă pământul, nerăbdător.", _iepure, LOOT_TRIVIAL),
    (4, 5): _enemy_zone("O muscă singuratică, departe de celelalte.", _musca, LOOT_TRIVIAL),
    (6, 5): _enemy_zone("O muscă îți dă târcoale fără motiv aparent.", _musca, LOOT_TRIVIAL),

    (1, 6): _chest_zone("Un cufăr îngropat superficial în zăpadă.", ["sabie_gheata"]),
    (3, 6): _enemy_zone("Un șoarece se oprește, te adulmecă, apoi atacă oricum.", _sobolan, LOOT_TRIVIAL),
    (5, 6): _enemy_zone("Un șoarece mic, aproape invizibil în iarbă.", _sobolan, LOOT_TRIVIAL),
    (7, 6): _enemy_zone("Un iepure traversează în fugă, aproape nevăzut.", _iepure, LOOT_TRIVIAL),

    (0, 7): _enemy_zone("O ultimă muscă, la marginea hărții.", _musca, LOOT_TRIVIAL),
    (2, 7): _chest_zone("Un cufăr vechi, aproape uitat lângă margine.", ["sabie_ruginita"]),
    (4, 7): _enemy_zone("Un iepure stă în calea ta, la marginea sudică.", _iepure, LOOT_TRIVIAL),
    (6, 7): _enemy_zone("O muscă ultimă, la marginea hărții.", _musca, LOOT_TRIVIAL),
}

# Deplasări pe grid: (dx, dy) per direcție.
DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "V": (-1, 0)}


def available_directions(x, y):
    avail = []
    for d, (dx, dy) in DIRECTIONS.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            avail.append(d)
    return avail


def roll_loot(loot_table):
    weights = [w for w, _ in loot_table]
    items = [item for _, item in loot_table]
    return random.choices(items, weights=weights, k=1)[0]


def power_ratio(player, enemy):
    return player.effective_power() / max(0.01, enemy.effective_power())


def describe_ratio(ratio):
    if ratio >= 1.5:
        return "Ești clar prădător aici."
    if ratio >= 0.8:
        return "E echilibrat — risc real."
    return "Ești pradă aici. Ai grijă."


def elemental_multiplier(element, target):
    if target.weak_to and element == target.weak_to:
        return 1.5
    if target.resist_to and element == target.resist_to:
        return 0.5
    return 1.0


def combat(player, enemy):
    print(f"\n⚔️  Luptă: {player.name} ({player.hp} HP) vs {enemy.name} ({enemy.hp} HP)")
    if enemy.weak_to or enemy.resist_to:
        hint = []
        if enemy.weak_to:
            hint.append(f"vulnerabil la {enemy.weak_to}")
        if enemy.resist_to:
            hint.append(f"rezistent la {enemy.resist_to}")
        print(f"({enemy.name} pare {', '.join(hint)}.)")
    player.choose_weapon()

    ratio = power_ratio(player, enemy)
    mult = elemental_multiplier(player.weapon["element"], enemy)
    print(f"Raport de putere: {ratio:.2f} — {describe_ratio(ratio)}")
    if mult != 1.0:
        print(f"Multiplicator elemental ({player.weapon['element']} vs {enemy.name}): x{mult}")

    # Angajare forțată: pasul pe celulă declanșează lupta direct, fără decizie
    # premergătoare. Runda 1 e automată; fuga devine opțiune abia de la runda 2,
    # dacă ambii supraviețuiesc runda 1.
    round_num = 1
    while player.alive and enemy.alive:
        if round_num > 1:
            choice = input("Continui sau fugi? [l/f]: ").strip().lower()
            if choice == "f":
                flee_roll = random.randint(1, D12)
                if flee_roll > 4:
                    print(f"(zar={flee_roll}) Ai scăpat.")
                    return "fled"
                print(f"(zar={flee_roll}) Fuga a eșuat — inamicul te lovește gratis.")
                dmg = enemy.roll_damage()
                player.hp -= dmg
                print(f"Ai pierdut {dmg} HP ({max(0, player.hp)}/{player.hp_max}).")
                if not player.alive:
                    print("Ai murit fugind. Așa se întâmplă uneori.")
                    return "dead"
                continue

        print(f"\n--- Runda {round_num} ---")
        mult = elemental_multiplier(player.weapon["element"], enemy)
        dmg_to_enemy = round(player.roll_damage() * mult)
        enemy.hp -= dmg_to_enemy
        print(f"Lovești pe {enemy.name} cu {dmg_to_enemy}. ({max(0, enemy.hp)}/{enemy.hp_max} HP)")
        if not enemy.alive:
            print(f"{enemy.name} a murit. Ai câștigat.")
            player.register_kill(enemy)
            print(f"HP crescut la {player.hp}/{player.hp_max}. Nivel {player.level} ({player.xp} XP).")
            return "won"

        dmg_to_player = enemy.roll_damage()
        player.hp -= dmg_to_player
        print(f"{enemy.name} te lovește cu {dmg_to_player}. ({max(0, player.hp)}/{player.hp_max} HP)")
        if not player.alive:
            print("Ai murit.")
            return "dead"

        round_num += 1

    return "unknown"


def handle_chest(player, zone):
    while True:
        choice = input("Deschizi cufărul sau pleci? [d/p]: ").strip().lower()
        if choice == "d":
            for key in zone["contents"]:
                player.add_item(WEAPONS[key])
            zone["contents"] = []
            return
        if choice == "p":
            print("Pleci, lași cufărul neatins.")
            return
        print("Răspunde cu 'd' (deschide) sau 'p' (pleacă).")


def handle_enemy(player, zone):
    enemy = zone["spawn"]()
    result = combat(player, enemy)
    print(f"\nRezultat: {result}")
    if result == "won" and "loot_table" in zone:
        drop = roll_loot(zone["loot_table"])
        if drop:
            player.add_item(WEAPONS[drop])
        else:
            print(f"{enemy.name} nu a lăsat nimic.")


def explore(player):
    avail = available_directions(player.x, player.y)
    print(f"\nPoziție: ({player.x}, {player.y}). Direcții posibile: {', '.join(avail)}.")
    direction = input(f"Unde mergi? [{'/'.join(avail)}]: ").strip().upper()
    if direction not in avail:
        print("Direcție invalidă sau blocată de marginea hărții.")
        return

    dx, dy = DIRECTIONS[direction]
    player.x += dx
    player.y += dy

    zone = GRID.get((player.x, player.y), EMPTY_ZONE)
    print(zone["description"])

    if zone["type"] == "chest":
        handle_chest(player, zone)
    elif zone["type"] == "enemy":
        handle_enemy(player, zone)


def main():
    player = Player()
    print("=== Nova RPG — prototip text ===")
    print(f"Start: {player.hp}/{player.hp_max} HP, armă: {player.weapon['name']}\n")

    while player.alive:
        explore(player)
        if not player.alive:
            break
        again = input("\nContinui explorarea? [d/n]: ").strip().lower()
        if again != "d":
            break

    print(f"\nFinal. XP acumulat: {player.xp}")


if __name__ == "__main__":
    main()
