import pygame
import sys
import math
import random

pygame.init()

#this is designed to be similar to tower defense game, where you have to defend your tower from enemies and stuff
#not finished yet

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Tower Defense Game")

pygame.font.init()
FONT = pygame.font.SysFont("Arial", 24)

FPS = 60
clock = pygame.time.Clock()
GREEN = (3, 139, 34) #grass background
GRAY = (128, 128, 128) #enemy path
RED = (255, 0, 0) #enemy color
WHITE = (255, 255, 255) #text color
BLUE = (0, 0, 255) #tower color
YELLOW = (255, 255, 0) #bullet thingy color i think its called like a projecticle or something but too hard to spell don't judge

COLOR_NORMAL = (255, 0, 0) #red
COLOR_FAST = (255, 105, 180) #pink (fast)
COLOR_TANK = (139, 0, 0) #dark red (mega hard to kill and high damage to you but slow)

PATH = [(0, 300), (300, 300), (300, 100), (600, 100), (600, 600)]

player_lives = 10
spawn_timer = 0
SPAWN_COOLDOWN = 90
enemy_speed = 2.0
enemies = []

towers = []
TOWER_RADIUS = 20
TOWER_RANGE = 150
BULLET_SPEED = 7.0
FIRE_RATE = 45
bullets = []

player_gold = 150
TOWER_COST = 50
ENEMY_START_HP = 3
GOLD_PER_KILL = 15

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #left click
                mouse_pos = pygame.mouse.get_pos()
                on_path = False
                for point in PATH:
                    if abs(mouse_pos[0] - point[0]) < 25 and abs(mouse_pos[1] - point[1]) < 25:
                        on_path = True

                if not on_path and player_lives > 0 and player_gold >= TOWER_COST:
                    new_tower = {
                        "x": mouse_pos[0],
                        "y": mouse_pos[1],
                        "cooldown": 0
                    }
                    towers.append(new_tower)
                    player_gold -= TOWER_COST
    
    if player_lives > 0:
        spawn_timer += 1
        if spawn_timer >= SPAWN_COOLDOWN:
            rand_choice = random.random()
            if rand_choice < 0.60: #normal enemy
                e_hp = 3
                e_speed = 2.0
                e_damage = 1
                e_color = COLOR_NORMAL
                e_radius = 15
            elif rand_choice < 0.80: #fast enemy
                e_hp = 3
                e_speed = 4.5
                e_damage = 1
                e_color = COLOR_FAST
                e_radius = 12
            else: #tank enemy
                e_hp = 15
                e_speed = 0.7
                e_damage = 3
                e_color = COLOR_TANK
                e_radius = 24

            #add a new enemy at start of path
            new_enemy = {
                "id": random.getrandbits(32),
                "x": float(PATH[0][0]),
                "y": float(PATH[0][1]),
                "target_index": 1,
                "hp": e_hp,
                "speed": e_speed,
                "damage": e_damage,
                "color": e_color,
                "radius": e_radius
            }
            enemies.append(new_enemy)
            spawn_timer = 0

    for i in range(len(enemies) -1, -1, -1): #loop backwards to remove enemies
        enemy = enemies[i]

        if enemy["target_index"] < len(PATH):
            target_x, target_y = PATH[enemy["target_index"]]

            dx = target_x - enemy["x"]
            dy = target_y - enemy["y"]
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance <= enemy["speed"]:
                enemy["x"] = float(target_x)
                enemy["y"] = float(target_y)
                enemy["target_index"] += 1
            else:
                enemy["x"] += (dx / distance) * enemy["speed"]
                enemy["y"] += (dy / distance) * enemy["speed"]
        else:
            enemies.pop(i)
            player_lives -= enemy["damage"]
            if player_lives < 0:
                player_lives = 0

    if player_lives > 0:
        for tower in towers:
            if tower["cooldown"] > 0:
                tower["cooldown"] -= 1

            if tower["cooldown"] == 0:
                for enemy in enemies:
                    dx = enemy["x"] - tower["x"]
                    dy = enemy["y"] - tower["y"]
                    distance = math.sqrt(dx ** 2 + dy ** 2)

                    if distance <= TOWER_RANGE:
                        new_bullet = {
                            "x": float(tower["x"]),
                            "y": float(tower["y"]),
                            "target_id": enemy["id"]
                        }
                        bullets.append(new_bullet)
                        tower["cooldown"] = FIRE_RATE
                        break

        for i in range(len(bullets) -1, -1, -1):
            b = bullets[i]

            target_enemy = None
            for enemy in enemies:
                if enemy["id"] == b["target_id"]:
                    target_enemy = enemy
                    break

            if target_enemy is None:
                bullets.pop(i)
                continue

            bdx = target_enemy["x"] - b["x"]
            bdy = target_enemy["y"] - b["y"]
            b_dist = math.sqrt(bdx ** 2 + bdy ** 2)

            if b_dist <= BULLET_SPEED:
                bullets.pop(i)
                target_enemy["hp"] -= 1

                if target_enemy["hp"] <= 0:
                    if target_enemy in enemies:
                        enemies.remove(target_enemy)
                        player_gold += GOLD_PER_KILL
            else:
                b["x"] += (bdx / b_dist) * BULLET_SPEED
                b["y"] += (bdy/ b_dist) * BULLET_SPEED

            if b["x"] < 0 or b["x"] > SCREEN_WIDTH or b["y"] < 0 or b["y"] > SCREEN_HEIGHT:
                if i < len(bullets):
                    bullets.pop(i)

    screen.fill(GREEN)

    if len(PATH) > 1:
        pygame.draw.lines(screen, GRAY, False, PATH, width = 40)

    for tower in towers:
        pygame.draw.circle(screen, BLUE, (tower["x"], tower["y"]), TOWER_RADIUS)

    for b in bullets:
        pygame.draw.circle(screen, YELLOW, (int(b["x"]), int(b["y"])), 4)

    for enemy in enemies:
        pygame.draw.circle(screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), enemy["radius"])

    if player_lives > 0:
        lives_text = FONT.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(lives_text, (20, 20))

        gold_text = FONT.render(f"Gold: {player_gold}", True, YELLOW)
        screen.blit(gold_text, (20, 50))
    else:
        game_over_text = FONT. render("Game Over", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 12))

    pygame.display.flip()

pygame.quit()
sys.exit()