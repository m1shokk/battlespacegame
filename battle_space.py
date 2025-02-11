import pygame
import sys
import random
import time
import json
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
screen_width = 800
screen_height = 600

# Création de la fenêtre
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle Space")

# Charger l'image de fond
background_image = pygame.image.load("./images/fond.jpg")
asteroid_background = pygame.image.load("./images/asteroid.jpg")
extra_background = pygame.image.load("./images/extra.jpg")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
asteroid_background = pygame.transform.scale(asteroid_background, (screen_width, screen_height))
extra_background = pygame.transform.scale(extra_background, (screen_width, screen_height))

backgrounds = [background_image, asteroid_background, extra_background]
current_background = backgrounds[0]
level = 1

# Charger l'image du personnage et des bonus
spaceship_image = pygame.image.load("./images/spaceship.png")
boom_image = pygame.image.load("./images/boom.png")
head_image = pygame.image.load("./images/head.png")
head_def_image = pygame.image.load("./images/head_def.png")
head_speed_image = pygame.image.load("./images/head_speed.png")
explosion_image = pygame.image.load("./images/explosion.png")
heart_image = pygame.image.load("./images/coeur.png")
heart_off_image = pygame.image.load("./images/coeur_off.png")
snow_image = pygame.image.load("./images/neige.png") 
laser_image = pygame.image.load("./images/laser.png")

# Redimensionner le personnage à 20 % de sa taille d'origine
original_width, original_height = spaceship_image.get_size()
new_width = int(original_width * 0.2)
new_height = int(original_height * 0.2)
spaceship_image = pygame.transform.scale(spaceship_image, (new_width, new_height))

# Redimensionner le projectile, le head et les bonus
boom_image = pygame.transform.scale(boom_image, (40, 50))
head_image = pygame.transform.scale(head_image, (80, 80))
head_def_image = pygame.transform.scale(head_def_image, (80, 80))
head_speed_image = pygame.transform.scale(head_speed_image, (80, 80))
explosion_image = pygame.transform.scale(explosion_image, (80, 80))
heart_image = pygame.transform.scale(heart_image, (30, 30))
heart_off_image = pygame.transform.scale(heart_off_image, (30, 30))
snow_image = pygame.transform.scale(snow_image, (40, 40))
laser_image = pygame.transform.scale(laser_image, (40, 40))

# Boss
boss_image = pygame.transform.scale(head_image, (240, 240))
boss_active = False
boss_health = 50
boss_x = (screen_width - 240) // 2
boss_y = 50
boss_last_shot = 0
boss_shot_delay = 2000  # 2 secondes
boss_projectiles = []
enemies_killed = 0
boss_direction = 1  # 1 pour droite, -1 pour gauche
boss_speed = 0.3
boss_vertical_speed = 0.1
boss_max_y = 200  # Position Y maximale du boss

# Position initiale du personnage
initial_x = (screen_width - new_width) // 2
initial_y = screen_height - new_height - 50
spaceship_x = initial_x
spaceship_y = initial_y

# Liste pour stocker les projectiles, les heads, les explosions et les bonus
projectiles = []
heads = []  # [x, y, type, health] - type: 0 normal, 1 defense, 2 speed
explosions = []
bonuses = []  # [x, y, type, spawn_time] - type: 0 coeur, 1 neige, 2 laser

# Variables pour les bonus
bonus_speed = 0.3
heart_spawn_time = 0
snow_spawn_time = 0
laser_spawn_time = 0
snow_active = False
snow_end_time = 0
laser_active = False
laser_end_time = 0

# Score et meilleur score
score = 0
try:
    with open('highscore.json', 'r') as f:
        high_score = json.load(f)['high_score']
except:
    high_score = 0

# Police pour le texte
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Vies du joueur et mode GOD
player_lives = 3
god_mode = False
god_code = ""

# Vitesse de déplacement du vaisseau
base_speed = 0.6
speed = base_speed
projectile_speed = 0.8
head_speed = 0.3
head_speed_fast = 0.5  # Vitesse pour le head rapide

# Variables pour les niveaux
spawn_speed_bonus = 0
mob_speed_bonus = 0
player_speed_bonus = 0

