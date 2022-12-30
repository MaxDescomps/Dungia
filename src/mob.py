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
        shot = MobShot(self.player, self, 5, "techpack/Projectiles/projectiles x1", 1)
        self.player.map_manager.get_group().add(shot)
        self.player.map_manager.get_mob_shots().append(shot)