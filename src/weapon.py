import pygame, math, copy
from shot import *
import random

class Weapon(pygame.sprite.Sprite):
    """Classe des armes du jeu"""

    def __init__(self, max_rate_clock:int, damage:float, bullet_speed:float, name:str):
        """
        Constructeur de la classe Weapon

        Args:
            max_rate_clock(int): le nombre de frame entre deux tirs
            damage(float): les dégats des tirs
            bullet_speed(float): la vitesse des balles de l'arme
            name(str): le nom de l'arme
        """

        super().__init__()

        self.bullet_speed = bullet_speed
        self.max_rate_clock = max_rate_clock
        self.damage = damage
        self.name = name
        self.first_image = pygame.image.load(f"../image/guns/{name}_1.png").convert_alpha() #l'image initiale de l'arme, sur laquelle on applique la rotation
        self.image = copy.copy(self.first_image) #l'image de l'arme après rotation
        self.rect = self.image.get_rect() #le rectangle d'affichage de l'arme

    def shoot(self, angle_modif:float=0) -> list[Shot]:
        """
        Tir de l'arme

        Args:
            angle_modif(float): modificateur de l'angle du tir

        Returns:
            shot(list[Shot]): les tirs
        """

        return [Shot(self.rect.center, self.bullet_speed, self.damage, self.angle + angle_modif, self.name, oriented=True)]

    def rotate_img(self):
        """fait une rotation d'une image en fonction de son angle"""

        if (self.angle > math.pi / 2) or (self.angle < -math.pi / 2):
            rotated_image = pygame.transform.rotate(self.first_image, math.degrees(self.angle)).convert_alpha() #rotation de l'image
        else:
            rotated_image = pygame.transform.rotate(self.first_image, -math.degrees(self.angle)).convert_alpha() #rotation de l'image

        self.rect = rotated_image.get_rect(center = self.rect.center) #on corrige la modification du centre de l'image causé par le changement de son rectangle après rotation

        self.image = rotated_image

class Remington(Weapon):
    """Classe spécialisée d'arme"""

    def __init__(self, max_rate_clock, damage, bullet_speed, name, angle_modif):
        """
        Constructeur de la classe Remington

        Args:
            max_rate_clock(int): le nombre de frame entre deux tirs
            damage(float): les dégats des tirs
            bullet_speed(float): la vitesse des balles de l'arme
            name(str): le nom de l'arme
        """

        super().__init__(max_rate_clock, damage, bullet_speed, name)
        self.angle_modif = angle_modif

    def shoot(self) -> list[Shot]:
        """
        Tir de l'arme

        Returns:
            shots(list[Shot]): les tirs
        """
        
        shots = []

        for i in range(5):
            shots.append(Shot(self.rect.center, self.bullet_speed, self.damage, self.angle + random.uniform(-self.angle_modif, self.angle_modif), self.name, oriented=True))

        return shots

class KSG(Weapon):
    """Classe spécialisée d'arme"""

    def __init__(self, max_rate_clock, damage, bullet_speed, name):
        """
        Constructeur de la classe KSG

        Args:
            max_rate_clock(int): le nombre de frame entre deux tirs
            damage(float): les dégats des tirs
            bullet_speed(float): la vitesse des balles de l'arme
            name(str): le nom de l'arme
        """

        super().__init__(max_rate_clock, damage, bullet_speed, name)

    def shoot(self) -> list[Shot]:
        """
        Tir de l'arme

        Returns:
            shots(list[Shot]): les tirs
        """

        return [
        Shot(self.rect.center, self.bullet_speed, self.damage, self.angle, self.name, oriented=True),
        Shot(self.rect.center, self.bullet_speed, self.damage, self.angle + 0.2, self.name, oriented=True),
        Shot(self.rect.center, self.bullet_speed, self.damage, self.angle - 0.2, self.name, oriented=True)
        ]

class PPBizon(Weapon):
    """Classe spécialisée d'arme"""

    def __init__(self, max_rate_clock, damage, bullet_speed, name):
        """
        Constructeur de la classe PPBizon

        Args:
            max_rate_clock(int): le nombre de frame entre deux tirs
            damage(float): les dégats des tirs
            bullet_speed(float): la vitesse des balles de l'arme
            name(str): le nom de l'arme
        """

        super().__init__(max_rate_clock, damage, bullet_speed, name)

    def shoot(self) -> list[Shot]:
        """
        Tir de l'arme

        Returns:
            shots(list[Shot]): les tirs
        """

        return [
        Shot(self.rect.center, self.bullet_speed, self.damage, self.angle + random.uniform(-0.2, 0.2), self.name, oriented=True)
        ]
    
class Gun(Weapon):
    """Classe spécialisée d'arme"""

    def __init__(self, max_rate_clock, damage, bullet_speed, name):
        """
        Constructeur de la classe Gun

        Args:
            max_rate_clock(int): le nombre de frame entre deux tirs
            damage(float): les dégats des tirs
            bullet_speed(float): la vitesse des balles de l'arme
            name(str): le nom de l'arme
        """

        super().__init__(max_rate_clock, damage, bullet_speed, name)

    def shoot(self) -> list[Shot]:
        """
        Tir de l'arme

        Returns:
            shots(list[Shot]): les tirs
        """

        return [
        Shot(self.rect.center, self.bullet_speed, self.damage, self.angle + random.uniform(-0.1, 0.1), self.name, oriented=True)
        ]

weapons = dict() #liste des armes

def list_weapons():
    """Remplit la liste des armes"""

    global weapons
    weapons["ak-47"] = Weapon(9, 1, 4, "1")
    weapons["ksg"] = KSG(25, 1, 4, "2")
    weapons["remington"] = Remington(30, 1, 3, "3", 0.3)
    weapons["pp-bizon"] = PPBizon(6, 1, 3, "4")
    weapons["rocket-launcher"] = Weapon(40, 5, 3, "5")
    weapons["sniper"] = Weapon(80, 10, 6, "6")
    weapons["shadow"] = Weapon(20, 1, 3, "7")
    weapons["x-tech"] = Weapon(20, 1, 3, "8")
    weapons["ray-gun"] = Weapon(20, 1, 3, "9")
    weapons["atomus"] = Weapon(4, 0.5, 3, "10")
    # weapons["atomus"] = Weapon(4, 10, 10, "10")
    weapons["gun"] = Gun(16, 2, 3, "11")