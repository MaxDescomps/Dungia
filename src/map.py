import pygame, pytmx, pyscroll, random, copy
import pygame.sprite
from dataclasses import dataclass
from npc import *
from shot import Shot
from door import *
from mob import *

@dataclass
class Room:
    rect: pygame.Rect
    doors: list[Door]
    mobs: list[Mob]
    mob_spawns: list[(int, int)]
    boss: list[Mob]
    boss_spawns: list[(int, int)]
    fighting_mobs: list[Mob]
    walls: list[pygame.Rect]
    acids: list[pygame.Rect]
    visited: bool = False

@dataclass
class Portal:
    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str

@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    acids: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]
    player_shots: list[Shot]
    mob_shots: list[Shot]
    doors: list[Door] #liste des portes de la carte pour calcul plus rapide des portes de chaque pièce
    rooms: list[Room]

class MapManager:

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.maps = dict()
        self.current_map = "home"
        self.current_room = None
        self.zoom = 3
        self.map_names = ["tech3", "tech4", "tech5"]
        self.map_level = 0 #le numéro de l'étage actuel

        next_level = random.choice(self.map_names)

        self.register_map("home", portals=[
            Portal(from_world="home", origin_point="portal_home", target_world=next_level, teleport_point=f"spawn_{next_level}")
        ], npcs=[
            NPC("paul", dialog=["Cet endroit ne devrait pas exister...", "Vous voyez la grande pierre de l'autre coté?", "C'est un portail traversez-le!", "Vous ferez peut-être revivre l'esprit linux..."])
        ])

        self.teleport_player("player")
        self.teleport_npcs()

    def check_collisions(self):
        """Gère les collisions sur la carte"""

        #joueur - pièce
        self.current_room = None

        for room in self.get_map().rooms:
            if self.player.feet.colliderect(room.rect):
                self.current_room = room
                break #current_room trouvée

        player_collided = False

        #joueur - acide
        if self.player.feet.collidelist(self.current_room.acids) > -1:
            self.player.take_damage()

        #joueur - portails
        for portal in self.get_map().portals:
            point = self.get_object(portal.origin_point)
            portal_rect = pygame.Rect(point.x, point.y, point.width, point.height)#recree a chaque appel? + toute la map au lieu de room

            if self.player.feet.colliderect(portal_rect):
                self.map_level += 1 #étage suivant

                next_map_portal = random.choice(self.map_names)

                self.register_map(portal.target_world, portals=[
                    Portal(from_world=portal.target_world, origin_point=f"portal_{portal.target_world}", target_world=next_map_portal, teleport_point=f"spawn_{next_map_portal}")
                ], npcs=[
                    NPC("paul", dialog=[f"Vous êtes à l'étage {self.map_level}"])
                ])

                self.current_map = portal.target_world
                self.teleport_player(portal.teleport_point)
                self.teleport_npcs()

                player_collided = True
                break #collision trouvée

        if player_collided == False:

            #joueur - mur
            if self.player.feet.collidelist(self.current_room.walls) > -1:
                self.player.move_back()
            else:

                #joueur - npc
                for npc in self.get_npcs(): #?toute la map
                    if self.player.feet.colliderect(npc.feet):
                        self.player.move_back()
                        player_collided = True
                        break #collision trouvée

                #joueur - porte
                if not player_collided:
                    in_doorway = False #dit si le joueur est dans le passage d'une porte
                    for door in self.current_room.doors:
                        if self.player.feet.colliderect(door.collision_rect):
                            in_doorway = True

                            #collision sur porte fermée
                            if not door.opened or door.blocked:
                                self.player.move_back()
                                player_collided = True
                            break #collision trouvée

                #entrée dans une nouvelle pièce
                if self.current_room:
                    if not self.current_room.visited:
                        if not in_doorway:
                            self.current_room.visited = True
                            self.manage_room_hostility()
                    else:
                        if not self.current_room.fighting_mobs: #attend que la vague de monstres soit vaincue
                            self.manage_room_hostility()

            #tirs du joueur
            for shot in self.get_player_shots():

                #tirs joueur - murs
                if shot.colliderect.collidelist(self.get_walls()) > -1: #pas uniquement les murs de la pièce car les tirs peuvent en sortir
                    shot.kill()#enlève le tir de tous les groupes d'affichage
                    self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte

                else:
                    if self.current_room.fighting_mobs: #si la pièce est hostile
                        shot_destroyed = False

                        #tirs joueur - portes
                        for door in self.current_room.doors:
                            if shot.colliderect.colliderect(door.collision_rect):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                shot_destroyed = True
                                break

                        if not shot_destroyed:
                            for mob in self.current_room.fighting_mobs:

                                #tirs joueur - monstres
                                if shot.colliderect.colliderect(mob.collision):
                                    shot.kill()#enlève le tir de tous les groupes d'affichage
                                    self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                    mob.pdv -= shot.damage
                                    break #tir détruit, fin de la recherche de collision

            #tirs des monstres
            for shot in self.get_mob_shots():

                #tirs monstre - murs
                if shot.colliderect.collidelist(self.get_walls()) > -1: #pas uniquement les murs de la pièce car les tirs peuvent en sortir
                    shot.kill()#enlève le tir de tous les groupes d'affichage
                    self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte

                else:
                    if self.current_room.fighting_mobs: #si la pièce est hostile
                        shot_destroyed = False

                        #tirs monstre - portes
                        for door in self.current_room.doors:
                            if shot.colliderect.colliderect(door.collision_rect):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                shot_destroyed = True
                                break

                        if not shot_destroyed:
                            #tirs monstre - joueur
                            if shot.colliderect.colliderect(self.player.collision):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                self.player.take_damage()
                                break #tir détruit, fin de la recherche de collision

            #monstres
            if self.current_room:
                for mob in self.current_room.fighting_mobs:
                    #monstre - joueur
                    if mob.feet.colliderect(self.player.feet):
                        mob.move_back()
                        self.player.take_damage()

                    #monstre - porte
                    elif mob.feet.collidelist(self.current_room.doors) > -1:
                        mob.move_back()
                    
                    #monstre - mur
                    elif mob.feet.collidelist(self.current_room.walls) > -1:
                        mob.move_back()

                        mob_rect = copy.deepcopy(mob.feet)

                        mob_rect.x += mob.speed * 10
                        if mob_rect.collidelist(self.current_room.walls) > -1:
                            mob.move_up()
                        else:
                            mob_rect.x -= mob.speed * 20
                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                mob.move_down()
                        
                            mob_rect.x += mob.speed * 10
                            mob_rect.y += mob.speed * 10
                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                mob.move_right()
                            else:
                                mob_rect.y -= mob.speed * 20
                                if mob_rect.collidelist(self.current_room.walls) > -1:
                                    mob.move_left()

                                else:
                                    mob_rect.x += mob.speed * 10
                                    if mob_rect.collidelist(self.current_room.walls) > -1:
                                        mob.move_up()
                                    else:
                                        mob_rect.x -= mob.speed * 20
                                        if mob_rect.collidelist(self.current_room.walls) > -1:
                                            mob.move_left()
                                        else:
                                            mob_rect.y += mob.speed * 20
                                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                                mob.move_down()
                                            else:
                                                mob_rect.x += mob.speed * 20
                                                if mob_rect.collidelist(self.current_room.walls) > -1:
                                                    mob.move_right()



    def manage_room_hostility(self):
        """
        Fais apparaitre les monstres d'une pièce par vagues de 4 (maximum 5 apparitions par vague)
        Cause la fermeture des portes d'une pièce hostile
        """
        room = self.current_room

        #si pièce hostile
        if room.mobs or room.boss:
            #fermeture des portes
            for door in room.doors:
                door.closing = True

            #spawn des boss
            try:
                boss = room.boss.pop(0)
            except:
                #plus de boss à faire apparaître
                pass
            else:
                boss.teleport_spawn(room.boss_spawns[0])
                room.fighting_mobs.append(boss)
                self.get_group().add(boss)

                if boss.weapon:
                    self.get_group().add(boss.weapon, layer=1) #ajout de l'arme du mob au groupe de calques

            #spawn des mobs
            spawn_index = 0

            if 4 <= len(room.mob_spawns):
                spawn_limit = 4
            else:
                spawn_limit = len(room.mob_spawns)
            
            while len(room.fighting_mobs) < spawn_limit:
                try:
                    mob = room.mobs.pop(0)
                except:
                    #plus de mobs à faire apparaître
                    break
                else:
                    mob.teleport_spawn(room.mob_spawns[spawn_index])
                    room.fighting_mobs.append(mob)
                    self.get_group().add(mob)

                    if mob.weapon:
                        self.get_group().add(mob.weapon, layer=1) #ajout de l'arme du mob au groupe de calques

                    spawn_index += 1

        #si pièce neutre
        else:
            for door in room.doors:
                door.opening = True

    def teleport_player(self, name):
        """
        Téléporte le joueur sur un point de spawn dans une carte
        
        Args:
            name (str): nom du tmx de la carte à charger
        """
        self.player.weapon.kill() #supprime l'arme du joueur du groupe de calques

        point = self.get_object(name) #l'objet du tmx sur lequel on se teleporte
        self.player.position = [point.x, point.y]
        self.player.save_location() #permet de ne pas se tp en boucle sur une collision?

        self.get_map().group.add(self.player.weapon, layer = 5) #ajout de l'arme du joueur au groupe de calques

    def register_map(self, name, portals=[], npcs=[]):
        """
        Charge une carte une seule fois pour le reste du programme depuis un fichier tmx en remplissant
        une instance de la classe de données Map
        """

        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx") #charge le fichier tmx avec les surfaces de pygame 
        map_data = pyscroll.data.TiledMapData(tmx_data) #récupère les données de la carte
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size()) #gère le déplacement de la carte (quand le joueur est au centre de l'écran)
        self.map_layer.zoom = self.zoom #zoom sur la carte

        player_shots = [] #liste des tirs du joueur
        mob_shots = [] #liste des tirs des monstres
        doors = [] #liste des portes de la carte
        mob_spawns = [] #liste des points de spawn pour mob dans la carte
        boss_spawns = [] #liste des points de spawn pour boss dans la carte
        walls = [] #liste des rectangles de collision bloquants
        acids = [] #liste des cases acides

        for obj in tmx_data.objects:
            if obj.name == "door":
                door = HDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_r_door":
                door = VRDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_l_door":
                door = VLDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "acid":
                acids.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "boss_spawn":
                boss_spawns.append((obj.x, obj.y))

            else:
                for i in range (1,6):
                    if obj.name == f"mob_spawn{i}":
                        mob_spawns.append((obj.x, obj.y))
                        break

        #liste des pièces
        rooms = []

        #récupère les pièces du tmx et leurs informations après enregistrement des autres éléments
        for obj in tmx_data.objects:
            if obj.name == "room":
                #rectangle de la pièce
                room_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                #récupération des points de spawn des boss de la pièce
                room_boss_spawns = []
                for boss_spawn in boss_spawns:
                    if room_rect.collidepoint(boss_spawn):
                        room_boss_spawns.append(boss_spawn)

                #récupération des points de spawn des mobs de la pièce
                room_mob_spawns = []
                for mob_spawn in mob_spawns:
                    if room_rect.collidepoint(mob_spawn):
                        room_mob_spawns.append(mob_spawn)

                #récupération des portes de la pièce
                room_doors = []
                for door in doors:
                    if door.rect.colliderect(room_rect):

                        room_doors.append(door)

                #récupération des murs de la pièce
                room_walls = []
                for wall in walls:
                    if wall.colliderect(room_rect):

                        room_walls.append(wall)

                #récupération des cases acides de la pièce
                room_acids = []
                for acid in acids:
                    if acid.colliderect(room_rect):

                        room_acids.append(acid)

                #mobs combattants dans la pièce
                room_fighting_mobs = []

                #récuprération des mobs de la pièce
                room_mobs = []
                if room_mob_spawns: #si la pièce est prévue pour faire spawn des mobs
                    for i in range(len(room_mob_spawns) * 2):
                        rand = random.randint(0,100)
                        if rand < 1/6 * 100:
                            room_mobs.append(Drone(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 2/6 * 100:
                            room_mobs.append(Mobot(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 3/6 * 100:
                            room_mobs.append(Android(room_fighting_mobs, self.player, 1, 1))

                #récuprération des boss de la pièce
                room_boss = []
                if room_boss_spawns: #si la pièce est prévue pour faire spawn de boss
                    room_boss.append(Boss(room_fighting_mobs, self.player, 1, 2))

                rooms.append(Room(room_rect, room_doors, room_mobs, room_mob_spawns, room_boss, room_boss_spawns, room_fighting_mobs, room_walls, room_acids))


        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2) #groupe de calques
        group.add(self.player, layer = 6) #ajout du joueur au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #ajout des portes au groupe
        for door in doors:
            group.add(door, layer=7)

        #creer un objet map
        self.maps[name] = Map(name, walls, acids, group, tmx_data, portals, npcs, player_shots, mob_shots, doors, rooms)

    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self) -> list[pygame.Rect]:
        return self.get_map().walls

    def get_npcs(self) -> list[NPC]:
        return self.get_map().npcs

    def get_player_shots(self):
        return self.get_map().player_shots

    def get_mob_shots(self):
        return self.get_map().mob_shots

    def draw(self):
        """Affiche le groupe de calques centré sur le joueur"""

        self.get_group().draw(self.screen) #affiche le groupe de calques
        self.get_group().center(self.player.rect.center) #centre le groupe de calques sur l'image du joueur

    def update(self):
        """Met à jour le groupe de calques ses collisions"""

        self.get_group().update() #appel la méthode update de tous les sprites du groupe
        self.check_collisions() #gère les collisions sur la carte

    def get_object(self, name):
        """Récupère les informations d'un objet du fichier tmx de la carte"""

        return self.get_map().tmx_data.get_object_by_name(name)

    def check_npc_collisions(self, dialog_box):
        """Active le dialogue d'un un NPC en collision avec le joueur"""

        npcs = self.get_npcs()#?toute la carte au lieu de la pièce

        if npcs:
            for npc in npcs:
                if npc.feet.colliderect(self.player.rect):
                    dialog_box.execute(self.map_level, npc.dialog)
                else:
                    dialog_box.reading = 0
        else:
            dialog_box.reading = 0
    
    def teleport_npcs(self):
        """Place les NPC sur leurs points d'apparition"""

        map_data = self.maps[self.current_map]

        npcs = map_data.npcs

        for npc in npcs:
            npc.teleport_spawn(map_data)