from entity import *

class Player(Entity):

    def __init__(self):
        super().__init__("player", 0, 0)

        self.ui_sprite_sheet = pygame.image.load(f"../image/techpack/UI/ui x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

        self.max_pdv = 9 #pdv maximums
        self.pdv = self.max_pdv #pdv effectifs
        self.damage_clock = 0 #laps de temps minimum entre deux dommages consécutifs

        self.get_pdv_images()
        self.get_pdv_image()

        self.crosshair = Crosshair("../image/crosshair.png")
        self.map_manager = None #gestionnaire de carte pour ajuster la position du crosshair en jeu, attribué dans Game.__init__()

        self.weapon_index = 0
        self.weapons = []
        self.take_weapon("ak-47")
        self.take_weapon("ksg")
        self.take_weapon("remington")
        self.take_weapon("pp-bizon")
        self.take_weapon("rocket-launcher")
        self.take_weapon("sniper")
        self.take_weapon("shadow")
        self.take_weapon("x-tech")
        self.take_weapon("ray-gun")
        self.take_weapon("atomus")
        self.weapon = self.weapons[self.weapon_index]

    def change_animation_list(self, direction):
        """
        Change la liste de sprites utilisés en fonction de la direction
        """

        self.direction = direction
        self.image = self.images[self.direction][self.animation_index]


    def change_animation(self):
        """
        Change l'animation du sprite avec le mouvement
        """

        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[self.direction]):
                self.animation_index = 0
            
            self.clock = 0

    def take_weapon(self, name):
        """ramassage d'une arme"""

        weapon = copy.copy(weapons[name]) #copie pour ne pas modifier le catalogue d'armes
        weapon.player = self

        self.weapons.append(weapon)

    def next_weapon(self):
        if self.weapon_index < len(weapons) - 1:
            self.weapon_index += 1
        else:
            self.weapon_index = 0

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def previous_weapon(self):
        if self.weapon_index > 0:
            self.weapon_index -= 1
        else:
            self.weapon_index = len(weapons) - 1

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def shoot(self):
        if not self.weapon.rate_clock:
            shots = self.weapon.shot()
            for shot in shots:
                self.map_manager.get_player_shots().append(shot)
                self.map_manager.get_group().add(shot)
                self.weapon.rate_clock = self.weapon.max_rate_clock

    def update(self):
        if self.pdv > 0:
            self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect
        else:
            exit(0) #game over

    def render_ui(self, screen):
        screen.blit(self.crosshair.image, self.crosshair.rect.topleft) #affichage du crosshair
        screen.blit(self.pdv_image, (100,20)) #affichage de la bar de vie
    
    def get_pdv_image(self):
        self.pdv_image = self.pdv_images[self.pdv] #image de la bar de vie

    def get_pdv_images(self):
        self.pdv_images = self.get_images(self.ui_sprite_sheet, 0, 1, 10)
        for i in range(len(self.pdv_images)):
            self.pdv_images[i] = pygame.transform.scale(self.pdv_images[i], (200,140)) #agrandit la bar de vie

    def take_damage(self):
        if not self.damage_clock:
            self.damage_clock = 60
            self.pdv -= 1
            self.get_pdv_image()

    def handle_damage(self):
        """Effet visuel des dégats et gestion du compteur d'invincibilité temporaire"""

        if self.damage_clock:
                self.damage_clock -= 1

                if self.damage_clock > 40:
                    self.damage_effect(0.35 * ((self.damage_clock - 40)/10))
                
    
    def damage_effect(self, scale):
        GB = min(255, max(0, round(255 * (1-scale))))
        self.map_manager.screen.fill((255, GB, GB), special_flags = pygame.BLEND_MULT)