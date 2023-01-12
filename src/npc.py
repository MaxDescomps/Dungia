from entity import *
import pytmx

class NPC(Entity):
    """Classe des NPCs"""

    def __init__(self, name:str, dialog:list[str]):
        """
        Constructeur de la classe NPC

        Args:
            name(str): nom du png du spritesheet
            dialog(list[str]): dialogues du NPC
        """
        super().__init__(name, 0, 0)

        self.name = name
        self.dialog = dialog

    def teleport_spawn(self, point:pytmx.TiledObject):
        """
        Téléporte le NPC à son point d'apparition
        
        Args:
            point(pytmx.TiledObject): point d'apparition du monstre
        """

        self.position = [point.x, point.y]
        self.save_location() #permet de ne pas se tp en boucle sur une collision?