import pygame

class AnimateSprite(pygame.sprite.Sprite):

    def __init__(self, name):
        """
        Constructeur de la classe AnimateSprite
        
        Args:
            name(str): nom du png du spritesheet
        """

        super().__init__()
        self.sprite_sheet = pygame.image.load(f"../image/{name}.png").convert_alpha() #spritesheet avec paramètre de transparence alpha
        self.speed = 2
        self.clock = 0

        self.animation_index = 0

        self.images = {
            "down": self.get_images(0),
            "left": self.get_images(32),
            "right": self.get_images(64),
            "up": self.get_images(96),
        }

    def change_animation(self, direction):
        """
        Change l'animation du sprite avec le mouvement et la direction
        
        Args:
            direction(str): direction prise par le sprite
        """

        self.image = self.images[direction][self.animation_index]
        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[direction]):
                self.animation_index = 0
            
            self.clock = 0

    def get_images(self, y):
        """
        Récupère les sprites d'une ligne d'un spritesheet 32x32
        
        Args:
            y(int): numéro de ligne sur le spritesheet

        Returns:
            images(list): une liste d'images
        """

        images = []
        
        for i in range(0,3):
            x = i*32
            image = self.get_image(x, y)
            images.append(image)
        
        return images

    def get_image(self, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        return image.convert_alpha()