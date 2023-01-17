import pygame

class PauseMenu(pygame.sprite.Sprite):
    """Menu de pause du jeu"""

    def __init__(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT) -> None:
        """Constructeur de la classe PauseMenu"""

        super().__init__()

        self.screen = screen

        mult_width = SCREEN_WIDTH / 1920
        mult_height = SCREEN_HEIGHT / 1080

        self.image = pygame.image.load(f"../image/menu_pause2.png").convert() #spritesheet avec paramètre de transparence alpha
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.resume_rect = pygame.Rect(mult_width * 645, mult_height * 561, mult_width * 629, mult_height * 126)
        self.exit_rect = pygame.Rect(mult_width * 645, mult_height * 767, mult_width * 629 , mult_height * 126)
        
    def deploy(self):
        """Déploie le menu pause"""

        pygame.mixer.music.pause() #met la musique en pause
        pygame.mouse.set_visible(True) #affiche le curseur

        paused = True
        
        self.screen.blit(self.image, (0, 0))
        pygame.display.flip()

        running = self.handle_input()

        pygame.mouse.set_visible(False)
        pygame.mixer.music.unpause()

        return running

    def handle_input(self):
        """Gère les inputs dans le menu pause"""

        clock = pygame.time.Clock() #pour limiter les fps
        running = True

        while True:
            for event in pygame.event.get():

                #évènement souris click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()

                        if self.resume_rect.collidepoint(mouse_pos):
                            return running
                        elif self.exit_rect.collidepoint(mouse_pos):
                            running = False
                            return running
                
                #click clavier
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                            return running

                #fermeture fenetre de jeu
                elif event.type == pygame.QUIT:
                    running = False
                    return running

            clock.tick(60) #60 fps
                