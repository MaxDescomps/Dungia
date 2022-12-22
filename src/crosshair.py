import pygame

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0] << 1), int(self.size[1] << 1)))
        
        self.image.convert_alpha()
        
        self.rect = self.image.get_rect()
        self.game_position = [0,0]

    def update(self):
        self.rect.center = pygame.mouse.get_pos()