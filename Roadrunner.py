
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode((640, 640))
pytmx_map = load_pygame("Fertigtest.tmx") 

# invent a moveable Game Character:
class Character(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speedx, speedy):
        pygame.sprite.Sprite.__init__(self)        # Call the parent class (Sprite) constructor
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.speedx = speedx
        self.speedy = speedy
        self.x = self.rect.x
        self.y = self.rect.y
        self.oldx = self.x
        self.oldy = self.y
    def update(self):
        if self.x !=0 or self.y != 0:
            self.oldx = self.x
            self.oldy = self.y
            self.x = self.x + self.speedx
            self.y = self.y + self.speedy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    def moveby(self, x, y):
        self.oldx = self.x
        self.oldy = self.y
        self.x = self.x + x
        self.y = self.y + y
    def undo(self):
        self.x = self.oldx
        self.y = self.oldy
    def draw(self, surface):
        surface.blit( self.image, self.rect )
    def textwrite(self,message,color):
        text = fontss.render(message, True, color)
        textpos = pygame.font.Font.size(fontss, message)
        game_display.blit(text,(self.x-textpos[0]/2+8,self.y-40))
        pygame.time.set_timer(2, 1000)

# create background surface
background_surf = pygame.Surface((20*32, 20*32))
for x, y, gid in pytmx_map.get_layer_by_name("Kachelebene"):
    image = pytmx_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
    background_surf.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren

# create sprite groups
spritegroups={}
for objectgroup in pytmx_map.objectgroups:
    spritegroups[objectgroup.name]=pygame.sprite.Group()
    for object in objectgroup:
        spritegroups[objectgroup.name].add( Character( object.image, object.x, object.y, 0, 0 ) )


spritegroups['npc'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 164,0,0 ) )
spritegroups['npc'].add( Character( player_surf, 75, 10, 0.5, 0.5 ) )
spritegroups['npc'].add( Character( player_surf, 400, 30, 0.2, 0.1 ) )
spritegroups['npc'].add( Character( player_surf, 1, 30, 0.4, 0.3 ) )

spritegroups['player'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 0,164,200 ) )
player = Character( player_surf, 300, 400, 0, 0 )
spritegroups['player'].add( player )



loop = True
event = None
lastkey = None

fontl = pygame.font.SysFont('Comic Sans MS',60)
fonts = pygame.font.SysFont('Comic Sans MS',20)
fontss = pygame.font.SysFont('Arial',15)


leavetrack = True





while(loop):
    # Bearbeiten der Message Queue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            lastkey = event.key
        if event.type == pygame.KEYUP:
            lastkey = None
        if event.type == pygame.USEREVENT:
            playermessage = ""
            pygame.time.set_timer(pygame.USEREVENT, 0)
    
    # Tasten verarbeiten:
    if lastkey == pygame.K_ESCAPE:
        pygame.quit()
        quit()
    elif lastkey == pygame.K_LEFT:
        player.moveby( -2, 0 )
    elif lastkey == pygame.K_RIGHT:
        player.moveby( 2, 0 )
    elif lastkey == pygame.K_DOWN:
        player.moveby( 0, 2 )
    elif lastkey == pygame.K_UP:
        player.moveby( 0, -2 )


        
                
#    if playerground.name != "weg":
#        if leavetrack:
#            leavetrack = False
#            playermessage = "Wenn du den Weg verlässt kannst du Monster töten"
#            pygame.time.set_timer(pygame.USEREVENT, 1000)
#    else:
#        leavetrack = True
        
#    if playerground.name == "cancleway":
#        playermask = pygame.mask.from_surface(boot)
#        tilemask = pygame.mask.from_surface(object.image)
#        if (playermask.overlap( tilemask, ( 0,0 )) != None):
#            bootpos = oldbootpos
#        
#    if bootpos.x < 0 or bootpos.x > 640-32 or bootpos.y < 0 or bootpos.y > 640-32:
#        bootpos = oldbootpos
#        playermessage = "Die Map ist hier zu Ende."
        
    game_display.blit(background_surf, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    
    
    for spritegroup in spritegroups.values():
        spritegroup.update()
        
    for spritegroup in spritegroups.values():
        spritegroup.draw( game_display )
    
    player.textwrite("lol",(255,255,255))
    
#    textwrite( bootpos.x+16, bootpos.y-32,playermessage, (0, 0, 0) , fonts)
    
    pygame.time.Clock().tick(70)
    pygame.display.update()