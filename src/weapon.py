import pygame, math, copy

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, max_rate_clock, damage, bullet_speed, name):
        super().__init__()

        self.player = player #le joueur qui tient l'arme
        self.bullet_speed = bullet_speed #la vitesse des balles de l'arme
        self.max_rate_clock = max_rate_clock #le nombre de frame entre deux tirs
        self.rate_clock = 0 #le compteur de cadence de tir
        self.damage = damage #les dégats des tirs
        self.name = name #le nom de l'arme
        self.first_image = pygame.image.load(f"../image/guns/{name}.png").convert_alpha() #l'image initiale de l'arme, sur laquelle on applique la rotation
        self.image = copy.copy(self.first_image) #l'image de l'arme après rotation
        self.rect = self.image.get_rect() #le rectangle d'affichage de l'arme
        self.position = self.rect.topleft #la position de l'arme

    def update(self):

        #décrémentation du compteur de cadence de tir
        if self.rate_clock:
            self.rate_clock -= 1

        #position en jeu du crosshair
        mouse_pos = [None, None]
        mouse_pos[0] = self.player.crosshair.rect.center[0] / self.player.map_manager.zoom + self.player.map_manager.get_group().view.x
        mouse_pos[1] = self.player.crosshair.rect.center[1] / self.player.map_manager.zoom + self.player.map_manager.get_group().view.y

        #calcul de l'angle de tir
        player_center = pygame.Vector2(self.player.rect.center)
        self.rect.center = player_center
        distance = mouse_pos - player_center
        self.angle = math.atan2(distance.y, distance.x)

        #coefficients du vecteur de déplacement de l'arme par rapport au joueur
        self.speed_x = math.cos(self.angle)
        self.speed_y = math.sin(self.angle)

        #rotation de l'image de l'arme en fonction de l'angle
        self.rotate_img()

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.pos = [None, None]
        self.pos[0] = self.rect[0]
        self.pos[1] = self.rect[1]

        #met la position du tir à jour
        self.pos[0] += 18 * self.speed_x
        self.pos[1] += 18 * self.speed_y

        #maj du rectangle d'affichage
        self.rect.topleft = self.pos

    def rotate_img(self):
        """fait une rotation d'une image en fonction de son angle"""

        rotated_image = pygame.transform.rotate(self.first_image, -math.degrees(self.angle)).convert_alpha() #rotation de l'image

        self.rect = rotated_image.get_rect(center = self.rect.center) #on corrige la modification du centre de l'image causé par le changement de son rectangle après rotation

        self.image = rotated_image

weapons = dict()

def list_weapons():
    global weapons
    weapons["ak-47"] = Weapon(None, 10, 1, 3, "1_1")
    weapons["sniper"] = Weapon(None, 80, 10, 6, "6_1")