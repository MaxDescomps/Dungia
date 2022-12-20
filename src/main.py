import pygame
from game import Game

def main():
    #initialisation de pygame
    pygame.init()

    #cache la souris
    pygame.mouse.set_visible(False)

    #lancement du jeu
    game = Game()
    game.run()

main()