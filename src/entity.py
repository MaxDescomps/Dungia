import pygame, copy
from animation import AnimateSprite
from crosshair import Crosshair
from shot import *
from weapon import *

class Entity(AnimateSprite):

    def __init__(self, name, x, y):
        super().__init__(name)

        self.image = self.get_image(self.sprite_sheet, 0, 0).convert_alpha() #sprite effectif de l'entité
        self.rect = self.image.get_rect() #rectangle de l'image de l'entité
        self.position = [x, y]
        self.feet = pygame.Rect(0, 0, 22, 12) #zone de collision de l'entité avec des obstacles
        self.collision = self.feet #zone de collision de l'entité avec des projectiles (parfois différente)
        self.old_position = self.position.copy()

    def save_location(self): self.old_position = self.position.copy()

    def move_left(self): self.position[0] -= self.speed

    def move_right(self): self.position[0] += self.speed

    def move_up(self): self.position[1] -= self.speed

    def move_down(self): self.position[1] += self.speed
    
    def update(self):
        self.rect.topleft = self.position #la position de l'entité avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect entity.feet et entity.rect

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position #la position de l'entité avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect entity.feet et entity.rect