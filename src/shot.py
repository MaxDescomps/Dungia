import pygame, math

def calc_angle(src_pos:pygame.Vector2, dest_pos:pygame.Vector2) -> float:
    """
    Calcule l'angle entre deux points

    Args:
        src_pos(pygame.Vector2): point de départ
        dest_pos(pygame.Vector2): point d'arrivée

    Returns:
        angle(float): angle en radiant dans l'intervalle [-PI; PI]
    """

    distance = dest_pos - src_pos
    
    return math.atan2(distance.y, distance.x)

class Shot(pygame.sprite.Sprite):
    """Classe d'un tir"""

    def __init__(self, src_pos:tuple[int, int], speed: float, damage: float, angle: float, weapon_name:str="9", oriented:bool=False):
        """
        constructeur de la classe Shot
        
        Args:
            src_pos(tuple[int, int]): position de départ du tir
            speed(float): vitesse du tir
            damage(float): dégats du tir
            angle(float): angle du tir
            weapon_name(str): nom du png de l'arme effectuant le tir
            oriented(bool): indique si le sprite du tir doit être tourné selon sa direction
        """

        super().__init__()

        self.speed = speed

        self.image = pygame.image.load(f"../image/bullets/{weapon_name}.png").convert_alpha()

        # self.image = self.get_image(self.sprite_sheet, 0, 0) #balles du spritesheet
        self.rect = self.image.get_rect()

        #centre la position de départ du tir sur l'arme du joueur
        self.rect.center = src_pos

        #calcul de l'angle de tir
        self.angle = angle
        
        #vitesse de déplacement du tir
        self.speed_x = self.speed * math.cos(self.angle)
        self.speed_y = self.speed * math.sin(self.angle)

        #rotation de l'image du tir en fonction de l'angle (optionnel si balle circulaire)
        if oriented:
            self.rotate_img()

        #calcul du rectangle de collision plus précis
        self.colliderect = pygame.Rect(0, 0, 8, 8)
        self.colliderect.center = self.rect.center

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.pos = [None, None]
        self.pos[0] = self.rect[0]
        self.pos[1] = self.rect[1]

        #dommages infligés par le tir
        self.damage = damage

    def update(self):
        """met la position du tir à jour"""
        
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

        #maj du rectangle d'affichage
        self.rect.topleft = self.pos
        
        #maj du rectangle de collision
        self.colliderect.center = self.rect.center

    def rotate_img(self):
        """fait une rotation de l'image du tir en fonction de son angle"""

        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.angle)).convert_alpha() #rotation de l'image

        self.rect = rotated_image.get_rect(center = self.rect.center) #on corrige la modification du centre de l'image causé par le changement de son rectangle après rotation

        self.image = rotated_image

class CurveShot(Shot):
    """Classe d'un tir téléguidé"""

    def __init__(self, modif_angle:float, max_angle:float, max_modif_clock:int, src_pos:tuple[int, int], speed: float, damage: float, angle: float, weapon_name:str="0", oriented:bool=False):
        """
        constructeur de la classe Shot
        
        Args:
            modif_angle(float): valeur ajoutée à l'angle du tir à chaque modification
            max_angle(float): valeur maximum de l'angle modifié
            max_modif_clock(int): décompte avant chaque modification de l'angle
            src_pos(tuple[int, int]): position de départ du tir
            speed(float): vitesse du tir
            damage(float): dégats du tir
            angle(float): angle du tir
            weapon_name(str): nom du png de l'arme effectuant le tir
            oriented(bool): indique si le sprite du tir doit être tourné selon sa direction
        """

        super().__init__(src_pos, speed, damage, angle, weapon_name, oriented)

        self.base_angle = angle
        self.max_angle = max_angle
        self.modif_angle = modif_angle
        self.added_angle = 0 #somme des modifications sur l'angle
        self.max_modif_clock = max_modif_clock
        self.modif_clock = self.max_modif_clock

        if self.modif_angle < 0:
            self.angle_sign = -1
        else:
            self.angle_sign = 1
    
    def update(self):
        """met la position du tir à jour"""

        if self.added_angle * self.angle_sign < self.max_angle and self.modif_clock <= 0:

            self.added_angle += self.modif_angle
            
            #vitesse de déplacement du tir
            self.speed_x = self.speed * math.cos(self.angle + self.added_angle)
            self.speed_y = self.speed * math.sin(self.angle + self.added_angle)

            #calcul du rectangle de collision plus précis
            self.colliderect.center = self.rect.center

            #remise en route du compteur
            self.modif_clock += self.max_modif_clock
        else:
            self.modif_clock -= 1
        
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

        #maj du rectangle d'affichage
        self.rect.topleft = self.pos
        
        #maj du rectangle de collision
        self.colliderect.center = self.rect.center