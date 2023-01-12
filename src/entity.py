import pygame
from animation import AnimateSprite
from shot import *
from weapon import *

class Entity(AnimateSprite):
    """Classe des entités (monstres, joueurs, NPC)"""

    def __init__(self, name:str, x:float, y:float):
        """
        Constructeur de la classe Entity
        
        Args:
            name(str): nom du png du spritesheet
            x(float): coordonnée horizontale sur la carte
            y(float): coordonnée verticale sur la carte
        """

        super().__init__(name)

        self.image = self.get_image(self.sprite_sheet, 0, 0).convert_alpha() #sprite effectif de l'entité
        self.rect = self.image.get_rect() #rectangle de l'image de l'entité
        self.position = [x, y] #position sur la carte
        self.feet = pygame.Rect(0, 0, 22, 12) #zone de collision de l'entité avec des obstacles
        self.collision = self.feet #zone de collision de l'entité avec des projectiles (parfois différente)
        self.old_position = self.position.copy()

    def save_location(self):
        """Enregistre la position du joueur"""

        self.old_position = self.position.copy()

    def move_left(self):
        """aller vers la gauche"""

        self.position[0] -= self.speed

    def move_right(self):
        """Aller vers la droite"""

        self.position[0] += self.speed

    def move_up(self):
        """Aller vers le haut"""

        self.position[1] -= self.speed

    def move_down(self):
        """Aller vers le bas"""

        self.position[1] += self.speed
    
    def update(self):
        """Met la position des rectangles du joueur à jour"""

        self.rect.topleft = self.position #la position de l'entité avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect entity.feet et entity.rect

    def move_back(self):
        """Retourne à la position précédente"""

        self.position = self.old_position
        self.rect.topleft = self.position #la position de l'entité avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect entity.feet et entity.rect