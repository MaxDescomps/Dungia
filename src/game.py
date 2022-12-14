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
        direction = None

        if pressed[pygame.K_z]:
            self.player.move_up()
            direction = "up"
        if pressed[pygame.K_s]:
            self.player.move_down()
            direction = "down"
        if pressed[pygame.K_q]:
            self.player.move_left()
            direction = "left"
        if pressed[pygame.K_d]:
            self.player.move_right()
            direction = "right"
        
        if direction:
            self.player.change_animation(direction)

    def update(self):
        self.map_manager.update() #update de tous les sprites et collisions

    def debug(self):

        #affiche la zone de collision du joueur en ajustant selon le zoom et le centrage
        pygame.draw.rect(self.screen, (255,0,0),
        (self.player.feet.x*self.map_manager.zoom - self.map_manager.get_group()._map_layer.view_rect.x*self.map_manager.zoom,
         self.player.feet.y*self.map_manager.zoom- self.map_manager.get_group()._map_layer.view_rect.y*self.map_manager.zoom,
         self.player.feet.width*self.map_manager.zoom, self.player.feet.height*self.map_manager.zoom), 1)

    def run(self):

        clock = pygame.time.Clock() #pour limiter les fps

        # boucle de jeu
        running = True

        while running:

            self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir move_back
            self.handle_input() #gestion entree clavier
            self.update()
            self.map_manager.draw() #dessine et centre le monde
            self.debug() #affichage de la collision du joueur

            pygame.display.flip() # rafraichit l'affichage

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            clock.tick(60) #60 fps

        pygame.quit()