def show_game_over_screen():
    global score, high_score, running, boss_active, enemies_killed, boss_health, level, current_background, spawn_speed_bonus, mob_speed_bonus, player_speed_bonus, speed
    
    if score > high_score:
        high_score = score
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': high_score}, f)
    
    game_over = True
    while game_over:
        screen.fill((0, 0, 0))
        
        game_over_text = font.render("Game Over!", True, (255, 255, 255))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        high_score_text = font.render(f"Meilleur score: {high_score}", True, (255, 255, 255))
        restart_text = font.render("Cliquez pour recommencer", True, (255, 255, 255))
        
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 200))
        screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, 250))
        screen.blit(high_score_text, (screen_width//2 - high_score_text.get_width()//2, 300))
        screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, 400))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                boss_active = False
                enemies_killed = 0
                boss_health = 50
                boss_projectiles.clear()
                level = 1
                current_background = backgrounds[0]
                spawn_speed_bonus = 0
                mob_speed_bonus = 0
                player_speed_bonus = 0
                speed = base_speed
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False

# Timer pour le spawn des heads
last_spawn_time = pygame.time.get_ticks()
spawn_delay = 1000

# Boucle principale
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # Gestion des bonus
    if current_time - heart_spawn_time > random.randint(10000, 30000):
        bonuses.append([random.randint(0, screen_width - 40), -40, 0, current_time])
        heart_spawn_time = current_time
        
    if current_time - snow_spawn_time > random.randint(5000, 15000):
        bonuses.append([random.randint(0, screen_width - 40), -40, 1, current_time])
        snow_spawn_time = current_time
        
    if current_time - laser_spawn_time > random.randint(8000, 45000):
        bonuses.append([random.randint(0, screen_width - 40), -40, 2, current_time])
        laser_spawn_time = current_time
    
    # Vérification de la fin des effets des bonus
    if snow_active and current_time > snow_end_time:
        snow_active = False
        speed = base_speed + player_speed_bonus
        head_speed = 0.3
        head_speed_fast = 0.5
        
    if laser_active and current_time > laser_end_time:
        laser_active = False
    
    # Gestion du spawn des ennemis
    spawn_delay = 10000 if boss_active else max(100, 1000 - (spawn_speed_bonus * 300))
    
    if current_time - last_spawn_time > spawn_delay and not boss_active:
        # 30% de chance d'avoir un head avec défense, 20% pour un head rapide
        rand = random.random()
        if rand < 0.3:
            head_type = 1  # défense
            health = 3
        elif rand < 0.5:
            head_type = 2  # rapide
            health = 1
        else:
            head_type = 0  # normal
            health = 1
        heads.append([random.randint(0, screen_width - 80), -80, head_type, health])
        last_spawn_time = current_time

    # Gestion des tirs du boss et de son mouvement
    if boss_active:
        # Mouvement horizontal
        boss_x += boss_speed * boss_direction
        if boss_x <= 0 or boss_x >= screen_width - 240:
            boss_direction *= -1
            
        # Mouvement vertical (suivre le joueur)
        if boss_y < boss_max_y:
            boss_y += boss_vertical_speed
            
        # Tir
        if current_time - boss_last_shot > boss_shot_delay:
            # Calculer la direction vers le joueur
            dx = spaceship_x - boss_x
            dy = spaceship_y - boss_y
            angle = math.atan2(dy, dx)
            
            # Créer le projectile avec une direction
            boss_projectiles.append([
                boss_x + 120 - 20,
                boss_y + 240,
                math.cos(angle) * projectile_speed,
                math.sin(angle) * projectile_speed
            ])
            boss_last_shot = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spaceship_x = initial_x
                spaceship_y = initial_y
            # Code GOD
            if event.key in [pygame.K_g, pygame.K_o, pygame.K_d]:
                god_code += event.unicode.upper()
                if len(god_code) > 3:
                    god_code = god_code[1:]
                if god_code == "GOD":
                    god_mode = True
                    player_lives = float('inf')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if laser_active:
                    projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35, 0])  # Tir droit
                    projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35, -0.5])  # Tir gauche
                    projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35, 0.5])  # Tir droit
                else:
                    projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35, 0])

    keys = pygame.key.get_pressed()
    current_speed = speed * (0.5 if snow_active else 1)
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and spaceship_x > 0:
        spaceship_x -= current_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and spaceship_x < screen_width - new_width:
        spaceship_x += current_speed
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and spaceship_y > 0:
        spaceship_y -= current_speed
    if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and spaceship_y < screen_height - new_height:
        spaceship_y += current_speed

    # Gestion des bonus
    for bonus in bonuses[:]:
        bonus[1] += bonus_speed
        if bonus[1] > screen_height:
            bonuses.remove(bonus)
            continue
            
        bonus_rect = pygame.Rect(bonus[0], bonus[1], 40, 40)
        spaceship_rect = pygame.Rect(spaceship_x, spaceship_y, new_width, new_height)
        
        if bonus_rect.colliderect(spaceship_rect):
            if bonus[2] == 0:  # Coeur
                if player_lives < 3:
                    player_lives += 1
            elif bonus[2] == 1:  # Neige
                snow_active = True
                snow_end_time = current_time + 5000
            elif bonus[2] == 2:  # Laser
                laser_active = True
                laser_end_time = current_time + 8000
            bonuses.remove(bonus)

    # Gestion des projectiles du joueur
    for projectile in projectiles[:]:
        projectile[1] -= projectile_speed
        if len(projectile) > 2:  # Si le projectile a une direction horizontale
            projectile[0] += projectile_speed * projectile[2]
        if projectile[1] < -50 or projectile[0] < -50 or projectile[0] > screen_width:
            projectiles.remove(projectile)
            continue
        
        # Collision avec le boss
        if boss_active:
            boss_rect = pygame.Rect(boss_x, boss_y, 240, 240)
            projectile_rect = pygame.Rect(projectile[0], projectile[1], 40, 50)
            if projectile_rect.colliderect(boss_rect):
                boss_health -= 1
                if boss_health <= 0:
                    boss_active = False
                    score += 5000
                    level += 1
                    spawn_speed_bonus += 0.3
                    mob_speed_bonus += 0.1
                    player_speed_bonus += 0.2
                    speed = base_speed + player_speed_bonus
                    boss_health = int(50 * (1.5 ** (level - 1)))
                    enemies_killed = 0
                    current_background = backgrounds[level % len(backgrounds)]
                projectiles.remove(projectile)
                continue
        
        # Collision avec les ennemis normaux
        projectile_rect = pygame.Rect(projectile[0], projectile[1], 40, 50)
        for head in heads[:]:
            head_rect = pygame.Rect(head[0], head[1], 80, 80)
            if projectile_rect.colliderect(head_rect):
                head[3] -= 1  # Réduit la santé
                if head[3] <= 0:
                    explosions.append([head[0], head[1], current_time])
                    heads.remove(head)
                    enemies_killed += 1
                    if head[2] == 1:
                        score += 500  # 500 points pour head défense
                    elif head[2] == 2:
                        score += 200  # 200 points pour head rapide
                    else:
                        score += 100  # 100 points pour head normal
                projectiles.remove(projectile)
                break

    # Gestion des projectiles du boss
    for projectile in boss_projectiles[:]:
        if len(projectile) == 4:  # Nouveau format avec direction
            projectile[0] += projectile[2]  # Déplacement X
            projectile[1] += projectile[3]  # Déplacement Y
        else:  # Ancien format (vers le bas)
            projectile[1] += projectile_speed
            
        if (projectile[1] > screen_height or projectile[1] < 0 or 
            projectile[0] > screen_width or projectile[0] < 0):
            boss_projectiles.remove(projectile)
            continue
        
        projectile_rect = pygame.Rect(projectile[0], projectile[1], 40, 50)
        spaceship_rect = pygame.Rect(spaceship_x, spaceship_y, new_width, new_height)
        if projectile_rect.colliderect(spaceship_rect):
            boss_projectiles.remove(projectile)
            if not god_mode:
                player_lives -= 1
                if player_lives <= 0:
                    if show_game_over_screen():
                        player_lives = 3
                        score = 0
                        heads.clear()
                        projectiles.clear()
                        explosions.clear()
                        boss_projectiles.clear()
                        bonuses.clear()
                        spaceship_x = initial_x
                        spaceship_y = initial_y
                        boss_active = False
                        enemies_killed = 0
                        boss_health = 50
                        god_mode = False
                        level = 1
                        current_background = backgrounds[0]
                        spawn_speed_bonus = 0
                        mob_speed_bonus = 0
                        player_speed_bonus = 0
                        speed = base_speed
                        snow_active = False
                        laser_active = False
                    else:
                        running = False

    # Activation du boss
    if enemies_killed >= 30 and not boss_active:
        boss_active = True
        heads.clear()
        boss_x = (screen_width - 240) // 2
        boss_y = 50
    
    for head in heads[:]:
        # Utilise la vitesse rapide pour le type 2 (speed)
        current_head_speed = ((head_speed_fast if head[2] == 2 else head_speed) + mob_speed_bonus) * (0.5 if snow_active else 1)
        head[1] += current_head_speed
        if head[1] > screen_height:
            heads.remove(head)
            if not god_mode:
                player_lives -= 1
                if player_lives <= 0:
                    if show_game_over_screen():
                        player_lives = 3
                        score = 0
                        heads.clear()
                        projectiles.clear()
                        explosions.clear()
                        boss_projectiles.clear()
                        bonuses.clear()
                        spaceship_x = initial_x
                        spaceship_y = initial_y
                        boss_active = False
                        enemies_killed = 0
                        boss_health = 50
                        god_mode = False
                        level = 1
                        current_background = backgrounds[0]
                        spawn_speed_bonus = 0
                        mob_speed_bonus = 0
                        player_speed_bonus = 0
                        speed = base_speed
                        snow_active = False
                        laser_active = False
                    else:
                        running = False

    for explosion in explosions[:]:
        if current_time - explosion[2] > 2000:
            explosions.remove(explosion)

    screen.blit(current_background, (0, 0))
    screen.blit(spaceship_image, (spaceship_x, spaceship_y))

    # Affichage du boss et de sa barre de vie
    if boss_active:
        screen.blit(boss_image, (boss_x, boss_y))
        pygame.draw.rect(screen, (255, 0, 0), (50, 20, 700, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, (boss_health/(50 * (1.5 ** (level - 1))))*700, 20))
        
        for projectile in boss_projectiles:
            screen.blit(boom_image, (projectile[0], projectile[1]))
    
    # Message d'avertissement pour l'arrivée du boss
    if enemies_killed >= 21 and enemies_killed < 30 and not boss_active:
        warning_text = font.render(f"Boss dans {30 - enemies_killed} ennemis!", True, (255, 0, 0))
        screen.blit(warning_text, (screen_width//2 - warning_text.get_width()//2, 20))

    # Affichage des bonus actifs et leurs timers
    if snow_active:
        remaining_time = (snow_end_time - current_time) // 1000
        timer_text = small_font.render(f"Neige: {remaining_time}s", True, (255, 255, 255))
        screen.blit(snow_image, (10, 10))
        screen.blit(timer_text, (60, 20))
        
    if laser_active:
        remaining_time = (laser_end_time - current_time) // 1000
        timer_text = small_font.render(f"Laser: {remaining_time}s", True, (255, 255, 255))
        screen.blit(laser_image, (10, 60))
        screen.blit(timer_text, (60, 70))

    for projectile in projectiles:
        screen.blit(boom_image, (projectile[0], projectile[1]))

    for head in heads:
        if head[2] == 1:  # Head avec défense
            screen.blit(head_def_image, (head[0], head[1]))
        elif head[2] == 2:  # Head rapide
            screen.blit(head_speed_image, (head[0], head[1]))
        else:  # Head normal
            screen.blit(head_image, (head[0], head[1]))

    for explosion in explosions:
        screen.blit(explosion_image, (explosion[0], explosion[1]))

    for bonus in bonuses:
        if bonus[2] == 0:  # Coeur
            screen.blit(heart_image, (bonus[0], bonus[1]))
        elif bonus[2] == 1:  # Neige
            screen.blit(snow_image, (bonus[0], bonus[1]))
        elif bonus[2] == 2:  # Laser
            screen.blit(laser_image, (bonus[0], bonus[1]))

    # Afficher les coeurs
    for i in range(3):
        heart_x = screen_width - 40 * (3-i)
        heart_y = screen_height - 40
        if god_mode or i < player_lives:
            screen.blit(heart_image, (heart_x, heart_y))
        else:
            screen.blit(heart_off_image, (heart_x, heart_y))

    # Afficher le score, le mode GOD et le niveau
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Niveau: {level}", True, (255, 255, 255))
    screen.blit(score_text, (10, screen_height - 40))
    screen.blit(level_text, (10, screen_height - 80))
    if god_mode:
        god_text = font.render("MODE GOD ACTIVÉ", True, (255, 215, 0))
        screen.blit(god_text, (screen_width//2 - god_text.get_width()//2, screen_height - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
