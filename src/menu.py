import pygame
import spritesheet
from player import *
import animation
from game import Game

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
FPS = 60

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Main Menu")

scroll = 0

sprite_sheet_image = pygame.image.load('../image/player.png').convert_alpha()
sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)

# create animation list
animation_list = []
animation_steps = 3
last_update = pygame.time.get_ticks()
animation_cooldown = 150 #vitesse animation personnage
frame = 0
player_height = 32
player_scale = 7 / (1920/SCREEN_WIDTH)
grass_height = 10
font_size = int(40 / (800/SCREEN_WIDTH))

for x in range(animation_steps):
    animation_list.append(sprite_sheet.get_image(x, 32, player_height, player_scale))

# music
pygame.mixer.music.load("../music/intro.wav")
pygame.mixer.music.play()

# image du sol
ground_image = pygame.image.load(f"../image/paralax/ground.png").convert_alpha()
ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH/2.5, SCREEN_HEIGHT/8))
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()

# image des arbres
bg_images = []
for i in range(1, 6):
    bg_image = pygame.image.load(f"../image/paralax/plx-{i}.png").convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT - ground_height + grass_height))
    bg_images.append(bg_image)
    bg_height = bg_image.get_height()

bg_width = bg_images[0].get_width()

def draw_bg():
    for x in range(10):
        speed = 1
        for i in bg_images:
            screen.blit(i, ((x * bg_width) - scroll * speed, SCREEN_HEIGHT - ground_height - bg_height + grass_height))
            speed += 0.2

def draw_ground():
    for x in range(30):
        screen.blit(ground_image, ((x * ground_width) - scroll * 2.2, SCREEN_HEIGHT - ground_height))

# define police
font = pygame.font.SysFont("arialblack", font_size)

# define colors
TEXT_COL = (255, 255, 255)

# define games variables
game_pause = False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col).convert_alpha()
    screen.blit(img, (x, y))

run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_ground()

    current_time = pygame.time.get_ticks()

    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = current_time
        if frame >= len(animation_list):
            frame = 0

    #affichage du personnage
    screen.blit(animation_list[frame], (100, SCREEN_HEIGHT - ground_height + grass_height - player_height * player_scale))

    # get keypressed
    if scroll < 3000:
        scroll += 1

    # check if game is paused
    if game_pause == True:
        draw_text("Test", font, TEXT_COL, 160, 160)
        # display menu
    else:
        draw_text("Press Space Button", font, TEXT_COL, 100, font_size)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_pause=True
                pygame.mixer.music.stop()
                game = Game()
                game.run()
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()