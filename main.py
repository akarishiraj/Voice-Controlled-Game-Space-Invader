import pygame
import random
import math
from pygame import mixer

# initialize the pygame
pygame.init()
# create the screen
screen = pygame.display.set_mode((800, 600))  # width , height or x,y axis
# Background
background = pygame.image.load("background.png")
running = True
# Background Sound
# mixer.music.load("background.wav")
# mixer.music.play(-1)

# title and icons
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("periscope.png")
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load("player.png")
playerX = 370
playerY = 480
playerX_change = 0

# enemy
# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6
for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)
# Bullet
bulletImg = pygame.image.load("bullet.png")
bulletX = 0
bulletY = 480  # coordinate of spaceship
bulletX_change = 0
bulletY_change = 10
# ready- you cant see bullet on screen
# fire- bullet is moving
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def player(x, y):
    screen.blit(playerImg, (x, y))  # blit means draw


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))  # blit means draw


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))  # 16 is added so that bullet look at the center of spaceship


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 25:
        return True
    else:
        return False


# game loop
while running:
    # RGB - red, green and blue
    screen.fill((0, 0, 0))
    # background image
    screen.blit(background, (0, 0))
    # playerX += 0.2 # to move right
    # playerX -=0.1  # to move left
    # playerY -= 0.1   # to move up

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # if keystroke is pressed check whether right or left
        if event.type == pygame.KEYDOWN:  # KEYDOWN means any key is pressed
            # print("KEY is pressed")
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bullet_sound = mixer.Sound("laser.wav")
                    bullet_sound.play()
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
        if event.type == pygame.KEYUP:  # when key is released
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0
    playerX += playerX_change
    # creating boundaries
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:  # 800-64 the size of spaceship
        playerX = 736
    for i in range(num_of_enemies):
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break
        enemyX[i] += enemyX_change[i]
        # creating boundaries
        if enemyX[i] <= 0:
            enemyX_change[i] = 4
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -4
            enemyY[i] += enemyY_change[i]

        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            collision_sound = mixer.Sound("explosion.wav")
            collision_sound.play()
            bulletY = 480
            bullet_state = "ready"
            score_value += 1
            print(score_value)
            enemyX[i] = random.randint(0, 735)
            enemyY[i] = random.randint(50, 150)
        enemy(enemyX[i], enemyY[i], i)

    # bullet movement
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"
    if bullet_state is "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)  # remember to call player above screen.fill because player needs to be above on the
    # screen otherwise it
    # will not appear
    show_score(textX, textY)
    pygame.display.update()
