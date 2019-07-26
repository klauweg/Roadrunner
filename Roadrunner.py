
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


# initialize pygame
pygame.init()

game_dimensions = (640,640)
# create game display
game_display = pygame.display.set_mode( game_dimensions )
pytmx_map = load_pygame("Fertigtest.tmx") 

# Define Fonts:
fontl = pygame.font.SysFont('Comic Sans MS',60)
fonts = pygame.font.SysFont('Comic Sans MS',20)
fontss = pygame.font.SysFont('Arial',15)

# Invent a moveable Game Character:
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
        self.messagequeue = []
        self.messagedisplay = None
    def update(self): # Neue Position aufgrund der gesetzten Geschwindigkeit ermitteln
        if self.x !=0 or self.y != 0:
            self.oldx = self.x
            self.oldy = self.y
            self.x = self.x + self.speedx
            self.y = self.y + self.speedy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    def moveby(self, x, y): # Um einen bestimmten Vektor verschieben
        self.oldx = self.x
        self.oldy = self.y
        self.x = self.x + x
        self.y = self.y + y
    def undo(self):          # Letzte Bewegung rückgängig machen
        self.x = self.oldx
        self.y = self.oldy
    def queuemessage(self, message, time):  # Anzuzeigende Message in der Queue speichern
        self.messagequeue.insert( 0, ( message, time ) )
    def drawmessage( self, surface ):      # Per Frame aufrufen um die Messages auszugeben
        # Aktuelle Nachricht bearbeiten:
        if self.messagedisplay != None:  # Wird gerade eine Nachricht angezeigt?
            if pygame.time.get_ticks() > self.messageStartTime + self.messagedisplay[1]: # Displayzeit abgelaufen?
                self.messagedisplay = None  # Dann Nachricht löschen
            else:
                # Ausgabe der Nachricht:
                x = self.rect.x + self.rect.width/2 - self.messagedisplay[0].get_rect().width/2 # mittelzentriert
                y = self.rect.y - self.messagedisplay[0].get_rect().height - 5 # texthöhe berücksichtigen
                x = min(game_dimensions[0] - self.messagedisplay[0].get_rect().width - 2, max(2, x)) # clamp to border
                y = min(game_dimensions[1] - self.messagedisplay[0].get_rect().height - 2, max(2, y)) # clamp to border
                surface.blit( self.messagedisplay[0], (x,y) ) # auf die angegebene Surface kopieren
        # Neue Nachricht zur Ausgabe vorbereiten:
        if len( self.messagequeue ) > 0 and self.messagedisplay == None: # Noch Nachrichten in der Queue und Platz dafür?
            self.messageStartTime = pygame.time.get_ticks() # Startzeit der neuen Message merken
            message = self.messagequeue.pop() # Oberste Nachricht aus der Queue holen (string, time)
            lines = message[0].split("\n")[:3] # Nachricht in Zeilen aufteilen, die ersten drei Zeilen verwenden
            lines_surf = [ fontss.render(line[:20], True, (0,0,0) ) for line in lines ] # Render ersten 20 zeichen pro Zeile
            message_surf = pygame.Surface( (300, 50), pygame.SRCALPHA ) # Alpha Surface für maximalen Platzbedarf erzeugen
            for i in range(0, len(lines_surf)): # traverse over lines index
                message_surf.blit( lines_surf[i], (0, i*fontss.get_linesize() ) ) # Zeilen auf Messagesurface mit Abstand blit
            self.messagedisplay = ( message_surf.subsurface( message_surf.get_bounding_rect() ), message[1] ) # Zuschneiden


# create background surface aus der Tilemap
background_surf = pygame.Surface((20*32, 20*32))
for x, y, gid in pytmx_map.get_layer_by_name("Kachelebene"):
    image = pytmx_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
    background_surf.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren

# create sprite groups aus der Tilemap
spritegroups={}
for objectgroup in pytmx_map.objectgroups:
    spritegroups[objectgroup.name]=pygame.sprite.Group()
    for object in objectgroup:
        spritegroups[objectgroup.name].add( Character( object.image, object.x, object.y, 0, 0 ) )


spritegroups['npc'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 164,0,0 ) )
npc1 = Character( player_surf, 75, 10, 0.5, 0.5 )
npc1.queuemessage("ich bin\nnpc1", 20000)
npc2 = Character( player_surf, 400, 30, 0.2, 0.1 )
npc2.queuemessage("ich bin\nnpc2", 22000)
npc3 = Character( player_surf, 100, 30, -0.2, 0.1 )
npc3.queuemessage("ich bin\nnpc3", 24000)
npc4 = Character( player_surf, 400, 300, -0.2, -0.1 )
npc4.queuemessage("ich bin\nnpc4",26000)
spritegroups['npc'].add( npc1 )
spritegroups['npc'].add( npc2 )
spritegroups['npc'].add( npc3 )
spritegroups['npc'].add( npc4 )

spritegroups['player'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 0,164,200 ) )
player = Character( player_surf, 400, 400, 0, 0 )
player.queuemessage("Hallo ich bin Felix\nich werde dich durch\ndieses Game führen!",3000)
player.queuemessage("Am besten du erkundest\nerst ein mal alles",2000)
player.queuemessage("Viel Spaß",1000)
spritegroups['player'].add( player )



loop = True
event = None
lastkey = None
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
        
    
    for spritegroup in spritegroups.values():
        spritegroup.update()
        
    game_display.blit(background_surf, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    
    for spritegroup in spritegroups.values():  # Objekte darstellen
        spritegroup.draw( game_display )
    
    for sprite in spritegroups['player']:    # Nachrichten ausgeben
        sprite.drawmessage( game_display )
    for sprite in spritegroups['npc']:    # Nachrichten ausgeben
        sprite.drawmessage( game_display )
    
    
    pygame.time.Clock().tick(70)
    pygame.display.update()
