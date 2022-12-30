from entity import *

class NPC(Entity):

    def __init__(self, name, dialog):
        super().__init__(name, 0, 0)
        self.name = name
        self.dialog = dialog

    def teleport_spawn(self, map):
        point = map.tmx_data.get_object_by_name(self.name) #l'objet du tmx sur lequel on se teleporte
        self.position = [point.x, point.y]
        self.save_location() #permet de ne pas se tp en boucle sur une collision?