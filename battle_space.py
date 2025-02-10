import pygame
import sys
import random
import time

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
screen_width = 800
screen_height = 600

# Création de la fenêtre
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle Space")

# Charger l'image de fond
background_image = pygame.image.load("./images/fond.jpg")  # Remplacez par le nom de votre fichier image
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Charger l'image du personnage
spaceship_image = pygame.image.load("./images/spaceship.png")  # Remplacez par le nom de votre fichier image
boom_image = pygame.image.load("./images/boom.png")
head_image = pygame.image.load("./images/head.png")
explosion_image = pygame.image.load("./images/explosion.png")
heart_image = pygame.image.load("./images/coeur.png")
heart_off_image = pygame.image.load("./images/coeur_off.png")

# Redimensionner le personnage à 20 % de sa taille d'origine
original_width, original_height = spaceship_image.get_size()
new_width = int(original_width * 0.2)  # 20 % de la largeur
new_height = int(original_height * 0.2)  # 20 % de la hauteur
spaceship_image = pygame.transform.scale(spaceship_image, (new_width, new_height))

# Redimensionner le projectile et le head
boom_image = pygame.transform.scale(boom_image, (40, 50))  # Réduit à 40x50
head_image = pygame.transform.scale(head_image, (80, 80))  # Taille du head augmentée à 80x80
explosion_image = pygame.transform.scale(explosion_image, (80, 80))  # Taille de l'explosion
heart_image = pygame.transform.scale(heart_image, (30, 30))  # Taille des coeurs
heart_off_image = pygame.transform.scale(heart_off_image, (30, 30))

# Position initiale du personnage
initial_x = (screen_width - new_width) // 2  # Position initiale x
initial_y = screen_height - new_height - 50  # Position initiale y plus basse
spaceship_x = initial_x  # Position courante x
spaceship_y = initial_y  # Position courante y

# Liste pour stocker les projectiles, les heads et les explosions
projectiles = []
heads = []
explosions = []  # Liste pour stocker les explosions avec leur temps de création

# Vies du joueur
player_lives = 3

# Vitesse de déplacement du vaisseau (réduite)
speed = 0.6
projectile_speed = 0.8
head_speed = 0.3

# Timer pour le spawn des heads
last_spawn_time = pygame.time.get_ticks()
spawn_delay = 1000  # 1000ms = 1 head par seconde

# Boucle principale
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # Spawn des heads
    if current_time - last_spawn_time > spawn_delay:
        heads.append([random.randint(0, screen_width - 80), -80])  # Position aléatoire en x, ajustée pour la nouvelle taille
        last_spawn_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Fermer la fenêtre
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Retour à la position initiale avec 'espace'
                spaceship_x = initial_x
                spaceship_y = initial_y
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Tirer avec le clic gauche de la souris
            if event.button == 1:  # 1 représente le bouton gauche
                projectiles.append([spaceship_x + new_width//2 - 20, spaceship_y - 35])

    # Gestion des touches pressées
    keys = pygame.key.get_pressed()
    # Mouvement avec les flèches
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and spaceship_x > 0:  # Gauche
        spaceship_x -= speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and spaceship_x < screen_width - new_width:  # Droite
        spaceship_x += speed
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and spaceship_y > 0:  # Haut
        spaceship_y -= speed
    if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and spaceship_y < screen_height - new_height:  # Bas
        spaceship_y += speed

    # Mettre à jour la position des projectiles et vérifier les collisions
    for projectile in projectiles[:]:
        projectile[1] -= projectile_speed
        if projectile[1] < -50:  # Ajusté pour la nouvelle taille du projectile
            projectiles.remove(projectile)
            continue
        
        # Vérifier les collisions avec les heads
        projectile_rect = pygame.Rect(projectile[0], projectile[1], 40, 50)
        for head in heads[:]:
            head_rect = pygame.Rect(head[0], head[1], 80, 80)
            if projectile_rect.colliderect(head_rect):
                # Ajouter une explosion à l'endroit de la collision
                explosions.append([head[0], head[1], current_time])
                heads.remove(head)
                projectiles.remove(projectile)
                break

    # Mettre à jour la position des heads
    for head in heads[:]:
        head[1] += head_speed
        if head[1] > screen_height:
            heads.remove(head)
            player_lives -= 1  # Perd une vie quand un head atteint le bas
            if player_lives <= 0:
                running = False  # Fin du jeu si plus de vies

    # Gérer les explosions
    for explosion in explosions[:]:
        if current_time - explosion[2] > 2000:  # 2000ms = 2 secondes
            explosions.remove(explosion)

    # Afficher l'image de fond
    screen.blit(background_image, (0, 0))

    # Afficher le personnage redimensionné
    screen.blit(spaceship_image, (spaceship_x, spaceship_y))

    # Afficher les projectiles
    for projectile in projectiles:
        screen.blit(boom_image, (projectile[0], projectile[1]))

    # Afficher les heads
    for head in heads:
        screen.blit(head_image, (head[0], head[1]))

    # Afficher les explosions
    for explosion in explosions:
        screen.blit(explosion_image, (explosion[0], explosion[1]))

    # Afficher les coeurs
    for i in range(3):
        heart_x = screen_width - 40 * (3-i)  # Position des coeurs en bas à droite
        heart_y = screen_height - 40
        if i < player_lives:
            screen.blit(heart_image, (heart_x, heart_y))
        else:
            screen.blit(heart_off_image, (heart_x, heart_y))

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
sys.exit()
