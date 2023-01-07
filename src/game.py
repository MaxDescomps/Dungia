import pygame, pytmx, pyscroll
from player import *
from map import MapManager
from dialog import DialogBox
from weapon import list_weapons

class Game:

    def __init__(self, screen):

        self.screen = screen
        
        #initialise le catalogue des armes après la fenetre de jeu
        list_weapons()

        #generer un joueur
        self.player = Player() #création joueur
        self.map_manager = MapManager(self.screen, self.player)

        self.dialog_box = DialogBox(400, 100)

        #donne les informations au joueur pour gere l'angle de visée (position du crosshair selon déplacement de la carte)
        self.player.map_manager = self.map_manager

        self.running = True

    def handle_real_time_input(self):
        #clavier
        pressed = pygame.key.get_pressed()

        moved = False

        if pressed[pygame.K_z]:
            self.player.move_up()
            self.player.direction = "up"
            moved = True

        if pressed[pygame.K_s]:
            self.player.move_down()
            self.player.direction = "down"
            moved = True

        if pressed[pygame.K_q]:
            self.player.move_left()
            self.player.direction = "left"
            moved = True

        if pressed[pygame.K_d]:
            self.player.move_right()
            self.player.direction = "right"
            moved = True

        if moved:
            self.player.change_animation()

        #souris
        pressed = pygame.mouse.get_pressed()

        if pressed[0]: #mouse left
            self.player.shoot()

    def handle_input(self):
        for event in pygame.event.get():

            #évènement souris click
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if event.button == 1:
                #     pass
                #     # print("left mouse button")
                # elif event.button == 3:
                #     # print("right mouse button")
                #     pass
                if event.button == 4:
                    # print("mouse wheel up")
                    self.player.previous_weapon()
                elif event.button == 5:
                    # print("mouse wheel down")
                    self.player.next_weapon()
            
            #évènement touche clavier pressée
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.map_manager.check_npc_collisions(self.dialog_box)
            
            #évènement souris fin de click
            # elif event.type == pygame.MOUSEBUTTONUP:
            #     if event.button == 1:
            #         # print("left mouse button end")
            #         pass
            #     elif event.button == 3:
            #         # print("right mouse button end")
            #         pass

            #fermeture fenetre de jeu
            elif event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Met les sprites et les collisions à jour"""

        self.map_manager.update() #update de tous les sprites et collisions
        self.player.crosshair.update() #update du sprite du crosshair

    def draw(self):
        self.map_manager.draw() #dessine et centre le monde
        self.dialog_box.render(self.screen) #affiche les boites de dialogue ouvertes
        self.player.render_ui(self.screen) #affiche l'interface utilisateur du joueur

    def debug(self):

        #bug si resize
        #affiche la zone de collision du joueur en ajustant selon le zoom et le centrage
        pygame.draw.rect(self.screen, (255,0,0),
        (self.player.feet.x*self.map_manager.zoom - self.map_manager.get_group().view.x*self.map_manager.zoom,
         self.player.feet.y*self.map_manager.zoom - self.map_manager.get_group().view.y*self.map_manager.zoom,
         self.player.feet.width*self.map_manager.zoom, self.player.feet.height*self.map_manager.zoom), 1)

    def run(self):

        clock = pygame.time.Clock() #pour limiter les fps

        # boucle de jeu
        while self.player.pdv > 0 and self.running:

            self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.handle_real_time_input() #gestion input à chaque frame
            self.handle_input() #gestion input à chaque click
            self.update() #met les sprites et les collisions à jour

            self.draw() #modifie l'affichage des sprites du jeu
            self.player.handle_damage() #effet visuel des dégats et gestion du compteur d'invincibilité temporaire
            # self.debug()

            pygame.display.flip() #rafraîchit l'affichage

            clock.tick(60) #60 fps