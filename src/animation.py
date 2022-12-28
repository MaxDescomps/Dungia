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
        self.direction = "down"

        self.animation_index = 0

        self.images = {
            "down": self.get_images(self.sprite_sheet, 0, 0, 3),
            "left": self.get_images(self.sprite_sheet, 32, 0, 3),
            "right": self.get_images(self.sprite_sheet, 64, 0, 3),
            "up": self.get_images(self.sprite_sheet, 96, 0, 3),
        }

    def change_animation_list(self, direction):
        """
        Change la liste de sprites utilisés
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

    def get_images(self, sprite_sheet, y, start, nb_sprites):
        """
        Récupère les sprites d'une ligne d'un spritesheet 32x32

        Args:
            y(int): numéro de ligne sur le spritesheet

        Returns:
            images(list): une liste d'images
        """

        images = []
        
        for i in range(start, start + nb_sprites):
            x = i*32
            image = self.get_image(sprite_sheet, x, y)
            images.append(image)
        
        return images

    def get_image(self, sprite_sheet, x, y):
        """Récupère un sprite 32*32 aux coordonnées x et y"""

        image = pygame.Surface([32, 32], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        return image.convert_alpha()