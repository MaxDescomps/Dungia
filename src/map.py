from dataclasses import dataclass
import pygame, pytmx, pyscroll
from player import *

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

class MapManager:

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.maps = dict()
        self.current_map = "tech2"

        self.register_map("tech1", portals=[
            Portal(from_world="tech1", origin_point="enter_tech1", target_world="tech2", teleport_point="spawn_tech2")
        ], npcs=[
            NPC("paul")
        ])
        self.register_map("tech2", portals=[
            Portal(from_world="tech2", origin_point="enter_tech1", target_world="tech1", teleport_point="spawn_tech2")
        ])

        self.teleport_player("player")
        self.teleport_npcs()

    def check_collisions(self):
        #portails
        for portal in self.get_map().portals:
            if portal.from_world == self.current_map: #verif optionnelle?
                point = self.get_object(portal.origin_point)
                rect = pygame.Rect(point.x, point.y, point.width, point.height)#recree a chaque appel?

                if self.player.feet.colliderect(rect):
                    copy_portal = portal
                    self.current_map = portal.target_world
                    self.teleport_player(copy_portal.teleport_point)
        #murs
        for sprite in self.get_group().sprites():
            if sprite.feet.collidelist(self.get_walls()) > -1:
                sprite.move_back()

    def teleport_player(self, name):
        point = self.get_object(name) #l'objet du tmx sur lequel on se teleporte
        self.player.position = [point.x, point.y]
        self.player.save_location() #permet de ne pas se tp en boucle sur une collision?

    def register_map(self, name, portals=[], npcs=[]):
        #charger carte tmx (faire une fonction generique? idem dans game.init)
        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2
        
        #liste des rectangles de collision
        walls = []

        for obj in tmx_data.objects:
            if obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2) #groupe de calques
        group.add(self.player) #ajout du joueur au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #creer un objet map
        self.maps[name] = Map(name, walls, group, tmx_data, portals, npcs)

    def get_map(self): return self.maps[self.current_map]

    def get_group(self): return self.get_map().group

    def get_walls(self): return self.get_map().walls

    def draw(self):
        self.get_group().draw(self.screen)
        self.get_group().center(self.player.rect.center) #centre le groupe de calques sur l'image du joueur

    def update(self):
        self.get_group().update() #appel la méthode update de tous les sprites du groupe
        self.check_collisions()

    def get_object(self, name):
        return self.get_map().tmx_data.get_object_by_name(name)
    
    def teleport_npcs(self):
        for map in self.maps:
            map_data = self.maps[map]

            npcs = map_data.npcs

            for npc in npcs:
                npc.teleport_spawn(map_data)