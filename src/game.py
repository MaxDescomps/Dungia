import pygame
from player import *
from map import *
from dialog import DialogBox
from pause_menu import *
from network import Network
import server_coop2

class Game:
    """Classe du jeu"""

    def __init__(self, screen:pygame.Surface, SCREEN_WIDTH:int, SCREEN_HEIGHT:int):
        """
        Constructeur de la classe Game
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            SCREEN_WIDTH(int): largeur de la fenêtre d'affichage
            SCREEN_HEIGHT(int): hauteur de la fenêtre d'affichage
        """

        self.screen = screen
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.pause_menu = PauseMenu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        #generer un joueur
        self.player = Player() #création joueur
        self.map_manager = MapManager(self.screen, self.player)

        self.dialog_box = DialogBox(400, 100)

        #donne les informations au joueur pour gere l'angle de visée (position du crosshair selon déplacement de la carte)
        self.player.map_manager = self.map_manager

        self.running = True

    def handle_real_time_input(self):
        """Gestion des inputs en 'temps réél' (un appui continuel vaut une série d'appuis)"""

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
        """Gestion des inputs (un appui continuel vaut un appui unique)"""

        for event in pygame.event.get():

            #évènement souris click
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                
                elif event.key == pygame.K_ESCAPE:
                        self.running = self.pause_menu.deploy()

            #fermeture fenetre de jeu
            elif event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Met les sprites et les collisions du jeu à jour"""

        self.map_manager.update() #update de tous les sprites et collisions
        self.player.crosshair.update() #update du sprite du crosshair

    def draw(self):
        """Affiche les sprites du jeu"""

        self.map_manager.draw() #dessine et centre le monde
        self.dialog_box.render(self.screen) #affiche les boites de dialogue ouvertes
        self.player.render_ui(self.screen) #affiche l'interface utilisateur du joueur

    def debug(self):
        """Permet d'afficher plus de détails en jeu comme les zones de collision du joueur"""
        
        #affiche la zone de collision du joueur en ajustant selon le zoom et le centrage
        pygame.draw.rect(self.screen, (255,0,0),
        (self.player.feet.x*self.map_manager.zoom - self.map_manager.get_group().view.x*self.map_manager.zoom,
         self.player.feet.y*self.map_manager.zoom - self.map_manager.get_group().view.y*self.map_manager.zoom,
         self.player.feet.width*self.map_manager.zoom, self.player.feet.height*self.map_manager.zoom), 1)

    def run(self):
        """Démarre le jeu"""

        clock = pygame.time.Clock() #pour limiter les fps
        
        pygame.mixer.music.load("../music/mysterious.wav")
        pygame.mixer.music.play(-1) #répète la musique à indéfiniment

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

