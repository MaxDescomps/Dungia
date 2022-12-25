import pygame, pytmx, pyscroll
from player import *
from map import MapManager
from dialog import DialogBox

class Game:

    def __init__(self):
        # fenetre de jeu
        self.screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
        pygame.display.set_caption("esieageon")

        #generer un joueur
        self.player = Player() #création joueur
        self.map_manager = MapManager(self.screen, self.player)

        self.dialog_box = DialogBox(400, 100)

        #donne les informations au joueur pour gere la position du crosshair en jeu
        self.player.map_manager = self.map_manager

        self.running = True

    def handle_real_time_input(self):
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

    def handle_input(self):
        for event in pygame.event.get():

            #évènement souris click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # print("left mouse button")
                    shot = self.player.shoot()
                    self.map_manager.get_shots().append(shot)
                    self.map_manager.get_group().add(shot)

                elif event.button == 3:
                    # print("right mouse button")
                    pass
                elif event.button == 4:
                    # print("mouse wheel up")
                    pass
                elif event.button == 5:
                    # print("mouse wheel down")
                    pass
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.map_manager.check_npc_collisions(self.dialog_box)
            
            #évènement souris fin de click
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # print("left mouse button end")
                    pass
                elif event.button == 3:
                    # print("right mouse button end")
                    pass

            #fermeture fenetre de jeu
            elif event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.map_manager.update() #update de tous les sprites et collisions
        self.player.crosshair.update()

    def draw(self):
        self.map_manager.draw() #dessine et centre le monde
        self.screen.blit(self.player.crosshair.image, self.player.crosshair.rect.topleft) #affichage du crosshair
        self.dialog_box.render(self.screen)

    def debug(self):

        #bug si resize
        #affiche la zone de collision du joueur en ajustant selon le zoom et le centrage
        pygame.draw.rect(self.screen, (255,0,0),
        (self.player.feet.x*self.map_manager.zoom - self.map_manager.get_group()._map_layer.view_rect.x*self.map_manager.zoom,
         self.player.feet.y*self.map_manager.zoom - self.map_manager.get_group()._map_layer.view_rect.y*self.map_manager.zoom,
         self.player.feet.width*self.map_manager.zoom, self.player.feet.height*self.map_manager.zoom), 1)

    def run(self):

        clock = pygame.time.Clock() #pour limiter les fps

        # boucle de jeu
        while self.running:

            self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.handle_real_time_input() #gestion entree clavier
            self.handle_input()
            self.update()

            self.draw()

            pygame.display.flip() # rafraichit l'affichage


            clock.tick(60) #60 fps

        pygame.quit()