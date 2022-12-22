import pygame

class DialogBox:

    def __init__(self, pos_x, pos_y):
        self.box = pygame.image.load("../image/dialog_box.png").convert_alpha()
        self.box = pygame.transform.scale(self.box, (800, 100))
        self.x = pos_x
        self.y = pos_y
        self.texts = []
        self.text_index = 0
        self.font = pygame.font.Font("../fonts/dialog_font.ttf", 20)
        self.reading = False

    def render(self, screen):
        if self.reading:
            screen.blit(self.box, (self.x, self.y))
            text = self.font.render(self.texts[self.text_index], False, (0,0,0))
            screen.blit(text, (self.x + 60, self.y + 40))

    def next_text(self):
        self.text_index += 1

        if self.text_index >= len(self.texts):
            #close dialog
            self.reading = False

    def execute(self, dialog=[]):
        if self.reading:
            self.next_text()
        else:
            self.reading = True
            self.text_index = 0
            self.texts = dialog