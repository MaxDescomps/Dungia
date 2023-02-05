# Dungia

Dungia est un jeu vidéo inspiré de Enter the Gungeon. Il inclut un mode solo et un mode multijoueur.
Vous devrez parcourir les différentes pièces du donjon et vaincre les monstres pour arriver au boss gardant l'accès de l'étage suivant.

INSTALLATION DES LIBRAIRIES:

  pip install pygame  
  pip install pytmx  
  pip install pyscroll  

LANCEMENT DU JEU:

  cd src  
  python3 main.py  

CONTRÔLES:

  Prévoir une souris pour jouer  
  Déplacement avec les touches "zqsd"  
  Changement d'arme avec la molette de la souris  
  Tir avec le click gauche de la souris  
  Echap pour ouvrir le menu pause ou pour quitter le jeu dans le menu de démarrage 
  Dialogue avec les PNJ avec la barre d'espace

MODE MULTIJOUEUR EN RÉSEAU LOCAL:  
  Le mode multijoueur en réseau local est la dernière fonctionnalité du projet.
  
  Pour jouer à deux il faut un joueur hôte et un joueur invité.  
  Le joueur hôte appuie sur 'h' dans le menu de démarrage, et donne l'adresse ip qui lui est donnée dans son terminal à l'invité.  
  L'invité appuie sur 'c' dans le menu de démarrage (le jeu gèle alors) et entre dans son terminal l'adresse ip fournie par l'hôte.  
  Les deux joueurs peuvent maintenant jouer ensemble.
