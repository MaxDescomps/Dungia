# Dungia

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

MODE MULTIJOUEUR LOCAL:  
  Une branche du projet supporte le mode multijoueur en local.  
  Attention: le multijoueur oblige seulement les joueurs à progresser en parallèle et leur permet de se voir, mais chacun combat ses propres monstres.  
  
  Pour jouer à deux il faut un joueur hôte et un joueur invité.  
  Le joueur hôte appuie sur 'h' dans le menu de démarrage, et donne l'adresse ip qui lui est donnée dans son terminal à l'invité.  
  L'invité appuie sur 'c' dans le menu de démarrage (le jeu gèle alors) et entre dans son terminal l'adresse ip fournie par l'hôte.  
  Les deux joueurs peuvent maintenant jouer.  
