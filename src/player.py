import pygame
from animation import AnimateSprite
from crosshair import Crosshair
from shot import *

class Entity(AnimateSprite):

    def __init__(self, name, x, y):
        super().__init__(name)
        self.image = self.get_image(0, 0)#sprite effectif de l'entité
        self.rect = self.image.get_rect() #rectangle de l'image de l'entité
        self.position = [x, y]
        self.feet = pygame.Rect(0, 0, 28, 12) #zone de collision de l'entité
        self.old_position = self.position.copy()

    def save_location(self): self.old_position = self.position.copy()

    def move_left(self): self.position[0] -= self.speed

    def move_right(self): self.position[0] += self.speed

    def move_up(self): self.position[1] -= self.speed

    def move_down(self): self.position[1] += self.speed
    
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
        self.max_pdv = 6 #pdv maximums
        self.pdv = self.max_pdv #pdv effectifs
        self.damage_clock = 0 #laps de temps minimum entre deux dommages consécutifs

        self.crosshair = Crosshair("../image/crosshair.png")
        self.map_manager = None #gestionnaire de carte pour ajuster la position du crosshair en jeu, attribué dans Game.__init__()

    def shoot(self):
        return PlayerShot(self, 3, "techpack/Projectiles/projectiles x1", 1)

    def update(self):
        if self.pdv:
            self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

            if self.damage_clock:
                self.damage_clock -= 1
        else:
            exit(0) #game over

class NPC(Entity):

    def __init__(self, name, dialog):
        super().__init__(name, 0, 0)
        self.name = name
        self.dialog = dialog

    def teleport_spawn(self, map):
        point = map.tmx_data.get_object_by_name(self.name) #l'objet du tmx sur lequel on se teleporte
        self.position = [point.x, point.y]
        self.save_location() #permet de ne pas se tp en boucle sur une collision?

class Mob(Entity):
    """Classe des monstres
    ?utilisation future: on init les mobs qu'on range dans les pièces de la map (pas de max, ils spawn par vagues de 5)
    on invoque les mobs d'une pièce quand on colliderect un pièce mais pas la porte (fermeture de la porte)
    pour les invoquer on les fait spawn avec teleport_spawn en donnant le nom du spawn (spawn_mob[1-5] dans chaque pièce hostile)
    """
    def __init__(self, name, fighting_mobs, player, speed):
        super().__init__(name, 0, 0)
        self.speed = speed
        self.player = player #joueur à attaquer
        self.max_pdv = 6 #pdv maximums
        self.pdv = self.max_pdv #pdv effectifs
        self.name = name #nom du fichier image png
        self.fighting_mobs = fighting_mobs #liste des mobs combattans actuellement dans la même pièce de la carte
    
    def teleport_spawn(self, point):
        self.position = [point[0], point[1]]
        self.save_location() #permet de ne pas se tp en boucle sur une collision?
    
    def update(self):
        if self.pdv:
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce
        
    def move_towards_player(self):
        if(self.position[0] < self.player.position[0]):
            self.position[0] += self.speed
        elif(self.position[0] > self.player.position[0]):
            self.position[0] -= self.speed
        
        if(self.position[1] < self.player.position[1]):
            self.position[1] += self.speed
        elif(self.position[1] > self.player.position[1]):
            self.position[1] -= self.speed