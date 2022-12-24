import pygame, pytmx, pyscroll, random
import pygame.sprite
from dataclasses import dataclass
from player import *
from shot import PlayerShot
from door import Door

@dataclass
class Room:
    rect: pygame.Rect
    doors: list[Door]
    mobs: list[Mob]
    mob_spawns: list[(int, int)]
    fighting_mobs: list[Mob]
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
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]
    shots: list[PlayerShot]
    doors: list[Door] #liste des portes de la carte pour calcul plus rapide des portes de chaque pièce
    rooms: list[Room]

class MapManager:

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.maps = dict()
        self.current_map = "tech2"
        self.zoom = 3

        self.register_map("tech1", portals=[
            Portal(from_world="tech1", origin_point="enter_tech1", target_world="tech2", teleport_point="spawn_tech2")
        ], npcs=[
            NPC("paul", dialog=["Salut c'est Julien je vous souhaite la bienvenue!", "Je vais vous expliquer comment gagner de l'argent!"])
        ])
        self.register_map("tech2", portals=[
            Portal(from_world="tech2", origin_point="enter_tech1", target_world="tech1", teleport_point="spawn_tech2")
        ])

        self.teleport_player("player")
        self.teleport_npcs()

    def check_collisions(self):
        """Gère les collisions sur la carte"""

        #portails
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map: #verif optionnelle?
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)#recree a chaque appel?

                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.teleport_player(copy_portal.teleport_point)
        #joueur
        #joueur - mur
        if self.player.feet.collidelist(self.get_walls()) > -1:
            self.player.move_back()
        else:
            player_collided = False
            
            #joueur - npc
            for npc in self.get_npcs():
                if self.player.feet.colliderect(npc.feet):
                    self.player.move_back()
                    player_collided = True

            #joueur - porte
            in_doorway = False #dit si le joueur est dans le passage d'une porte

            if not player_collided:
                for door in self.get_map().doors:
                    if self.player.feet.colliderect(door.rect):
                        in_doorway = True

                        #collision sur porte fermée
                        if not door.opened:
                            self.player.move_back()
                            player_collided = True

            #joueur - nouvelle pièce
            if not player_collided:
                for room in self.get_map().rooms:
                    if self.player.feet.colliderect(room.rect) and not room.visited and not in_doorway:
                        room.visited = True
                        self.manage_room_hostility(room)

        #tirs
        for shot in self.get_shots():
            if shot.colliderect.collidelist(self.get_walls()) > -1:
                shot.kill()#enlève le tir de tous les groupes d'affichage
                self.get_shots().remove(shot)#enlève le tir de la liste des tirs de la carte

    def manage_room_hostility(self, room):
        print("ok")
        
        #si pièce hostile
        if room.mobs:
            #fermeture des portes
            for door in room.doors:
                door.closing = True

            #spawn des mobs
            spawn_index = 0

            for i in range(5):
                try:
                    mob = room.mobs.pop(0)
                except:
                    print("plus de mobs à spawn dans la pièce")
                else:
                    print(room.mob_spawns)
                    mob.teleport_spawn(room.mob_spawns[0])
                    room.fighting_mobs.append(mob)
                    self.get_group().add(mob)

                    spawn_index += 1

    def teleport_player(self, name):
        point = self.get_object(name) #l'objet du tmx sur lequel on se teleporte
        self.player.position = [point.x, point.y]
        self.player.save_location() #permet de ne pas se tp en boucle sur une collision?

    def register_map(self, name, portals=[], npcs=[]):
        """
        Charge une carte une seule fois pour le reste du programme depuis un fichier tmx en remplissant
        une instance de la classe de données Map
        """

        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx") #charge le fichier tmx avec les surfaces de pygame 
        map_data = pyscroll.data.TiledMapData(tmx_data) #récupère les données de la carte
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size()) #gère le déplacement de la carte (quand le joueur est au centre de l'écran)
        self.map_layer.zoom = self.zoom #zoom sur la carte

        #liste des tirs
        shots = []

        #liste des portes et des points de spawn pour mob dans la carte
        doors = [] #pas besoin de stocker dans la class carte?
        mob_spawns = []
        for obj in tmx_data.objects:
            if obj.name == "door":
                door = Door(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)
            else:
                for i in range (1,6):
                    if obj.name == f"mob_spawn{i}":
                        mob_spawns.append((obj.x, obj.y))

        #liste des rectangles de collision
        walls = []

        #liste des pièces
        rooms = []

        #récupère les murs et pièces du tmx
        for obj in tmx_data.objects:
            if obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "room":
                #rectangle de la pièce
                room_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

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

                #récuprération des mobs de la pièce?
                room_mobs = []
                if room_mob_spawns: #si la pièce est prévue pour faire spawn des mobs
                    # if bool(random.getrandbits(1)): #une chance sur deux
                        room_mobs.append(Mob("boss"))

                rooms.append(Room(room_rect, room_doors, room_mobs, room_mob_spawns, []))


        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2) #groupe de calques
        group.add(self.player, layer = 3) #ajout du joueur au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #ajout des portes au groupe
        for door in doors:
            group.add(door, layer=4)

        #creer un objet map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs, shots, doors, rooms)

    def get_map(self):
        return self.maps[self.current_map]

    def get_group(self):
        return self.get_map().group

    def get_walls(self) -> list[pygame.Rect]:
        return self.get_map().walls

    def get_npcs(self) -> list[NPC]:
        return self.get_map().npcs

    def get_shots(self):
        return self.get_map().shots

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center) #centre le groupe de calques sur l'image du joueur

    def update(self):
        self.get_group().update() #appel la méthode update de tous les sprites du groupe
        self.check_collisions()

    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)

    def check_npc_collisions(self, dialog_box):

        npcs = self.get_npcs()

        if npcs:
            for npc in npcs:
                if npc.feet.colliderect(self.player.rect):
                    dialog_box.execute(npc.dialog)
                else:
                    dialog_box.reading = 0
        else:
            dialog_box.reading = 0
    
    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]

            npcs = map_data.npcs

            for npc in npcs:
                npc.teleport_spawn(map_data)