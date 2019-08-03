
import pygame
import pytmx

from math import sqrt

# Invent a moveable Game Character:
#
# image: surface welche die Grafik des Characters enthält
# x,y : Startposition
# speedx, speedy : Geschwindigkeit in pixel pro frame. (Kann aber auch float sein!)
#
# self.x/y enthält die Position ggf. in float (eigentlich nur für intern)
# self.rect enthält die Pixelposition und Dimension
#
class Character(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speedx, speedy):
        pygame.sprite.Sprite.__init__(self)        # Call the parent class (Sprite) constructor
        self.image = image
        self.rect = self.image.get_rect() # rectgröße ermitteln
        self.rect.topleft = (x,y)         # startposition setzen
        self.speedx = speedx   # kann float sein!
        self.speedy = speedy   # kann float sein!
        self.x = self.rect.x   # float position mit pixelposition initialiseren
        self.y = self.rect.y   # float position mit pixelposition initialisieren
        self.oldx = self.x     # alte float position (für undo) initialisieren
        self.oldy = self.y     # alte float position (für undo) initialisieren
        self.messagequeue = []
        self.messagedisplay = None
    def update(self): # Neue Position aufgrund der gesetzten Geschwindigkeit ermitteln
        # Nur für Objekte mit Geschwindigkeit ausführen:
        if self.speedx !=0 or self.speedy != 0:
            self.oldx = self.x
            self.oldy = self.y
            self.x = self.x + self.speedx
            self.y = self.y + self.speedy
            self.rect.x = int(self.x)  # neue pixelposition
            self.rect.y = int(self.y)
    def undo(self):          # Letzte Bewegung rückgängig machen
        self.x = self.oldx
        self.y = self.oldy
        self.rect.x = int(self.x)  # neue pixelposition
        self.rect.y = int(self.y)
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
                x = min(surface.get_rect().width - self.messagedisplay[0].get_rect().width - 2, max(2, x)) # clamp to border
                y = min(surface.get_rect().height - self.messagedisplay[0].get_rect().height - 2, max(2, y)) # clamp to border
                surface.blit( self.messagedisplay[0], (x,y) ) # auf die angegebene Surface kopieren
        # Neue Nachricht zur Ausgabe vorbereiten:
        elif len( self.messagequeue ) > 0: # Noch Nachrichten in der Queue?
            fontss = pygame.font.SysFont('Arial',15)
            self.messageStartTime = pygame.time.get_ticks() # Startzeit der neuen Message merken
            message = self.messagequeue.pop() # Oberste Nachricht aus der Queue holen (string, time)
            lines = message[0].split("\n")[:3] # Nachricht in Zeilen aufteilen, die ersten drei Zeilen verwenden
            lines_surf = [ fontss.render(line[:20], True, (0,0,0) ) for line in lines ] # Render ersten 20 zeichen pro Zeile
            message_surf = pygame.Surface( (300, 50), pygame.SRCALPHA ) # Alpha Surface für maximalen Platzbedarf erzeugen
            for i in range(0, len(lines_surf)): # traverse over lines index
                message_surf.blit( lines_surf[i], (0, i*fontss.get_linesize() ) ) # Zeilen auf Messagesurface mit Abstand blit
            self.messagedisplay = ( message_surf.subsurface( message_surf.get_bounding_rect() ), message[1] ) # Zuschneiden


# Diese Funktion erzeugt aus einer Tiled Map und einem Objektnamen
# einen (moveable) Character:
def object2character( tmx_map, objectname ):
    object = tmx_map.get_object_by_name( objectname )
    return Character( object.image, object.x, object.y, 0, 0 )

####################### Unbewegliche Objekte #####################################

# Entsprechend der Character Klasse, wird hier eine Spriteklasse
# erzeugt, welche aber nicht für bewegliche Objekte vorgesehen ist:
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
# Diese Funktion erzeugt aus einer Tiled Map und einem Objektnamen
# ein unbewegliches Tile:
def object2tile( tmx_map, objectname ):
    object = tmx_map.get_object_by_name( objectname )
    return Tile( object.image, object.x, object.y )

# Diese Funktion erzeugt aus einer Tiled Map und einem Layernamen
# eine Spritegruppe unbeweglicher Tiles:
def layer2tilegroup( tmx_map, layername ):
    spritegroup = pygame.sprite.Group() # Neues Spritegroup Layer erzeugen
    tilewidth = tmx_map.tilewidth
    tileheight = tmx_map.tileheight
    for x, y, image in tmx_map.get_layer_by_name( layername ).tiles():
        spritegroup.add( Tile( image, x*tilewidth, y*tileheight ) )
    return spritegroup
                        
###################### Geometrie ###########################################

# Berechnet das Zentrum eines Rects:
def v_center( rect ):
    x = rect.x + rect.width / 2
    y = rect.y + rect.height / 2
    return ( x, y )

# Berechnet den Richtungsvektor zwischen zwei Ortsvektoren:
def v_dir( ov1, ov2 ):
    ov1x, ov1y = ov1
    ov2x, ov2y = ov2
    x = ov2x - ov1x
    y = ov2y - ov1y
    return ( x, y )

# Berechnet den Richtungsvektor zweier kollidierender Objekte:
# Vom Zentrum des ersten Objekts zum Zentrum des Collisionrects
def v_collision( obj1, obj2 ):
    intersection = obj1.rect.clip( obj2.rect )
    return v_dir( v_center(obj1.rect), v_center(intersection) )

# Senkrechten Vektor berechnen:
# entspricht: ( 0  -1 )
#             ( 1  0  )
def v_ortho( vektor ):
    x,y = vektor
    return ( -y, x )

# Einheitsvektor berechnen:
def v_norm( vektor ):
    x,y = vektor
    laenge = sqrt( x*x + y*y )
    x = x / laenge
    y = y / laenge
    return ( x,y )

# Vektor an Vektor spiegeln
# entspricht: ( mx   my ) * ( vx )
#             ( my   -mx )   ( vy )
def v_mirror( v_mirror, vektor ):
    mx, my = v_mirror
    x, y = vektor
    x = mx * x + my * y
    y = my * x + -mx * y
    return ( x, y )

# Lässt ein Objekt am anderen abprallen:
def bounce( object, hindernis ):
    direction_of_collision = v_collision( object, hindernis )
    mirror_plane = v_norm( v_ortho( direction_of_collision ) )
    newspeedx, newspeedy = v_mirror( mirror_plane, (object.speedx, object.speedy) )
    object.speedx = newspeedx
    object.speedy = newspeedy


    