import pygame, math, copy
from shot import *

class Weapon(pygame.sprite.Sprite):
    def __init__(self, max_rate_clock, damage, bullet_speed, name):
        super().__init__()

        self.bullet_speed = bullet_speed #la vitesse des balles de l'arme
        self.max_rate_clock = max_rate_clock #le nombre de frame entre deux tirs
        self.damage = damage #les dégats des tirs
        self.name = name #le nom de l'arme
        self.first_image = pygame.image.load(f"../image/guns/{name}_1.png").convert_alpha() #l'image initiale de l'arme, sur laquelle on applique la rotation
        self.image = copy.copy(self.first_image) #l'image de l'arme après rotation
        self.rect = self.image.get_rect() #le rectangle d'affichage de l'arme

    def shoot(self, owner):
        return [PlayerShot(owner, self.bullet_speed, "techpack/Projectiles/projectiles x1", self.damage, self.name, self.angle)]

    def rotate_img(self):
        """fait une rotation d'une image en fonction de son angle"""

        if (self.angle > math.pi / 2) or (self.angle < -math.pi / 2):
            rotated_image = pygame.transform.rotate(self.first_image, math.degrees(self.angle)).convert_alpha() #rotation de l'image
        else:
            rotated_image = pygame.transform.rotate(self.first_image, -math.degrees(self.angle)).convert_alpha() #rotation de l'image

        self.rect = rotated_image.get_rect(center = self.rect.center) #on corrige la modification du centre de l'image causé par le changement de son rectangle après rotation

        self.image = rotated_image

class Shotgun(Weapon):
    def __init__(self, max_rate_clock, damage, bullet_speed, name):

        super().__init__(max_rate_clock, damage, bullet_speed, name)

    def shoot(self, owner):
        return [
        PlayerShot(owner, self.bullet_speed, "techpack/Projectiles/projectiles x1", self.damage, self.name, self.angle),
        PlayerShot(owner, self.bullet_speed, "techpack/Projectiles/projectiles x1", self.damage, self.name, self.angle - 0.4),
        PlayerShot(owner, self.bullet_speed, "techpack/Projectiles/projectiles x1", self.damage, self.name, self.angle + 0.4)
        ]

weapons = dict()

def list_weapons():
    global weapons
    weapons["ak-47"] = Weapon(10, 1, 3, "1")
    weapons["ksg"] = Weapon(30, 1, 4, "2")
    weapons["remington"] = Shotgun(10, 1, 3, "3")
    weapons["android_remington"] = Shotgun(50, 1, 2, "3")
    weapons["pp-bizon"] = Weapon(10, 1, 3, "4")
    weapons["rocket-launcher"] = Weapon(10, 1, 3, "5")
    weapons["sniper"] = Weapon(80, 10, 6, "6")
    weapons["shadow"] = Weapon(20, 10, 6, "7")
    weapons["x-tech"] = Weapon(20, 10, 6, "8")
    weapons["ray-gun"] = Weapon(20, 10, 6, "9")
    weapons["atomus"] = Weapon(1, 10, 10, "10")