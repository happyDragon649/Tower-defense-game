import pygame
import sys
import math
import random

pygame.init()

#this is designed to be similar to tower defense game, where you have to defend your tower from enemies and stuff
#not finished yet

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Tower Defense Game")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 22)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
LARGE_FONT = pygame.font.SysFont("Arial", 40)
MEDIUM_FONT = pygame.font.SysFont("Arial", 30)

GREEN = (3, 139, 34) #grass background
GRAY = (128, 128, 128) #enemy path
RED = (255, 0, 0) #enemy color
WHITE = (255, 255, 255) #text color
BLUE = (0, 0, 255) #tower color
YELLOW = (255, 255, 0) #bullet thingy color i think its called like a projecticle or something but too hard to spell don't judge
BLACK = (0, 0, 0)
CYAN = (0, 255, 255) #tower selection outline
PURPLE = (180, 80, 255) #3rd level tower color

COLOR_NORMAL = (255, 0, 0) #red
COLOR_FAST = (255, 105, 180) #pink (fast)
COLOR_TANK = (139, 0, 0) #dark red (mega hard to kill and high damage to you but slow)

PATH = [(0, 300), (300, 300), (300, 100), (600, 100), (600, 600)]

PATH_WIDTH = 40

TOWER_RADIUS = 20
TOWER_RANGE = 150
TOWER_COST = 50

BULLET_SPEED = 7.0
GOLD_PER_KILL = 15

MAX_WAVES = 10
WAVE_BREAK_DURATION = 180

TOWER_DAMAGE = {
    1: 1,
    2: 2,
    3: 3
}

TOWER_FIRE_RATE = {
    1: 45,
    2: 30,
    3: 20
}

UPGRADE_COST = {
    1: 75,
    2: 125
}

TOWER_COLORS = {
    1: BLUE,
    2: (0, 220, 220),
    3: PURPLE
}

def reset_game():
    return {
        "lives": 10,
        "gold": 150,
        "towers": [],
        "enemies": [],
        "bullets": [],
        "current_wave": 1,
        "enemies_to_spawn": 5,
        "enemies_spawned": 0,
        "spawn_timer": 0,
        "spawn_cooldown": 90,
        "wave_break_timer": 0,
        "in_wave_break": False,
        "game_over": False,
        "game_won": False,
        "selected_tower": None
    }

game = reset_game()

