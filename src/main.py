import pygame
from menu import Menu

def main():
    #initialisation de pygame
    pygame.init()
    pygame.mixer.init()

    #cache la souris
    pygame.mouse.set_visible(False)

    #menu de démarrage du jeu
    menu = Menu()
    menu.play()

    pygame.quit() #ferme pygame

main()