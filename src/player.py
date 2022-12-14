import pygame
from animation import AnimateSprite

class Entity(AnimateSprite):

    def __init__(self, name, x, y):
        super().__init__(name)
        self.image = self.get_image(0, 0) #sprite effectif du joueur
        self.image.set_colorkey([0,0,0]) #enleve le noir (rgb 0,0,0) de l'image
        self.rect = self.image.get_rect() #rectangle de l'image du joueur
        self.position = [x, y]
        self.speed = 2
        self.feet = pygame.Rect(0, 0, 28, 12) #zone de collision du joueur
        self.old_position = self.position.copy()

    def save_location(self): self.old_position = self.position.copy()

    def move_left(self): self.position[0] -= self.speed

    def move_right(self): self.position[0] += self.speed

    def move_up(self): self.position[1] -= self.speed

    def move_down(self): self.position[1] += self.speed

    def change_animation(self, direction):
        self.image = self.images[direction]
        self.image.set_colorkey([0,0,0]) #enleve le noir (rgb 0,0,0) de l'image
    
    def update(self):
        self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

    def move_back(self):#remplacer par une vérif de collision avant de bouger?
        self.position = self.old_position
        #remplacer en bas par update?
        self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

class Player(Entity):

    def __init__(self):
        super().__init__("player", 0, 0)

class NPC(Entity):

    def __init__(self, name):
        super().__init__(name, 0, 0)
        self.name = name

    def teleport_spawn(self, map):
        point = map.tmx_data.get_object_by_name(self.name) #l'objet du tmx sur lequel on se teleporte
        self.position = [point.x, point.y]
        self.save_location() #permet de ne pas se tp en boucle sur une collision?
