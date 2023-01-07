from entity import *
from weapon import *

class Mob(Entity):
    """
    Classe des monstres
    Les monstres apparaissent par vagues de 5 monstres maximum
    """
    def __init__(self, name, fighting_mobs, player, speed, damage):
        super().__init__(name, 0, 0)

        self.damage = damage
        self.weapon = None
        self.max_weapon_rate_clock = 60
        self.weapon_rate_clock = self.max_weapon_rate_clock
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
            if self.weapon_rate_clock > 0:
                self.weapon_rate_clock -= 1
            else:
                self.shoot()
                self.weapon_rate_clock = self.max_weapon_rate_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            if self.weapon:
                self.weapon.kill()

            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce
        
    def move_towards_player(self):
        moved = False

        delta_x = self.position[0] - self.player.position[0]
        delta_y = self.position[1] - self.player.position[1]

        if(delta_x < -1):
            self.move_right()
            moved = True
            self.direction = "right"
        elif(delta_x > 1):
            self.move_left()
            moved = True
            self.direction = "left"
        
        if(delta_y < -1):
            self.move_down()
            moved = True

            if -delta_y > abs(delta_x):
                self.direction = "down"
        elif(delta_y > 1):
            self.move_up()
            moved = True

            if delta_y > abs(delta_x):
                self.direction = "up"

        if moved:
            self.change_animation()
        
    def shoot(self):
        shot = Shot(self, 3, "techpack/Projectiles/projectiles x1", 1, calc_angle(pygame.Vector2(self.rect.center), pygame.Vector2(self.player.feet.center)), oriented=True)
        self.player.map_manager.get_group().add(shot)
        self.player.map_manager.get_mob_shots().append(shot)

