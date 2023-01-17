import pygame
from game import *
import network
import server_coop2
import threading
from weapon import list_weapons

class Character():
    """Classe du personnage du menu de démarrage"""

    def __init__(self, name: str):
        """
        Constructeur de la classe Character
        
        Args:
            name(str): nom du fichier contenant les sprites du personnage
        """

        self.sheet = pygame.image.load(f'../image/{name}.png').convert_alpha()

    def get_image(self, player_frame: int, width: float, height: float, row: float, scale: float) -> pygame.Surface:
        """
        Récupère une des images du personnage du menu de démarrage
        
        Args:
            player_frame(int): numéro du sprite sur la ligne en partant de la gauche
            width(float): largeur du sprite
            height(float): hauteur du sprite
            row(float): coordonnées de la ligne contenant le sprite
            scale(float): multiplicateur de la taille du sprite
        """

        image = pygame.Surface([width, height], pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((player_frame * width), row, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))

        return image

    def get_images(self, animation_steps: int, width: float, height: float, row: float, scale: float) -> list[pygame.Surface]:
        """
        Récupère les images du personnage du menu de démarrage
        
        Args:
            animation_steps(int): nombre de sprites à récupérer
            width(float): largeur des sprites
            height(float): hauteur des sprites
            row(float): coordonnées de la ligne contenant les sprites
            scale(float): multiplicateur de la taille des sprites
        """

        player_images = []

        for animation_step in range(animation_steps):
            player_images.append(self.get_image(animation_step, width, height, row, scale))

        return player_images

