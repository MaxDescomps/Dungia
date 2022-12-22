import pygame

class AnimateSprite(pygame.sprite.Sprite):

    def __init__(self, name):
        super().__init__()
        self.sprite_sheet = pygame.image.load(f"../image/{name}.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

    def get_image(self, x, y):
        image = pygame.Surface([32, 32], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))
        return image.convert_alpha()