import pygame

class Crosshair(pygame.sprite.Sprite):
    """Classe du viseur du joueur en jeu"""

    def __init__(self, image_path: str):
        """
        Constructeur de la classe Crosshair
        
        Args:
            image_path(str): chemin du png du sprite
        """

        super().__init__()
        
        #chargement du sprite
        self.image = pygame.image.load(image_path).convert_alpha()
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (64, 64))
        
        #coordonnées
        self.rect = self.image.get_rect()
        self.game_position = [0,0]

    def update(self):
        """Met la position du crosshair à jour"""

        self.rect.center = pygame.mouse.get_pos()