def distance_to_segment(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    length_squared = dx * dx + dy * dy

    if length_squared == 0:
        return math.hypot(px - ax, py - ay)

    t = ((px - ax) * dx + (py - ay) * dy) / length_squared
    t = max(0, min(1, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.hypot(px - closest_x, py - closest_y)

def position_on_path(x, y):
    for i in range(len(PATH) - 1):
        ax, ay = PATH[i]
        bx, by = PATH[i + 1]

        if distance_to_segment(x, y, ax, ay, bx, by) < (PATH_WIDTH/2 + TOWER_RADIUS):
            return True

    return False

def get_tower_at_position(x, y):
    for tower in reversed(game["towers"]):
        distance = math.hypot(x - tower["x"], y - tower["y"])

        if distance <= TOWER_RADIUS + 5:
            return tower

    return None

def place_tower(x, y):
    if game["game_over"] or game["game_won"]:
        return

    if game["gold"] < TOWER_COST:
        return

    if not (TOWER_RADIUS <= x <= SCREEN_WIDTH - TOWER_RADIUS and TOWER_RADIUS <= y <= SCREEN_HEIGHT - TOWER_RADIUS):
        return

    if position_on_path(x, y):
        return

    for tower in game["towers"]:
        if math.hypot(x - tower["x"], y - tower["y"]) < TOWER_RADIUS * 2:
            return

    new_tower = {
        "x": x,
        "y": y,
        "level": 1,
        "cooldown": 0
    }

    game["towers"].append(new_tower)
    game["gold"] -= TOWER_COST

    game["selected_tower"] = new_tower

def upgrade_selected_tower():
    tower = game["selected_tower"]

    if tower is None:
        return

    if game["game_over"] or game["game_won"]:
        return

    level = tower["level"]

    if level >= 3:
        return

    cost = UPGRADE_COST[level]

    if game["gold"] < cost:
        return

    game["gold"] -= cost
    tower["level"] += 1

    tower["cooldown"] = 0

def spawn_enemy():
    wave = game["current_wave"]

    hp_multiplier = 1.0 + (wave - 1) * 0.45
    speed_multiplier = 1.0 + (wave - 1) * 0.12

    choice = random.random()

    if choice < 0.50:
        hp = int(3 * hp_multiplier)
        speed = 2.0 * speed_multiplier
        damage = 1
        color = COLOR_NORMAL
        radius = 15

    elif choice < 0.75:
        hp = int(3 * hp_multiplier)
        speed = 4.5 * speed_multiplier
        damage = 1
        color = COLOR_FAST
        radius = 12

    else:
        hp = int(18 * hp_multiplier)
        speed = 0.7 * speed_multiplier
        damage = 4
        color = COLOR_TANK
        radius = 26

    game["enemies"].append({
        "id": random.getrandbits(32),
        "x": float(PATH[0][0]),
        "y": float(PATH[0][1]),
        "target_index": 1,
        "hp": hp,
        "max_hp": hp,
        "speed": speed,
        "damage": damage,
        "color": color,
        "radius": radius
    })

    game["enemies_spawned"] += 1

def update_enemies():
    for i in range(len(game["enemies"]) - 1, -1, -1):
        enemy = game["enemies"][i]

        if enemy["target_index"] >= len(PATH):
            game["lives"] = max(0, game["lives"] - enemy["damage"])
            game["enemies"].pop(i)
            continue

        target_x , target_y = PATH[enemy["target_index"]]

        dx = target_x - enemy["x"]
        dy = target_y - enemy["y"]
        distance = math.hypot(dx, dy)

        if distance <= enemy["speed"]:
            enemy["x"] = float(target_x)
            enemy["y"] = float(target_y)
            enemy["target_index"] += 1

        elif distance > 0:
            enemy["x"] += dx/distance * enemy["speed"]
            enemy["y"] += dy/distance * enemy["speed"]

def update_towers():
    for tower in game["towers"]:
        if tower["cooldown"] > 0:
            tower["cooldown"] -= 1

        if tower["cooldown"] > 0:
            continue

        for enemy in game["enemies"]:
            distance = math.hypot(enemy["x"] - tower["x"], enemy["y"] - tower["y"])

            if distance <= TOWER_RANGE:
                game["bullets"].append({
                    "x": float(tower["x"]),
                    "y": float(tower["y"]),
                    "target_id": enemy["id"],
                    "damage": TOWER_DAMAGE[tower["level"]]
                })

                tower["cooldown"] = TOWER_FIRE_RATE[tower["level"]]
                break

def update_bullets():
    for i in range(len(game["bullets"]) - 1, -1, -1):
        bullet = game["bullets"][i]

        target = next(
            (
                enemy for enemy in game["enemies"]
                if enemy["id"] == bullet["target_id"]
            ),
            None
        )

        if target is None:
            game["bullets"].pop(i)
            continue

        dx = target["x"] - bullet["x"]
        dy = target["y"] - bullet["y"]
        distance = math.hypot(dx, dy)

        if distance <= BULLET_SPEED:
            game["bullets"].pop(i)

            target["hp"] -= bullet["damage"]

            if target["hp"] <= 0:
                if target in game["enemies"]:
                    game["enemies"].remove(target)
                    game["gold"] += GOLD_PER_KILL

        elif distance > 0:
            bullet["x"] += dx/distance * BULLET_SPEED
            bullet["y"] += dy/distance * BULLET_SPEED

def start_next_wave():
    game["current_wave"] += 1
    game["enemies_spawned"] = 0

    game["enemies_to_spawn"] = (int(game["enemies_to_spawn"] * 1.5) + 3)

    game["spawn_cooldown"] = max(20, game["spawn_cooldown"] - 12)

    game["spawn_timer"] = 0
    game["wave_break_timer"] = 0
    game["in_wave_break"] = True

def draw_centered(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center = (SCREEN_WIDTH // 2, y))
    screen.blit(surface, rect)

def draw_game():
    screen.fill(GREEN)

    pygame.draw.lines(screen, GRAY, False, PATH, PATH_WIDTH)

    screen.blit(
        SMALL_FONT.render(
            f"Lives: {game['lives']}", True, WHITE
        ),
        (15, 12)
    )

    screen.blit(
        SMALL_FONT.render(
            f"Gold: {game['gold']}", True, YELLOW
        ),
        (15, 36)
    )

    screen.blit(
        SMALL_FONT.render(
            f"Wave: {game['current_wave']}/{MAX_WAVES}",
            True, WHITE
        ),
        (15, 60)
    )

    selected = game["selected_tower"]

    if selected is not None:
        pygame.draw.circle(
            screen, CYAN,
            (selected["x"], selected["y"]),
            TOWER_RANGE, 1
        )

    for tower in game["towers"]:
        color = TOWER_COLORS[tower["level"]]

        pygame.draw.circle(
            screen, color,
            (tower["x"], tower["y"]),
            TOWER_RADIUS
        )

        level_text = SMALL_FONT.render(str(tower["level"]), True, WHITE)
        level_rect = level_text.get_rect(center = (tower["x"], tower["y"]))
        screen.blit(level_text, level_rect)

        if tower is selected:
            pygame.draw.circle(
                screen, CYAN,
                (tower["x"], tower["y"]),
                TOWER_RADIUS + 4, 3
            )

    for bullet in game["bullets"]:
        pygame.draw.circle(
            screen, YELLOW,
            (int(bullet["x"]), int(bullet["y"])), 4
        )

    for enemy in game["enemies"]:
        pygame.draw.circle(
            screen, enemy["color"],
            (int(enemy["x"]), int(enemy["y"])),
            enemy["radius"]
        )

        bar_width = enemy["radius"] * 2
        bar_height = 5
        bar_x = int(enemy["x"] - bar_width/2)
        bar_y = int(enemy["y"] - enemy["radius"] - 10)

        hp_ratio = max(0, min(1, enemy["hp"]/enemy["max_hp"]))

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

    if selected is not None:
        panel = pygame.Rect(565, 350, 220, 220)

        pygame.draw.rect(screen, BLACK, panel, border_radius = 10)
        pygame.draw.rect(screen, WHITE, panel, 2, border_radius = 10)

        level = selected["level"]

        lines = [
            ("Selected Tower", YELLOW),
            (f"Level: {level}/3", WHITE),
            (f"Damage: {TOWER_DAMAGE[level]}", WHITE),
            (f"Fire Rate: {TOWER_FIRE_RATE[level]} frames", WHITE)
        ]

        for index, (text, color) in enumerate(lines):
            surface = SMALL_FONT.render(text, True, color)
            screen.blit(surface, (578, 360 + index * 27))

        if level < 3:
            cost = UPGRADE_COST[level]

            if game["gold"] >= cost:
                upgrade_color = (100, 255, 100)
            else:
                upgrade_color = RED

            screen.blit(SMALL_FONT.render(f"Upgrade: {cost} gold", True, upgrade_color), (578, 475))

            screen.blit(SMALL_FONT.render("Press U to upgrade", True, WHITE), (578, 500))

        else:
            screen.blit(SMALL_FONT.render("MAX LEVEL!", True, YELLOW), (578, 475))

        screen.blit(SMALL_FONT.render("Click another tower", True, WHITE), (578, 530))

    screen.blit(SMALL_FONT.render("Click grass: build (50 gold)", True, WHITE), (15, SCREEN_HEIGHT - 48))

    screen.blit(SMALL_FONT.render("Click tower: select | U: upgrade", True, WHITE), (15, SCREEN_HEIGHT - 25))

    if game["in_wave_break"] and not game["game_over"]:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        draw_centered(f"WAVE {game['current_wave']}", LARGE_FONT, WHITE, SCREEN_HEIGHT // 2 - 75)
        draw_centered("Get ready!", MEDIUM_FONT, YELLOW, SCREEN_HEIGHT // 2 - 35)

    if game["game_over"]:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        draw_centered("GAME OVER", LARGE_FONT, RED, SCREEN_HEIGHT // 2 - 45)
        draw_centered(f"You reached Wave {game['current_wave']}", MEDIUM_FONT, WHITE, SCREEN_HEIGHT // 2 + 10)
        draw_centered("Press ESC to quit", FONT, WHITE, SCREEN_HEIGHT // 2 + 55)

    elif game["game_won"]:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        draw_centered("VICTORY!", LARGE_FONT, YELLOW, SCREEN_HEIGHT // 2 - 30)
        draw_centered("Press ESC to quit", FONT, WHITE, SCREEN_HEIGHT // 2 + 70)

    pygame.display.flip()

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_u:
                upgrade_selected_tower()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game["game_over"] and not game["game_won"]:
                mouse_x, mouse_y = event.pos

                clicked_tower = get_tower_at_position(mouse_x, mouse_y)

                if clicked_tower is not None:
                    game["selected_tower"] = clicked_tower

                else:
                    mouse_pos = place_tower(mouse_x, mouse_y)

    if not game["game_over"] and not game["game_won"]:
        if game["in_wave_break"]:
            game["wave_break_timer"] += 1

            if game["wave_break_timer"] >= WAVE_BREAK_DURATION:
                game["in_wave_break"] = False
                game["wave_break_timer"] = 0

        else:
            if game["enemies_spawned"] < game["enemies_to_spawn"]:
                game["spawn_timer"] += 1

                if game["spawn_timer"] >= game["spawn_cooldown"]:
                    spawn_enemy()
                    game["spawn_timer"] = 0

            update_enemies()
            update_towers()
            update_bullets()

            if game["lives"] <= 0:
                game["lives"] = 0
                game["game_over"] = True

            elif game["enemies_spawned"] >= game["enemies_to_spawn"] and len(game["enemies"]) == 0:
                if game["current_wave"] >= MAX_WAVES:
                    game["game_won"] = True
                else:
                    start_next_wave()

    draw_game()

pygame.quit()
sys.exit()