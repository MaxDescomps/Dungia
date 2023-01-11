import pygame
from menu import Menu

def main():
    #initialisation de pygame
    pygame.init()
    pygame.mixer.init()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP]) #limite la liste des événements possibles

    #cache la souris
    pygame.mouse.set_visible(False)

    #menu de démarrage du jeu
    menu = Menu()
    menu.play()

    pygame.quit() #ferme pygame

main()