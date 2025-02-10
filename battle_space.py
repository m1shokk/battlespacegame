import pygame
import sys
import random
import time
import json

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
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Charger l'image du personnage
spaceship_image = pygame.image.load("./images/spaceship.png")
boom_image = pygame.image.load("./images/boom.png")
head_image = pygame.image.load("./images/head.png")
head_def_image = pygame.image.load("./images/head_def.png")
head_speed_image = pygame.image.load("./images/head_speed.png")
explosion_image = pygame.image.load("./images/explosion.png")
heart_image = pygame.image.load("./images/coeur.png")
heart_off_image = pygame.image.load("./images/coeur_off.png")

# Redimensionner le personnage à 20 % de sa taille d'origine
original_width, original_height = spaceship_image.get_size()
new_width = int(original_width * 0.2)
new_height = int(original_height * 0.2)
spaceship_image = pygame.transform.scale(spaceship_image, (new_width, new_height))

# Redimensionner le projectile et le head
boom_image = pygame.transform.scale(boom_image, (40, 50))
head_image = pygame.transform.scale(head_image, (80, 80))
head_def_image = pygame.transform.scale(head_def_image, (80, 80))
head_speed_image = pygame.transform.scale(head_speed_image, (80, 80))
explosion_image = pygame.transform.scale(explosion_image, (80, 80))
heart_image = pygame.transform.scale(heart_image, (30, 30))
heart_off_image = pygame.transform.scale(heart_off_image, (30, 30))

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

# Position initiale du personnage
initial_x = (screen_width - new_width) // 2
initial_y = screen_height - new_height - 50
spaceship_x = initial_x
spaceship_y = initial_y

# Liste pour stocker les projectiles, les heads et les explosions
projectiles = []
heads = []  # [x, y, type, health] - type: 0 normal, 1 defense, 2 speed
explosions = []

# Score et meilleur score
score = 0
try:
    with open('highscore.json', 'r') as f:
        high_score = json.load(f)['high_score']
except:
    high_score = 0

# Police pour le texte
font = pygame.font.Font(None, 36)

# Vies du joueur
player_lives = 3

# Vitesse de déplacement du vaisseau
speed = 0.6
projectile_speed = 0.8
head_speed = 0.3
head_speed_fast = 0.5  # Vitesse pour le head rapide

def show_game_over_screen():
    global score, high_score, running, boss_active, enemies_killed, boss_health
    
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
    
    # Gestion du spawn des ennemis
    spawn_delay = 10000 if boss_active else 1000  # 10 secondes si boss actif, 1 seconde sinon
    
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

    # Gestion des tirs du boss
    if boss_active and current_time - boss_last_shot > boss_shot_delay:
        boss_projectiles.append([boss_x + 120 - 20, boss_y + 240])
        boss_last_shot = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spaceship_x = initial_x
                spaceship_y = initial_y
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35])

    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and spaceship_x > 0:
        spaceship_x -= speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and spaceship_x < screen_width - new_width:
        spaceship_x += speed
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and spaceship_y > 0:
        spaceship_y -= speed
    if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and spaceship_y < screen_height - new_height:
        spaceship_y += speed

    # Gestion des projectiles du joueur
    for projectile in projectiles[:]:
        projectile[1] -= projectile_speed
        if projectile[1] < -50:
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
        projectile[1] += projectile_speed
        if projectile[1] > screen_height:
            boss_projectiles.remove(projectile)
            continue
        
        projectile_rect = pygame.Rect(projectile[0], projectile[1], 40, 50)
        spaceship_rect = pygame.Rect(spaceship_x, spaceship_y, new_width, new_height)
        if projectile_rect.colliderect(spaceship_rect):
            boss_projectiles.remove(projectile)
            player_lives -= 1
            if player_lives <= 0:
                if show_game_over_screen():
                    player_lives = 3
                    score = 0
                    heads.clear()
                    projectiles.clear()
                    explosions.clear()
                    boss_projectiles.clear()
                    spaceship_x = initial_x
                    spaceship_y = initial_y
                    boss_active = False
                    enemies_killed = 0
                    boss_health = 50
                else:
                    running = False

    # Activation du boss
    if enemies_killed >= 50 and not boss_active:
        boss_active = True
        boss_health = 50
        heads.clear()
    
    for head in heads[:]:
        # Utilise la vitesse rapide pour le type 2 (speed)
        current_speed = head_speed_fast if head[2] == 2 else head_speed
        head[1] += current_speed
        if head[1] > screen_height:
            heads.remove(head)
            player_lives -= 1
            if player_lives <= 0:
                if show_game_over_screen():
                    player_lives = 3
                    score = 0
                    heads.clear()
                    projectiles.clear()
                    explosions.clear()
                    boss_projectiles.clear()
                    spaceship_x = initial_x
                    spaceship_y = initial_y
                    boss_active = False
                    enemies_killed = 0
                    boss_health = 50
                else:
                    running = False

    for explosion in explosions[:]:
        if current_time - explosion[2] > 2000:
            explosions.remove(explosion)

    screen.blit(background_image, (0, 0))
    screen.blit(spaceship_image, (spaceship_x, spaceship_y))

    # Affichage du boss et de sa barre de vie
    if boss_active:
        screen.blit(boss_image, (boss_x, boss_y))
        pygame.draw.rect(screen, (255, 0, 0), (50, 20, 700, 20))
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, (boss_health/50)*700, 20))
        
        for projectile in boss_projectiles:
            screen.blit(boom_image, (projectile[0], projectile[1]))
    
    # Message d'avertissement pour l'arrivée du boss
    if enemies_killed >= 41 and enemies_killed < 50 and not boss_active:
        warning_text = font.render(f"Boss dans {50 - enemies_killed} ennemis!", True, (255, 0, 0))
        screen.blit(warning_text, (screen_width//2 - warning_text.get_width()//2, 20))

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

    # Afficher les coeurs
    for i in range(3):
        heart_x = screen_width - 40 * (3-i)
        heart_y = screen_height - 40
        if i < player_lives:
            screen.blit(heart_image, (heart_x, heart_y))
        else:
            screen.blit(heart_off_image, (heart_x, heart_y))

    # Afficher le score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, screen_height - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
