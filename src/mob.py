from entity import *

class Mob(Entity):
    """
    Classe des monstres
    Les monstres apparaissent par vagues de 5 monstres maximum
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
        shot = MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1, calc_angle(self, self.player))
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
            if self.shot_clock > 0:
                self.shot_clock -= 1
            else:
                self.shoot()
                self.shot_clock = self.max_shot_clock

            self.save_location() #enregistre la position du mob avant deplacement pour pouvoir revenir en arrière en cas de collision
            self.move_towards_player()
            self.rect.topleft = self.position #la position du mob avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect mob.feet et mob.rect
            self.collision.midbottom = self.rect.center #aligne les centres des rect mob.feet et mob.rect
        else:
            self.kill() #retire le sprite des groupes d'affichage
            self.fighting_mobs.remove(self) #retire le mob de la liste des mobs combattants de la pièce

class Android(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("android", fighting_mobs, player, speed, damage)

        self.speed = 0.5

    def get_image(self, sprite_sheet, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y et en fait un sprite 48*48"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA).convert_alpha()#surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        image = pygame.transform.scale(image, (48, 48))

        return image

    def shoot(self):
        shots = [MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1, calc_angle(self, self.player)),
        MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1, calc_angle(self, self.player) - 0.3),
        MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1, calc_angle(self, self.player) + 0.3),
        ]

        for shot in shots:
            self.player.map_manager.get_group().add(shot)
            self.player.map_manager.get_mob_shots().append(shot)

class Mobot(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("mobot", fighting_mobs, player, speed, damage)

class Boss(Mob):

    def __init__(self, fighting_mobs, player, speed, damage):
        super().__init__("boss", fighting_mobs, player, speed, damage)