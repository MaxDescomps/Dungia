import pygame

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0] << 1), int(self.size[1] << 1)))
        
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()