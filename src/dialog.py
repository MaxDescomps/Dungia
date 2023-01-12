import pygame

class DialogBox:
    """Classe des boites de dialogue"""

    def __init__(self, x: float, y: float):
        """
        Constructeur de la classe DialogBox
        
        Args:
            x(float): coordonnée horizontale
            y(float): coordonnée verticale
        """
        
        self.box = pygame.image.load("../image/dialog_box.png").convert_alpha()
        self.box = pygame.transform.scale(self.box, (800, 100))
        self.x = x
        self.y = y
        self.texts = []
        self.text_index = 0
        self.font = pygame.font.Font("../fonts/dialog_font.ttf", 20)
        self.reading = False

    def render(self, screen: pygame.Surface):
        """
        Affichage de la boite de dialogue
        
        Args:
            screen(pygame.Surface): Fenêtre d'affichage
        """

        if self.reading:
            screen.blit(self.box, (self.x, self.y))
            text = self.font.render(self.texts[self.text_index], False, (0,0,0))
            screen.blit(text, (self.x + 60, self.y + 40))

    def next_text(self):
        """Passe au dialogue suivant"""

        self.text_index += 1

        if self.text_index >= len(self.texts):
            self.reading = False #fin du dialogue

    def execute(self, dialog:list[str]=[]):
        """
        Démarre le dialogue
        
        Args:
            dialog(list[str]): liste des textes du dialogue
        """

        if self.reading:
            self.next_text()
        else:
            self.reading = True
            self.text_index = 0
            self.texts = dialog