class Menu():
    """Classe du menu de démarrage"""

    def __init__(self):
        """Constructeur de la classe du menu de démarrage"""

        #limite d'images par seconde
        self.clock = pygame.time.Clock()
        self.FPS = 50

        # fenêtre de jeu
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("DUNGIA")

        #initialise le catalogue des armes après la fenetre de jeu
        list_weapons()

        #multi
        server_coop2.define_players()

        #personnage annimé
        self.player_height = 32 #hauteur du sprite du personnage
        self.player_width = 32 #largeur du sprite du personnage
        self.player_scale = 7 / (1920/self.SCREEN_WIDTH) #multiplicateur du sprite du personnage
        self.player = Character("player")
        self.animation_steps = 3 #nombre d'animations du personnage
        self.player_images = self.player.get_images(self.animation_steps, self.player_width, self.player_height, 64, self.player_scale)
        self.player_animation_cooldown = 120 #décompte avant animation du personnage

        #décor
        self.grass_height = 10 #taille de l'herbe
        self.get_ground_image()
        self.get_bg_image()

        #texte
        self.font_size = int(40 / (800/self.SCREEN_WIDTH)) #taille
        self.font = pygame.font.SysFont("arialblack", self.font_size) #police
        self.TEXT_COL = (255, 255, 255) #couleur

    def get_ground_image(self):
        """Image du sol du menu"""

        self.ground_image = pygame.image.load(f"../image/paralax/ground.png").convert_alpha()
        self.ground_image = pygame.transform.scale(self.ground_image, (self.SCREEN_WIDTH/2.5, self.SCREEN_HEIGHT/8))
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

    def get_bg_image(self):
        """Image des arbres du menu"""

        self.bg_images = []
        for i in range(1, 6):
            bg_image = pygame.image.load(f"../image/paralax/plx-{i}.png").convert_alpha()
            bg_image = pygame.transform.scale(bg_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT - self.ground_height + self.grass_height))
            self.bg_images.append(bg_image)
            self.bg_height = bg_image.get_height()

        self.bg_width = self.bg_images[0].get_width()

    def play(self):
        """Lance le menu de démarrage"""

        self.scroll = 0 #progression des animations du décor
        last_player_update = pygame.time.get_ticks() #heure de la dernière animation du personnage
        player_frame = 0 #numéro de sprite du personnage affiché

        # musique
        pygame.mixer.music.load("../music/intro.wav")
        pygame.mixer.music.play(-1) #répète la musique à indéfiniment

        running = True

        #boucle principale du menu de démarrage
        while running:

            self.clock.tick(self.FPS) #limite de FPS
            current_time = pygame.time.get_ticks()

            #évolution animation personnage
            if current_time - last_player_update >= self.player_animation_cooldown:
                player_frame += 1
                last_player_update = current_time
                if player_frame >= len(self.player_images):
                    player_frame = 0

            #renouvellement de l'affichage du décor une fois terminé
            if self.scroll > 3000:
                self.scroll = 0
            else:
                self.scroll += 2

            #affichage complet
            self.draw_all(player_frame)
            pygame.display.update()

            #détection d'input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:

                    #lancement du jeu
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.music.stop()

                        game = Game(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                        game.run()

                        #redémarre le menu si on quitte le jeu
                        pygame.mixer.music.load("../music/intro_low.wav")
                        pygame.mixer.music.play(-1)
                        self.scroll = 0

                    elif event.key == pygame.K_h:
                        pygame.mixer.music.stop()
                        
                        self.jeu_hote()

                        #redémarre le menu si on quitte le jeu
                        pygame.mixer.music.load("../music/intro_low.wav")
                        pygame.mixer.music.play(-1)
                        self.scroll = 0
                    
                    elif event.key == pygame.K_c:
                        pygame.mixer.music.stop()

                        self.jeu_cli()

                        #redémarre le menu si on quitte le jeu
                        pygame.mixer.music.load("../music/intro_low.wav")
                        pygame.mixer.music.play(-1)
                        self.scroll = 0
                    
                    #fermeture du menu
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                #fermeture du menu
                elif event.type == pygame.QUIT:
                    running = False

    def jeu_cli(self):
        n = network.Network()

        p = n.get_p()

        game = GameCli(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, p, n)
        game.run()

    def jeu_hote(self):

        th_serv = threading.Thread(target=server_coop2.main)
        # le thread n'est pas deamon pour deconnecter les clients et le socket proprement après fermeture du processus père
        th_serv.start()

        p = server_coop2.players[0]
        p2 = server_coop2.players[1]

        game = GameHost(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, p, p2)
        game.run()

    def draw_all(self, player_frame: int):
        """
        Affichage complet du menu de démarrage
        
        Args:
            player_frame(int): numéro du sprite personnage à afficher
        """

        self.draw_bg()
        self.draw_ground()
        self.draw_character(player_frame)
        self.draw_text("Press Space Button", self.font, self.TEXT_COL, 100, self.font_size)

    def draw_character(self, player_frame: int):
        """
        Affichage du personnage
        
        Args:
            player_frame(int): numéro du sprite personnage à afficher
        """

        self.screen.blit(self.player_images[player_frame], (100, self.SCREEN_HEIGHT - self.ground_height + self.grass_height - self.player_height * self.player_scale))            

    def draw_bg(self):
        """Affiche l'arrière_plan"""

        for x in range(10):
            speed = 1
            for i in self.bg_images:
                self.screen.blit(i, ((x * self.bg_width) - self.scroll * speed, self.SCREEN_HEIGHT - self.ground_height - self.bg_height + self.grass_height))
                speed += 0.2

    def draw_ground(self):
        """Affiche le sol"""

        for x in range(30):
            self.screen.blit(self.ground_image, ((x * self.ground_width) - self.scroll * 2.2, self.SCREEN_HEIGHT - self.ground_height))

    def draw_text(self, text:str, font:pygame.font.Font, text_col:tuple[int,int,int], x:float, y:float):
        """
        Affiche le texte
        
        Args:
            text(str): texte à afficher
            font(pygame.font.Font): police du texte
            text_col(tuple[int,int,int]): couleur du texte
            x(float): coordonnée horizontale du texte
            y(float): coordonnée verticale du texte
        """

        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))