class Drone(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("drone", fighting_mobs, player, speed, damage)

        self.feet.width = 15
        self.collision = copy.copy(self.feet)

    def update(self):
        if self.pdv > 0:
            #tire sur le joueur
            if self.weapon_rate_clock > 0:
                self.weapon_rate_clock -= 1
            else:
                self.shoot()
                self.weapon_rate_clock = self.max_weapon_rate_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
            self.collision.midbottom = self.rect.center #aligne les centres des rect mob.feet et mob.rect
        else:
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce
    
    def get_image(self, sprite_sheet, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y et en fait un sprite 48*48"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA).convert_alpha()#surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        image = pygame.transform.scale(image, (48, 48))

        return image

class Android(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("android", fighting_mobs, player, speed, damage)

        self.speed = 0.5
        self.collision = copy.copy(self.feet)
        self.collision.height += 12
        self.weapon = Remington(50, 1, 2, "3", 0.5)
        self.weapon_rate_clock = 0

    def update(self):
        if self.pdv > 0:
            self.manage_weapon()

            #tire sur le joueur
            if self.weapon_rate_clock > 0:
                self.weapon_rate_clock -= 1
            else:
                self.shoot()
                self.weapon_rate_clock = self.weapon.max_rate_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
            self.collision.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            self.weapon.kill()
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce

    def manage_weapon(self):
        self.weapon.angle = calc_angle(pygame.Vector2(self.rect.center), pygame.Vector2(self.player.feet.center)) #position en jeu du crosshair
        self.weapon.rect.center = self.rect.center

        #coefficients du vecteur de déplacement de l'arme par rapport au joueur
        self.weapon.speed_x = math.cos(self.weapon.angle)
        self.weapon.speed_y = math.sin(self.weapon.angle)

        #rotation de l'image de l'arme en fonction de l'angle
        self.weapon.rotate_img()

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.weapon.pos = [None, None]
        self.weapon.pos[0] = self.weapon.rect[0]
        self.weapon.pos[1] = self.weapon.rect[1]

        #met la position du tir à jour
        self.weapon.pos[0] += 18 * self.weapon.speed_x
        self.weapon.pos[1] += 18 * self.weapon.speed_y

        #maj du rectangle d'affichage
        self.weapon.rect.topleft = self.weapon.pos

        #arme et joueur visent dans le bon sens
        if (self.weapon.angle > math.pi / 2) or (self.weapon.angle < -math.pi / 2): #côté gauche
            self.weapon.image = pygame.transform.flip(self.weapon.image, False, True)

            if (self.weapon.angle > math.pi * (3/4)) or (self.weapon.angle < -math.pi * (3/4)):
                self.change_animation_list("left")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

        else: #côté droit
            if (self.weapon.angle < math.pi/4) and (self.weapon.angle > -math.pi/4):
                self.change_animation_list("right")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

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

    def get_image(self, sprite_sheet, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y et en fait un sprite 48*48"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA).convert_alpha()#surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        image = pygame.transform.scale(image, (48, 48))

        return image

    def shoot(self):
        shots = self.weapon.shoot(self)

        for shot in shots:
            self.player.map_manager.get_group().add(shot, layer=4)
            self.player.map_manager.get_mob_shots().append(shot)

class Mobot(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("mobot", fighting_mobs, player, speed, damage)

        self.speed = 0.6
        self.collision = copy.copy(self.feet)
        self.collision.height += 12
        self.weapon = Weapon(25, 1, 2, "10")
        self.weapon_rate_clock = 0
        self.angle_modif = 0

    def update(self):
        if self.pdv > 0:
            self.manage_weapon()

            #tire sur le joueur
            if self.weapon_rate_clock > 0:
                self.weapon_rate_clock -= 1
            else:
                self.shoot()
                self.weapon_rate_clock = self.weapon.max_rate_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
            self.collision.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            self.weapon.kill()
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce

    def manage_weapon(self):
        self.weapon.angle = calc_angle(pygame.Vector2(self.rect.center), pygame.Vector2(self.player.feet.center)) #position en jeu du crosshair
        self.weapon.rect.center = self.rect.center

        #coefficients du vecteur de déplacement de l'arme par rapport au joueur
        self.weapon.speed_x = math.cos(self.weapon.angle)
        self.weapon.speed_y = math.sin(self.weapon.angle)

        #rotation de l'image de l'arme en fonction de l'angle
        self.weapon.rotate_img()

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.weapon.pos = [None, None]
        self.weapon.pos[0] = self.weapon.rect[0]
        self.weapon.pos[1] = self.weapon.rect[1]

        #met la position du tir à jour
        self.weapon.pos[0] += 18 * self.weapon.speed_x
        self.weapon.pos[1] += 18 * self.weapon.speed_y

        #maj du rectangle d'affichage
        self.weapon.rect.topleft = self.weapon.pos

        #arme et joueur visent dans le bon sens
        if (self.weapon.angle > math.pi / 2) or (self.weapon.angle < -math.pi / 2): #côté gauche
            self.weapon.image = pygame.transform.flip(self.weapon.image, False, True)

            if (self.weapon.angle > math.pi * (3/4)) or (self.weapon.angle < -math.pi * (3/4)):
                self.change_animation_list("left")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

        else: #côté droit
            if (self.weapon.angle < math.pi/4) and (self.weapon.angle > -math.pi/4):
                self.change_animation_list("right")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

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

    def get_image(self, sprite_sheet, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y et en fait un sprite 48*48"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA).convert_alpha()#surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        image = pygame.transform.scale(image, (48, 48))

        return image

    def shoot(self):

        for i in range(-4, 4, 2):
            shots = self.weapon.shoot(self, i/4 * math.pi + self.angle_modif)

            for shot in shots:
                self.player.map_manager.get_group().add(shot, layer=4)
                self.player.map_manager.get_mob_shots().append(shot)
        
        self.angle_modif += 0.2

class Boss(Mob):

    def __init__(self, fighting_mobs, player, speed, damage, map_level):
        super().__init__("boss", fighting_mobs, player, speed, damage)

        self.speed = 0.2 * map_level
        self.angle_modif = 0
        self.max_weapon_rate_clock = 80
        self.max_pdv = 100
        self.pdv = 100

    def shoot(self):
        shots = []

        for i in range(-6, 6, 1):
            shots.append(CurveShot(0.005 + ((self.max_pdv - self.pdv) / self.max_pdv) * 0.005 * 3, math.pi, 1, self, 1 + (self.max_pdv - self.pdv) / self.max_pdv * 3, "techpack/Projectiles/projectiles x1", 1, i/6 * math.pi + self.angle_modif))
            shots.append(CurveShot(-0.005 - ((self.max_pdv - self.pdv) / self.max_pdv) * 0.005 * 3, math.pi, 1, self, 1 + (self.max_pdv - self.pdv) / self.max_pdv * 3, "techpack/Projectiles/projectiles x1", 1, i/6 * math.pi + self.angle_modif))

        for shot in shots:
            self.player.map_manager.get_group().add(shot, layer=4)
            self.player.map_manager.get_mob_shots().append(shot)
        
        self.angle_modif += 0.2

    def update(self):
        if self.pdv > 0:
            #tire sur le joueur
            if self.weapon_rate_clock > 0:
                self.weapon_rate_clock -= 1
            else:
                self.shoot()
                self.weapon_rate_clock = self.max_weapon_rate_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
        else:
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce