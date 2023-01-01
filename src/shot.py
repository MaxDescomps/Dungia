import pygame, math
from animation import AnimateSprite

def calc_angle(src_pos, dest_pos) -> float:
    """Calcule l'angle entre deux points"""

    distance = dest_pos - src_pos
    
    return math.atan2(distance.y, distance.x)

class Shot(AnimateSprite):
    """Classe d'un tir"""

    def __init__(self, entity, speed, name, damage, angle, weapon_name=0):
        """
        constructeur d'objet Playershot

        Args:
            entity (Entity): l'entité qui tire
            speed (int): la vitesse du tir
            name (str): le chemin du fichier image du tir à partir de ../image
        """
        super().__init__(name)

        self.image = pygame.image.load(f"../image/bullets/{weapon_name}.png").convert_alpha()

        # self.image = self.get_image(self.sprite_sheet, 0, 0) #balles du spritesheet
        self.rect = self.image.get_rect()

        #centre la position de départ du tir sur l'arme du joueur
        if entity.weapon:
            self.rect.center = entity.weapon.rect.center
        else:
            self.rect.center = entity.rect.center

        #calcul de l'angle de tir
        self.angle = angle
        
        #vitesse de déplacement du tir
        self.speed_x = speed * math.cos(self.angle)
        self.speed_y = speed * math.sin(self.angle)

        #rotation de l'image du tir en fonction de l'angle (optionnel si balle circulaire)
        self.rotate_img()

        #calcul du rectangle de collision plus précis
        self.colliderect = pygame.Rect(0, 0, 8, 8)
        self.colliderect.center = self.rect.center

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.pos = [None, None]
        self.pos[0] = self.rect[0]
        self.pos[1] = self.rect[1]

        #dommages infligés par le tir
        self.damage = damage

    def update(self):
        """met la position du tir à jour"""
        
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

        #maj du rectangle d'affichage
        self.rect.topleft = self.pos
        
        #maj du rectangle de collision
        self.colliderect.center = self.rect.center

    def rotate_img(self):
        """fait une rotation de l'image du tir en fonction de son angle"""

        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.angle)).convert_alpha() #rotation de l'image

        self.rect = rotated_image.get_rect(center = self.rect.center) #on corrige la modification du centre de l'image causé par le changement de son rectangle après rotation

        self.image = rotated_image