import pygame, pytmx, pyscroll
from player import *
from map import MapManager

class Game:
    def __init__(self):
        # fenetre de jeu
        self.screen = pygame.display.set_mode((800,600), pygame.RESIZABLE)
        pygame.display.set_caption("esieageon")

        #generer un joueur
        self.player = Player() #création joueur
        self.map_manager = MapManager(self.screen, self.player)

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_z]:
            self.player.move_up()
        if pressed[pygame.K_s]:
            self.player.move_down()
        if pressed[pygame.K_q]:
            self.player.move_left()
        if pressed[pygame.K_d]:
            self.player.move_right()

    def update(self):
        self.map_manager.update() #update de tous les sprites et collisions


    def run(self):

        clock = pygame.time.Clock() #pour limiter les fps

        # boucle de jeu
        running = True

        while running:

            self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir move_back
            self.handle_input() #gestion entree clavier
            self.update()
            self.map_manager.draw() #dessine et centre le monde

            pygame.display.flip() # rafraichit l'affichage

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clock.tick(60) #60 fps

        pygame.quit()