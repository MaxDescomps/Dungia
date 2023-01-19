import pygame, pytmx, pyscroll, random, copy, player
import pygame.sprite
from dataclasses import dataclass
from npc import NPC
from shot import Shot
from door import *
from mob import *
from dialog import DialogBox

@dataclass
class Room:
    """Représentation d'une pièce de la carte"""

    rect: pygame.Rect
    doors: list[Door]
    mobs: list[Mob]
    mob_spawns: list[(int, int)]
    boss: list[Mob]
    boss_spawns: list[(int, int)]
    fighting_mobs: list[Mob]
    walls: list[pygame.Rect]
    acids: list[pygame.Rect]
    visited: bool = False

@dataclass
class Portal:
    """Représentation d'un portail de la carte"""

    from_world: str
    origin_point: str
    target_world: str
    teleport_point: str

@dataclass
class Map:
    """Représentation de la carte"""

    name: str
    walls: list[pygame.Rect]
    acids: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]
    npcs: list[NPC]
    player_shots: list[Shot]
    mob_shots: list[Shot]
    doors: list[Door] #liste des portes de la carte pour calcul plus rapide des portes de chaque pièce
    rooms: list[Room]

class MapManager:
    """Gestionnaire des cartes du jeu"""

    def __init__(self, screen:pygame.Surface, player:player.Player):
        """
        Constructeur de la classe MapManager
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            player: joueur dans l'environnement de ce gestionnaire de carte
        """

        self.screen = screen
        self.player = player

        self.maps = dict() #cartes gérées
        self.map_names = ["tech3", "tech4", "tech5"] #nom des différentes cartes
        self.current_map = "home" #carte actuelle du joueur
        self.current_room = None #pièce actuelle du joueur

        self.zoom = 2 #zoom d'affichage
        self.map_level = 0 #le numéro de l'étage actuel
        self.boss_fight = False #indicateur de combat contre un boss

        next_level = random.choice(self.map_names) #désignation aléatoire de la prochaine carte

        #génération de la première carte
        self.register_map("home", portals=[
            Portal(from_world="home", origin_point="portal_home", target_world=next_level, teleport_point=f"spawn_{next_level}")
        ], npcs=[
            NPC("paul", dialog=["Je pensais que ça n'était qu'un mythe...", "L'ESTACA avait bien un labo secret dans la foret!", "Je vais te suivre à l'interieur...", "Tu vois la grande pierre de l'autre coté?", "C'est un portail... traverse-le!"])
        ])

        #placement de entités joueurs et NPC sur la carte actuelle
        self.teleport_player("player")
        self.teleport_npcs()

    def check_collisions(self):
        """Gère les collisions sur la carte"""

        #joueur - pièce
        #recherche de la pièce actuelle
        self.current_room = None

        for room in self.get_map().rooms:
            if self.player.feet.colliderect(room.rect):
                self.current_room = room
                break #current_room trouvée

        player_collided = False #indicateur de collision trouvée

        #joueur - acide
        if self.player.feet.collidelist(self.current_room.acids) > -1:
            self.player.take_damage()

        #joueur - portails
        for portal in self.get_map().portals:
            point = self.get_object(portal.origin_point)
            portal_rect = pygame.Rect(point.x, point.y, point.width, point.height)#recree a chaque appel? + toute la map au lieu de room

            if self.player.feet.colliderect(portal_rect):
                self.map_level += 1 #étage suivant

                self.current_map = portal.target_world
                next_map_portal = self.select_new_map()

                self.register_map(portal.target_world, portals=[
                    Portal(from_world=portal.target_world, origin_point=f"portal_{portal.target_world}", target_world=next_map_portal, teleport_point=f"spawn_{next_map_portal}")
                ], npcs=[
                    NPC("paul", dialog=[f"On est à l'étage {self.map_level}!", "Il faut continuer..."])
                ])

                self.teleport_player(portal.teleport_point)

                if self.map_level > 0:
                    pygame.mixer.music.load("../music/battle_low.wav")
                    pygame.mixer.music.play(-1) #répète la musique à indéfiniment
                else:
                    pygame.mixer.music.load("../music/mysterious.wav")
                    pygame.mixer.music.play(-1) #répète la musique à indéfiniment

                self.teleport_npcs()

                player_collided = True
                break #collision trouvée

        if player_collided == False:

            #joueur - mur
            if self.player.feet.collidelist(self.current_room.walls) > -1:
                self.player.move_back()
            else:

                #joueur - npc
                for npc in self.get_npcs(): #?toute la map
                    if self.player.feet.colliderect(npc.feet):
                        self.player.move_back()
                        player_collided = True
                        break #collision trouvée

                #joueur - porte
                if not player_collided:
                    in_doorway = False #dit si le joueur est dans le passage d'une porte
                    for door in self.current_room.doors:
                        if self.player.feet.colliderect(door.collision_rect):
                            in_doorway = True

                            #collision sur porte fermée
                            if not door.opened or door.blocked:
                                self.player.move_back()
                                player_collided = True
                            break #collision trouvée

                #entrée dans une nouvelle pièce
                if self.current_room:
                    if not self.current_room.visited:
                        if not in_doorway:
                            self.current_room.visited = True
                            self.manage_room_hostility()
                    else:
                        if not self.current_room.fighting_mobs: #attend que la vague de monstres soit vaincue
                            self.manage_room_hostility()

            #tirs du joueur
            for shot in self.get_player_shots():

                #tirs joueur - murs
                if shot.colliderect.collidelist(self.get_walls()) > -1: #pas uniquement les murs de la pièce car les tirs peuvent en sortir
                    shot.kill()#enlève le tir de tous les groupes d'affichage
                    self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte

                else:
                    if self.current_room.fighting_mobs: #si la pièce est hostile
                        shot_destroyed = False

                        #tirs joueur - portes
                        for door in self.current_room.doors:
                            if shot.colliderect.colliderect(door.collision_rect):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                shot_destroyed = True
                                break

                        if not shot_destroyed:
                            for mob in self.current_room.fighting_mobs:

                                #tirs joueur - monstres
                                if shot.colliderect.colliderect(mob.collision):
                                    shot.kill()#enlève le tir de tous les groupes d'affichage
                                    self.get_player_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                    mob.pdv -= shot.damage
                                    break #tir détruit, fin de la recherche de collision

            #tirs des monstres
            for shot in self.get_mob_shots():

                #tirs monstre - murs
                if shot.colliderect.collidelist(self.get_walls()) > -1: #pas uniquement les murs de la pièce car les tirs peuvent en sortir
                    shot.kill()#enlève le tir de tous les groupes d'affichage
                    self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte

                else:
                    if self.current_room.fighting_mobs: #si la pièce est hostile
                        shot_destroyed = False

                        #tirs monstre - portes
                        for door in self.current_room.doors:
                            if shot.colliderect.colliderect(door.collision_rect):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                shot_destroyed = True
                                break

                        if not shot_destroyed:
                            #tirs monstre - joueur
                            if shot.colliderect.colliderect(self.player.collision):
                                shot.kill()#enlève le tir de tous les groupes d'affichage
                                self.get_mob_shots().remove(shot)#enlève le tir de la liste des tirs de la carte
                                self.player.take_damage()
                                break #tir détruit, fin de la recherche de collision

            #monstres
            if self.current_room:
                for mob in self.current_room.fighting_mobs:
                    #monstre - joueur
                    if mob.feet.colliderect(self.player.feet):
                        mob.move_back()
                        self.player.take_damage()

                    #monstre - porte
                    elif mob.feet.collidelist(self.current_room.doors) > -1:
                        mob.move_back()
                    
                    #monstre - mur
                    elif mob.feet.collidelist(self.current_room.walls) > -1:
                        mob.move_back()

                        mob_rect = copy.deepcopy(mob.feet)

                        mob_rect.x += mob.speed * 10
                        if mob_rect.collidelist(self.current_room.walls) > -1:
                            mob.move_up()
                        else:
                            mob_rect.x -= mob.speed * 20
                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                mob.move_down()
                        
                            mob_rect.x += mob.speed * 10
                            mob_rect.y += mob.speed * 10
                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                mob.move_right()
                            else:
                                mob_rect.y -= mob.speed * 20
                                if mob_rect.collidelist(self.current_room.walls) > -1:
                                    mob.move_left()

                                else:
                                    mob_rect.x += mob.speed * 10
                                    if mob_rect.collidelist(self.current_room.walls) > -1:
                                        mob.move_up()
                                    else:
                                        mob_rect.x -= mob.speed * 20
                                        if mob_rect.collidelist(self.current_room.walls) > -1:
                                            mob.move_left()
                                        else:
                                            mob_rect.y += mob.speed * 20
                                            if mob_rect.collidelist(self.current_room.walls) > -1:
                                                mob.move_down()
                                            else:
                                                mob_rect.x += mob.speed * 20
                                                if mob_rect.collidelist(self.current_room.walls) > -1:
                                                    mob.move_right()

    def select_new_map(self) -> str:
        """
        Sélectionne une nouvelle carte différente de la carte actuelle
        
        Returns:
            new_map(str): nom de la nouvelle carte
        """

        new_map = random.choice(self.map_names)

        while(new_map == self.current_map):
            new_map = random.choice(self.map_names)
        
        return new_map

    def manage_room_hostility(self):
        """
        Gestion d'une pièce hostile
        Fais apparaitre les monstres par vagues
        Gère la fermeture et l'ouverture des portes
        """
        room = self.current_room

        #si pièce hostile
        if room.mobs or room.boss:
            #fermeture des portes
            for door in room.doors:
                door.closing = True

            #spawn des boss
            try:
                boss = room.boss.pop(0)
            except:
                #plus de boss à faire apparaître
                pass
            else:
                pygame.mixer.music.load("../music/boss_low.wav")
                pygame.mixer.music.play(-1) #répète la musique à indéfiniment
                self.boss_fight = True

                boss.teleport_spawn(room.boss_spawns[0])
                room.fighting_mobs.append(boss)
                self.get_group().add(boss)

                if boss.weapon:
                    self.get_group().add(boss.weapon, layer=1) #ajout de l'arme du mob au groupe de calques

            #spawn des mobs
            spawn_index = 0

            if 4 <= len(room.mob_spawns):
                spawn_limit = 4
            else:
                spawn_limit = len(room.mob_spawns)
            
            while len(room.fighting_mobs) < spawn_limit:
                try:
                    mob = room.mobs.pop(0)
                except:
                    #plus de mobs à faire apparaître
                    break
                else:
                    mob.teleport_spawn(room.mob_spawns[spawn_index])
                    room.fighting_mobs.append(mob)
                    self.get_group().add(mob)

                    if mob.weapon:
                        self.get_group().add(mob.weapon, layer=1) #ajout de l'arme du mob au groupe de calques

                    spawn_index += 1

        #si pièce neutre
        else:
            if self.boss_fight:
                pygame.mixer.music.load("../music/win_low.wav")
                pygame.mixer.music.play(-1) #répète la musique à indéfiniment
                self.boss_fight = False

            for door in room.doors:
                door.opening = True

    def teleport_player(self, name:str):
        """
        Téléporte le joueur sur un point de spawn dans une carte
        
        Args:
            name(str): nom du point de destination
        """

        point = self.get_object(name) #l'objet du tmx sur lequel on se teleporte
        self.player.position = [point.x, point.y]
        self.player.save_location() #permet de ne pas se tp en boucle sur une collision?

    def register_map(self, name:str, portals:list[Portal]=[], npcs:list[NPC]=[]):
        """
        Génère une carte depuis un fichier tmx

        Args:
            name(str): nom du fichier tmx de la carte
            portals(list[Portal]): portails présents sur la carte
            npcs(list[NPC]): NPCs présents sur la carte
        """

        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx") #charge le fichier tmx avec les surfaces de pygame 
        map_data = pyscroll.data.TiledMapData(tmx_data) #récupère les données de la carte
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size()) #gère le déplacement de la carte (quand le joueur est au centre de l'écran)
        self.map_layer.zoom = self.zoom #zoom sur la carte

        player_shots = [] #liste des tirs du joueur
        mob_shots = [] #liste des tirs des monstres
        doors = [] #liste des portes de la carte
        mob_spawns = [] #liste des points de spawn pour mob dans la carte
        boss_spawns = [] #liste des points de spawn pour boss dans la carte
        walls = [] #liste des rectangles de collision bloquants
        acids = [] #liste des cases acides

        for obj in tmx_data.objects:
            if obj.name == "door":
                door = HDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_r_door":
                door = VRDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_l_door":
                door = VLDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "acid":
                acids.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "boss_spawn":
                boss_spawns.append((obj.x, obj.y))

            else:
                for i in range (1,6):
                    if obj.name == f"mob_spawn{i}":
                        mob_spawns.append((obj.x, obj.y))
                        break

        #liste des pièces
        rooms = []

        #récupère les pièces du tmx et leurs informations après enregistrement des autres éléments
        for obj in tmx_data.objects:
            if obj.name == "room":
                #rectangle de la pièce
                room_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                #récupération des points de spawn des boss de la pièce
                room_boss_spawns = []
                for boss_spawn in boss_spawns:
                    if room_rect.collidepoint(boss_spawn):
                        room_boss_spawns.append(boss_spawn)

                #récupération des points de spawn des mobs de la pièce
                room_mob_spawns = []
                for mob_spawn in mob_spawns:
                    if room_rect.collidepoint(mob_spawn):
                        room_mob_spawns.append(mob_spawn)

                #récupération des portes de la pièce
                room_doors = []
                for door in doors:
                    if door.rect.colliderect(room_rect):

                        room_doors.append(door)

                #récupération des murs de la pièce
                room_walls = []
                for wall in walls:
                    if wall.colliderect(room_rect):

                        room_walls.append(wall)

                #récupération des cases acides de la pièce
                room_acids = []
                for acid in acids:
                    if acid.colliderect(room_rect):

                        room_acids.append(acid)

                #mobs combattants dans la pièce
                room_fighting_mobs = []

                #récuprération des mobs de la pièce
                room_mobs = []
                if room_mob_spawns: #si la pièce est prévue pour faire spawn des mobs
                    for i in range(len(room_mob_spawns) * 2):
                        rand = random.randint(0,100)
                        if rand < 1/6 * 100:
                            room_mobs.append(Drone(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 2/6 * 100:
                            room_mobs.append(Mobot(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 3/6 * 100:
                            room_mobs.append(Android(room_fighting_mobs, self.player, 1, 1))

                #récuprération des boss de la pièce
                room_boss = []
                if room_boss_spawns: #si la pièce est prévue pour faire spawn de boss
                    room_boss.append(Boss(room_fighting_mobs, self.player, 1, 2, self.map_level))

                rooms.append(Room(room_rect, room_doors, room_mobs, room_mob_spawns, room_boss, room_boss_spawns, room_fighting_mobs, room_walls, room_acids))


        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2) #groupe de calques
        group.add(self.player, layer = 6) #ajout du joueur au groupe de calques
        group.add(self.player.weapon, layer = 5) #ajout de l'arme du joueur au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #ajout des portes au groupe
        for door in doors:
            group.add(door, layer=7)

        #creer un objet map
        self.maps[name] = Map(name, walls, acids, group, tmx_data, portals, npcs, player_shots, mob_shots, doors, rooms)

    def get_map(self) -> Map:
        """
        Récupère la carte actuelle du gestionnaire de cartes
        
        Returns:
            current_map(Map): la carte actuelle
        """

        return self.maps[self.current_map]

    def get_group(self) -> pyscroll.PyscrollGroup:
        """
        Récupère le groupe de calques de la carte
        
        Returns:
            group(pyscroll.PyscrollGroup): le groupe de calques de la carte
        """

        return self.get_map().group

    def get_walls(self) -> list[pygame.Rect]:
        """
        Récupère les collisions des murs de la carte
        
        Returns:
            walls(list[pygame.Rect]): les collisions des murs de la carte
        """

        return self.get_map().walls

    def get_npcs(self) -> list[NPC]:
        """
        Récupère les NPCs de la carte
        
        Returns:
            npcs(list[NPC]): les NPCs de la carte
        """

        return self.get_map().npcs

    def get_player_shots(self) -> list[Shot]:
        """
        Récupère les tirs des joueurs
        
        Returns:
            player_shots(list[Shot]): les tirs des joueurs
        """

        return self.get_map().player_shots

    def get_mob_shots(self) -> list[Shot]:
        """
        Récupère les tirs des monstres
        
        Returns:
            mob_shots(list[Shot]): les tirs des monstres
        """

        return self.get_map().mob_shots

    def draw(self):
        """Affiche le groupe de calques centré sur le joueur"""

        self.get_group().draw(self.screen) #affiche le groupe de calques
        self.get_group().center(self.player.rect.center) #centre le groupe de calques sur l'image du joueur

    def update(self):
        """Met à jour le groupe de calques des collisions"""

        self.get_group().update() #appel la méthode update de tous les sprites du groupe
        self.check_collisions() #gère les collisions sur la carte

    def get_object(self, name:str) -> pytmx.TiledObject:
        """
        Récupère un objet du fichier tmx de la carte

        Args:
            name(str): le nom de l'objet à récupérer dans le fichier tmx
        
        Returns:
            object(pytmx.TiledObject): un objet du fichier tmx de la carte
        """

        return self.get_map().tmx_data.get_object_by_name(name)

    def check_npc_collisions(self, dialog_box:DialogBox):
        """
        Active le dialogue d'un NPC en collision avec le joueur
        
        Args:
            dialog_box(DialogBox): la boite de dialogue à activer
        """

        npcs = self.get_npcs()#?toute la carte au lieu de la pièce

        if npcs:
            for npc in npcs:
                if npc.feet.colliderect(self.player.rect):
                    dialog_box.execute(npc.dialog)
                else:
                    dialog_box.reading = 0
        else:
            dialog_box.reading = 0
    
    def teleport_npcs(self):
        """Place les NPC sur leurs points d'apparition"""

        map_data = self.maps[self.current_map]

        npcs = map_data.npcs

        for npc in npcs:
            npc.teleport_spawn(self.get_object(npc.name))

class MapManagerMulti(MapManager):
    """Classe du gestionnaire de cartes du mode multijoueur"""

    def __init__(self, screen: pygame.Surface, player: player.Player, p2: player.PlayerMulti):
        self.p2 = p2
        super().__init__(screen, player)


    def teleport_player(self, name:str):
        """
        Téléporte le joueur sur un point de spawn dans une carte
        
        Args:
            name(str): nom du point de destination
        """
        point = self.get_object(name) #l'objet du tmx sur lequel on se teleporte
        self.player.position = [point.x, point.y]
        self.p2.position = [point.x, point.y]
        self.p2.save_location() #permet de ne pas se tp en boucle sur une collision?

class MapManagerHost(MapManagerMulti):
    """Classe du gestionnaire de cartes du client-serveur (joueur hôte) en multijoueur"""

    def __init__(self, screen: pygame.Surface, player: player.Player, p2: player.PlayerMulti):
        """
        Constructeur de la classe MapManagerHost
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            player: joueur dans l'environnement de ce gestionnaire de carte
            p2: représentation du joueur client
        """

        super().__init__(screen, player, p2)

    def register_map(self, name:str, portals:list[Portal]=[], npcs:list[NPC]=[]):
        """
        Génère une carte depuis un fichier tmx

        Args:
            name(str): nom du fichier tmx de la carte
            portals(list[Portal]): portails présents sur la carte
            npcs(list[NPC]): NPCs présents sur la carte
        """

        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx") #charge le fichier tmx avec les surfaces de pygame 
        map_data = pyscroll.data.TiledMapData(tmx_data) #récupère les données de la carte
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size()) #gère le déplacement de la carte (quand le joueur est au centre de l'écran)
        self.map_layer.zoom = self.zoom #zoom sur la carte

        player_shots = [] #liste des tirs du joueur
        mob_shots = [] #liste des tirs des monstres
        doors = [] #liste des portes de la carte
        mob_spawns = [] #liste des points de spawn pour mob dans la carte
        boss_spawns = [] #liste des points de spawn pour boss dans la carte
        walls = [] #liste des rectangles de collision bloquants
        acids = [] #liste des cases acides

        for obj in tmx_data.objects:
            if obj.name == "door":
                door = HDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_r_door":
                door = VRDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_l_door":
                door = VLDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "acid":
                acids.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "boss_spawn":
                boss_spawns.append((obj.x, obj.y))

            else:
                for i in range (1,6):
                    if obj.name == f"mob_spawn{i}":
                        mob_spawns.append((obj.x, obj.y))
                        break

        #liste des pièces
        rooms = []

        #récupère les pièces du tmx et leurs informations après enregistrement des autres éléments
        for obj in tmx_data.objects:
            if obj.name == "room":
                #rectangle de la pièce
                room_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                #récupération des points de spawn des boss de la pièce
                room_boss_spawns = []
                for boss_spawn in boss_spawns:
                    if room_rect.collidepoint(boss_spawn):
                        room_boss_spawns.append(boss_spawn)

                #récupération des points de spawn des mobs de la pièce
                room_mob_spawns = []
                for mob_spawn in mob_spawns:
                    if room_rect.collidepoint(mob_spawn):
                        room_mob_spawns.append(mob_spawn)

                #récupération des portes de la pièce
                room_doors = []
                for door in doors:
                    if door.rect.colliderect(room_rect):

                        room_doors.append(door)

                #récupération des murs de la pièce
                room_walls = []
                for wall in walls:
                    if wall.colliderect(room_rect):

                        room_walls.append(wall)

                #récupération des cases acides de la pièce
                room_acids = []
                for acid in acids:
                    if acid.colliderect(room_rect):

                        room_acids.append(acid)

                #mobs combattants dans la pièce
                room_fighting_mobs = []

                #récuprération des mobs de la pièce
                room_mobs = []
                if room_mob_spawns: #si la pièce est prévue pour faire spawn des mobs
                    for i in range(len(room_mob_spawns) * 2):
                        rand = random.randint(0,100)
                        if rand < 1/6 * 100:
                            room_mobs.append(Drone(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 2/6 * 100:
                            room_mobs.append(Mobot(room_fighting_mobs, self.player, 1, 1))
                        elif rand < 3/6 * 100:
                            room_mobs.append(Android(room_fighting_mobs, self.player, 1, 1))

                #récuprération des boss de la pièce
                room_boss = []
                if room_boss_spawns: #si la pièce est prévue pour faire spawn de boss
                    room_boss.append(Boss(room_fighting_mobs, self.player, 1, 2, self.map_level))

                rooms.append(Room(room_rect, room_doors, room_mobs, room_mob_spawns, room_boss, room_boss_spawns, room_fighting_mobs, room_walls, room_acids))


        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2) #groupe de calques
        group.add(self.player, layer = 6) #ajout du joueur au groupe de calques
        group.add(self.p2, layer = 6) #ajout du joueur 2 au groupe de calques
        group.add(self.player.weapon, layer = 5) #ajout de l'arme du joueur au groupe de calques
        group.add(self.p2.weapon, layer = 5) #ajout de l'arme du joueur 2 au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #ajout des portes au groupe
        for door in doors:
            group.add(door, layer=7)

        #creer un objet map
        self.maps[name] = Map(name, walls, acids, group, tmx_data, portals, npcs, player_shots, mob_shots, doors, rooms)

class MapManagerCli(MapManagerMulti):
    """Classe du gestionnaire de cartes du client (joueur invité) en multijoueur"""

    def __init__(self, screen: pygame.Surface, player: player.Player, p2: player.PlayerMulti):
        """
        Constructeur de la classe MapManagerCli
        
        Args:
            screen(pygame.Surface): fenêtre d'affichage
            player: joueur dans l'environnement de ce gestionnaire de carte
            p2: représentation du joueur hôte
        """

        super().__init__(screen, player, p2)
        
        self.screen = screen
        self.player = player

        self.maps = dict() #cartes gérées
        self.map_names = ["tech3", "tech4", "tech5"] #nom des différentes cartes
        self.current_map = "home" #carte actuelle du joueurs
        self.current_room = None #pièce actuelle du joueur
        self.p2_current_room = None #pièce actuelle du joueur2

        self.map_level = 0 #le numéro de l'étage actuel
        self.boss_fight = False #indicateur de combat contre un boss

        #génération de la première carte
        self.register_map("home", npcs=[
            NPC("paul", dialog=["Je pensais que ça n'était qu'un mythe...", "L'ESTACA avait bien un labo secret dans la foret!", "Je vais te suivre à l'interieur...", "Tu vois la grande pierre de l'autre coté?", "C'est un portail... traverse-le!"])
        ])

        self.check_p2_room() #met l'information de la pièce du joueur 2 à jour

        #placement de entités joueurs et NPC sur la carte actuelle
        self.teleport_player("player")
        self.teleport_npcs()
    
    def register_map(self, name:str, portals:list[Portal]=[], npcs:list[NPC]=[]):
        """
        Génère une carte depuis un fichier tmx

        Args:
            name(str): nom du fichier tmx de la carte
            portals(list[Portal]): portails présents sur la carte
            npcs(list[NPC]): NPCs présents sur la carte
        """

        tmx_data = pytmx.util_pygame.load_pygame(f"../image/{name}.tmx") #charge le fichier tmx avec les surfaces de pygame 
        map_data = pyscroll.data.TiledMapData(tmx_data) #récupère les données de la carte
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size()) #gère le déplacement de la carte (quand le joueur est au centre de l'écran)
        self.map_layer.zoom = self.zoom #zoom sur la carte

        player_shots = [] #liste des tirs du joueur
        mob_shots = [] #liste des tirs des monstres
        doors = [] #liste des portes de la carte
        mob_spawns = [] #liste des points de spawn pour mob dans la carte
        boss_spawns = [] #liste des points de spawn pour boss dans la carte
        walls = [] #liste des rectangles de collision bloquants
        acids = [] #liste des cases acides

        for obj in tmx_data.objects:
            if obj.name == "door":
                door = HDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_r_door":
                door = VRDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "v_l_door":
                door = VLDoor(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                doors.append(door)

            elif obj.name == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "acid":
                acids.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

            elif obj.name == "boss_spawn":
                boss_spawns.append((obj.x, obj.y))

            else:
                for i in range (1,6):
                    if obj.name == f"mob_spawn{i}":
                        mob_spawns.append((obj.x, obj.y))
                        break

        #liste des pièces
        rooms = []

        #récupère les pièces du tmx et leurs informations après enregistrement des autres éléments
        for obj in tmx_data.objects:
            if obj.name == "room":
                #rectangle de la pièce
                room_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

                #récupération des points de spawn des boss de la pièce
                room_boss_spawns = []
                for boss_spawn in boss_spawns:
                    if room_rect.collidepoint(boss_spawn):
                        room_boss_spawns.append(boss_spawn)

                #récupération des points de spawn des mobs de la pièce
                room_mob_spawns = []
                for mob_spawn in mob_spawns:
                    if room_rect.collidepoint(mob_spawn):
                        room_mob_spawns.append(mob_spawn)

                #récupération des portes de la pièce
                room_doors = []
                for door in doors:
                    if door.rect.colliderect(room_rect):

                        room_doors.append(door)

                #récupération des murs de la pièce
                room_walls = []
                for wall in walls:
                    if wall.colliderect(room_rect):

                        room_walls.append(wall)

                #récupération des cases acides de la pièce
                room_acids = []
                for acid in acids:
                    if acid.colliderect(room_rect):

                        room_acids.append(acid)

                #mobs combattants dans la pièce
                room_fighting_mobs = []
                room_mobs = []
                room_boss = []

                rooms.append(Room(room_rect, room_doors, room_mobs, room_mob_spawns, room_boss, room_boss_spawns, room_fighting_mobs, room_walls, room_acids))


        # dessiner le groupe de calques
        group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2) #groupe de calques
        group.add(self.player, layer = 6) #ajout du joueur au groupe de calques
        group.add(self.p2, layer = 6) #ajout du joueur 2 au groupe de calques
        group.add(self.player.weapon, layer = 5) #ajout de l'arme du joueur au groupe de calques
        group.add(self.p2.weapon, layer = 5) #ajout de l'arme du joueur 2 au groupe de calques

        #ajout des npc au groupe
        for npc in npcs:
            group.add(npc)

        #ajout des portes au groupe
        for door in doors:
            group.add(door, layer=7)

        #creer un objet map
        self.maps[name] = Map(name, walls, acids, group, tmx_data, portals, npcs, player_shots, mob_shots, doors, rooms)

    def add_serv_mob(self, mob_info:list[int]):
        mob_type = mob_info[2]

        if mob_type == 1:
            mob = Drone(self.p2_current_room.fighting_mobs, self.p2, 1, 1)
        elif mob_type == 2:
            mob = Android(self.p2_current_room.fighting_mobs, self.p2, 1, 1)
        elif mob_type == 3:
            mob = Mobot(self.p2_current_room.fighting_mobs, self.p2, 1, 1)
        elif mob_type == 4:
            mob = Boss(self.p2_current_room.fighting_mobs, self.p2, 1, 2, self.map_level)

        mob.position = [mob_info[0], mob_info[1]]
        mob.pdv = mob_info[4]
        mob.angle_modif = mob_info[5]
        
        self.p2_current_room.fighting_mobs.append(mob)
        self.get_group().add(mob)

        #arme du monstre
        if mob.weapon:
            self.get_group().add(mob.weapon, layer=1) #ajout de l'arme du mob au groupe de calques
        
        #tir du monstre
        if mob_info[3]:
            mob.update()
            mob.shoot()

    def check_p2_room(self):
        self.p2_current_room = None

        for room in self.get_map().rooms:
            if self.p2.feet.colliderect(room.rect):
                self.p2_current_room = room
                break #current_room trouvée

    def update(self):
        """Met à jour le groupe de calques des collisions"""

        self.get_group().update() #appel la méthode update de tous les sprites du groupe
        self.check_collisions() #gère les collisions sur la carte
        self.check_p2_room() #met l'information de la pièce du joueur 2 à jour