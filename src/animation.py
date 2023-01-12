import pygame

class AnimateSprite(pygame.sprite.Sprite):
    """Classe AnimateSprite utilisée pour animer les entités selon la direction"""

    def __init__(self, name: str):
        """
        Constructeur de la classe AnimateSprite
        
        Args:
            name(str): nom du png du spritesheet
        """

        super().__init__()
        self.sprite_sheet = pygame.image.load(f"../image/{name}.png").convert_alpha() #spritesheet avec paramètre de transparence alpha
        self.speed = 2 #vitesse de changement d'animation
        self.clock = 0 #compteur avant changement d'animation
        self.direction = "down"

        self.animation_index = 0 #numéro du sprite affiché

        #sprites organisés selon la direction correspondante
        self.images = {
            "down": self.get_images(self.sprite_sheet, 0, 0, 3),
            "left": self.get_images(self.sprite_sheet, 32, 0, 3),
            "right": self.get_images(self.sprite_sheet, 64, 0, 3),
            "up": self.get_images(self.sprite_sheet, 96, 0, 3),
        }

    def change_animation(self):
        """
        Change l'animation du sprite avec le mouvement et la direction
        """

        self.image = self.images[self.direction][self.animation_index]
        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[self.direction]):
                self.animation_index = 0
            
            self.clock = 0

    def get_images(self, sprite_sheet: pygame.Surface, y: float, start: int, nb_sprites: int) -> list[pygame.Surface]:
        """
        Récupère les sprites d'une ligne d'un spritesheet de type 32x32

        Args:
            sprite_sheet(pygame.Surface): le spritesheet source
            y(int): coordonnée verticale des sprites à récupérer
            start(int): premier spite à récupérer sur une ligne
            nb_sprites(int): nombre de sprites à récupérer sur une ligne

        Returns:
            images(list): la liste des sprites récupérés sur une ligne du spritesheet
        """

        images = []
        
        for i in range(start, start + nb_sprites):
            x = i*32
            image = self.get_image(sprite_sheet, x, y)
            images.append(image)
        
        return images

    def get_image(self, sprite_sheet: pygame.Surface, x: float, y:float) -> pygame.Surface:
        """
        Récupère un sprite 32*32 aux coordonnées x et y
        
        Args:
            sprite_sheet(pygame.Surface): le spritesheet source
            x(int): coordonnée horizontale du sprite à récupérer
            y(int): coordonnée verticale du sprite à récupérer
        """

        image = pygame.Surface([32, 32], pygame.SRCALPHA).convert_alpha() #surface avec un parametre de transparence (alpha = 0)
        image.blit(sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        
        return image