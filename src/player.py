import pygame, copy
from animation import AnimateSprite
from crosshair import Crosshair
from shot import *
from weapon import weapons

class Entity(AnimateSprite):

    def __init__(self, name, x, y):
        super().__init__(name)

        self.image = self.get_image(self.sprite_sheet, 0, 0).convert_alpha() #sprite effectif de l'entité
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

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
        self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

class Player(Entity):

    def __init__(self):
        super().__init__("player", 0, 0)

        self.ui_sprite_sheet = pygame.image.load(f"../image/techpack/UI/ui x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

        self.max_pdv = 9 #pdv maximums
        self.pdv = self.max_pdv #pdv effectifs
        self.damage_clock = 0 #laps de temps minimum entre deux dommages consécutifs

        self.get_pdv_images()
        self.get_pdv_image()

        self.crosshair = Crosshair("../image/crosshair.png")
        self.map_manager = None #gestionnaire de carte pour ajuster la position du crosshair en jeu, attribué dans Game.__init__()

        self.weapon_index = 0
        self.weapons = []
        self.take_weapon("ak-47")
        self.take_weapon("ksg")
        self.take_weapon("remington")
        self.take_weapon("pp-bizon")
        self.take_weapon("rocket-launcher")
        self.take_weapon("sniper")
        self.take_weapon("shadow")
        self.take_weapon("x-tech")
        self.take_weapon("ray-gun")
        self.take_weapon("atomus")
        self.weapon = self.weapons[self.weapon_index]

    def change_animation_list(self, direction):
        """
        Change la liste de sprites utilisés en fonction de la direction
        """

        self.direction = direction
        self.image = self.images[self.direction][self.animation_index]


    def change_animation(self):
        """
        Change l'animation du sprite avec le mouvement
        """

        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[self.direction]):
                self.animation_index = 0
            
            self.clock = 0

    def take_weapon(self, name):
        """ramassage d'une arme"""

        weapon = copy.copy(weapons[name]) #copie pour ne pas modifier le catalogue d'armes
        weapon.player = self

        self.weapons.append(weapon)

    def next_weapon(self):
        if self.weapon_index < len(weapons) - 1:
            self.weapon_index += 1
        else:
            self.weapon_index = 0

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def previous_weapon(self):
        if self.weapon_index > 0:
            self.weapon_index -= 1
        else:
            self.weapon_index = len(weapons) - 1

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def shoot(self):
        if not self.weapon.rate_clock:
            shot = PlayerShot(self, self.weapon.bullet_speed, "techpack/Projectiles/projectiles x1", self.weapon.damage, self.weapon.name)
            self.map_manager.get_player_shots().append(shot)
            self.map_manager.get_group().add(shot)
            self.weapon.rate_clock = self.weapon.max_rate_clock

    def update(self):
        if self.pdv > 0:
            self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

            if self.damage_clock:
                self.damage_clock -= 1
        else:
            exit(0) #game over

    def render_ui(self, screen):
        screen.blit(self.crosshair.image, self.crosshair.rect.topleft) #affichage du crosshair
        screen.blit(self.pdv_image, (100,20)) #affichage de la bar de vie
    
    def get_pdv_image(self):
        self.pdv_image = self.pdv_images[self.pdv] #image de la bar de vie

    def get_pdv_images(self):
        self.pdv_images = self.get_images(self.ui_sprite_sheet, 0, 1, 10)
        for i in range(len(self.pdv_images)):
            self.pdv_images[i] = pygame.transform.scale(self.pdv_images[i], (200,140)) #agrandit la bar de vie

    def take_damage(self):
        if not self.damage_clock:
            self.damage_clock = 60
            self.pdv -= 1
            self.get_pdv_image()

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
    def __init__(self, name, fighting_mobs, player, speed, damage):
        super().__init__(name, 0, 0)

        self.damage = damage
        self.max_shot_clock = 60
        self.shot_clock = self.max_shot_clock
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
        if self.pdv > 0:
            #tire sur le joueur
            if self.shot_clock > 0:
                self.shot_clock -= 1
            else:
                self.shoot()
                self.shot_clock = self.max_shot_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce
        
    def move_towards_player(self):
        moved = False

        if(self.position[0] - self.player.position[0] < -1):
            self.move_right()
            moved = True
            self.direction = "right"
        elif(self.position[0] - self.player.position[0] > 1):
            self.move_left()
            moved = True
            self.direction = "left"
        
        if(self.position[1] - self.player.position[1] < -1):
            self.move_down()
            moved = True
            self.direction = "down"
        elif(self.position[1] - self.player.position[1] > 1):
            self.move_up()
            moved = True
            self.direction = "up"

        if moved:
            self.change_animation()
        
    def shoot(self):
        shot = MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1)
        self.player.map_manager.get_group().add(shot)
        self.player.map_manager.get_mob_shots().append(shot)