class GameCli(Game):
    """Classe de jeu du client en multijoueur"""

    def __init__(self, screen:pygame.Surface, SCREEN_WIDTH:int, SCREEN_HEIGHT:int, position:list[float], network:Network):
        """
        Constructeur de la classe GameCli
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            SCREEN_WIDTH(int): largeur de la fenêtre d'affichage
            SCREEN_HEIGHT(int): hauteur de la fenêtre d'affichage
            position(list[float]): position du client sur le serveur en le rejoignant
            network(Network): réseau du serveur
        """

        self.network = network

        super().__init__(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        #generer un joueur
        self.p2 = PlayerMulti()

        data = self.network.send([self.player.position, self.player.weapon.angle, self.player.shooting, self.player.weapon_index])
        self.p2.position, self.p2.true_angle, self.p2.shooting = data[0], data[1], data[3]

        self.p2.update()

        self.player = Player() #création joueur
        self.player.position = position
        self.map_manager = MapManagerCli(self.screen, self.player, self.p2)

        #donne les informations au joueur pour gere l'angle de visée (position du crosshair selon déplacement de la carte)
        self.player.map_manager = self.map_manager
        self.p2.map_manager = self.map_manager

    def run(self):
        """Démarre le jeu"""

        clock = pygame.time.Clock() #pour limiter les fps
        
        pygame.mixer.music.load("../music/mysterious.wav")
        pygame.mixer.music.play(-1) #répète la musique à indéfiniment

        # boucle de jeu
        while self.player.pdv > 0 and self.running:
            
            #récupération du j2
            self.p2.rect.topleft = self.p2.position #la position du joueur avec [0,0] le coin superieur gauche
            self.p2.feet.midbottom = self.p2.rect.midbottom #aligne les centres des rect player.feet et player.rect

            data = self.network.send([self.player.position, self.player.weapon.angle, self.player.shooting, self.player.weapon_index])

            self.player.shooting = False #assure que l'information d'un tir n'est reçue q'une fois

            self.p2.position, self.p2.true_angle, self.p2.shooting, self.p2.weapon_index, fighting_mob_info = data[0], data[1], data[3], data[4], data[5]

            #efface les anciens mobs combattants
            for mob in self.map_manager.p2_current_room.fighting_mobs:
                if mob.weapon:
                    mob.weapon.kill()

                mob.kill() #retire le sprite des groupes d'affichage
                mob.fighting_mobs.remove(mob) #retire le mob de la liste des mobs combattants de la pièce

            #récupération des mobs du serveur
            for mob_info in fighting_mob_info:
                self.map_manager.add_serv_mob(mob_info)

            #changement d'arme du joueur distant
            if self.p2.weapon is not self.p2.weapons[self.p2.weapon_index]:
                self.p2.weapon.kill() #retire l'ancienne arme des groupes d'affichage
                self.p2.weapon = self.p2.weapons[self.p2.weapon_index]
                self.map_manager.get_group().add(self.p2.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

            #changement de carte
            if self.player.map_manager.current_map != data[2]:
                self.player.map_manager.register_map(data[2])
                self.player.map_manager.current_map = data[2]
                self.map_manager.map_level += 1
                self.map_manager.teleport_player(f"spawn_{self.map_manager.current_map}")
                self.p2.update()

            #si le serveur est connecté
            if self.p2.position:

                self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir revenir en arrière en cas de collision
                self.handle_real_time_input() #gestion input à chaque frame
                self.handle_input() #gestion input à chaque click
                self.update() #met les sprites et les collisions à jour

                self.draw() #modifie l'affichage des sprites du jeu
                self.player.handle_damage() #effet visuel des dégats et gestion du compteur d'invincibilité temporaire
                # self.debug()

                pygame.display.flip() #rafraîchit l'affichage

                clock.tick(60) #60 fps

            else:
                self.running = False

        if self.p2.position:
            self.network.send("".encode("utf-8"))

class GameHost(Game):
    """Classe de jeu du client-serveur (hôte de la partie)"""

    def __init__(self, screen: pygame.Surface, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, player:Player, p2:Player):
        """
        Constructeur de la classe GameHost
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            SCREEN_WIDTH(int): largeur de la fenêtre d'affichage
            SCREEN_HEIGHT(int): hauteur de la fenêtre d'affichage
            player(Player): joueur hôte
            p2(Player): joueur distant
        """

        super().__init__(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        #generer un joueur
        self.p2 = p2
        self.player = player #création joueur
        self.map_manager = MapManagerMulti(self.screen, self.player, self.p2)

        #donne les informations au joueur pour gere l'angle de visée (position du crosshair selon déplacement de la carte)
        self.player.map_manager = self.map_manager
        self.p2.map_manager = self.map_manager


    def run(self):
        """Démarre le jeu"""

        clock = pygame.time.Clock() #pour limiter les fps
        
        pygame.mixer.music.load("../music/mysterious.wav")
        pygame.mixer.music.play(-1) #répète la musique à indéfiniment

        # boucle de jeu
        while self.player.pdv > 0 and self.running:
            self.p2 = server_coop2.players[1]

            self.player.save_location() #enregistre la position du joueur avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.handle_real_time_input() #gestion input à chaque frame
            self.handle_input() #gestion input à chaque click
            self.update() #met les sprites et les collisions à jour

            self.draw() #modifie l'affichage des sprites du jeu
            self.player.handle_damage() #effet visuel des dégats et gestion du compteur d'invincibilité temporaire
            # self.debug()

            pygame.display.flip() #rafraîchit l'affichage

            clock.tick(60) #60 fps

        server_coop2.current_player -= 1
        server_coop2.host_connected = 0