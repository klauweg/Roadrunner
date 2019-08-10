
import pygame
import pytmx

from math import sqrt, acos, pi, atan, sin, cos, tan

try:
    fontss = pygame.font.SysFont('Arial',15)
except:
    pass

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
        self.x = x   # float position mit pixelposition initialiseren
        self.y = y   # float position mit pixelposition initialisieren
        self.messagedisplay = None
        
    def update(self): # Neue Position aufgrund der gesetzten Geschwindigkeit ermitteln
        # Nur für Objekte mit Geschwindigkeit ausführen:
        if self.speedx !=0 or self.speedy != 0:
            self.x = self.x + self.speedx
            self.y = self.y + self.speedy
            self.rect.x = int(self.x)  # neue pixelposition
            self.rect.y = int(self.y)
            
    def showmessage(self, message, time):
        self.messageStartTime = pygame.time.get_ticks() # Startzeit der neuen Message merken
        linesize = fontss.get_linesize()
        textlines = message.split("\n")[:3] # Nachricht in Zeilen aufteilen, die ersten drei Zeilen verwenden
        surfacelines = [ fontss.render(line[:20], True, (0,0,0) ) for line in textlines ] # Render ersten 20 zeichen pro Zeile
        max_width = max( [ surface.get_rect().width for surface in surfacelines ] ) # breiteste Zeile bestimmen
        messagesurface = pygame.Surface( (max_width, len(textlines)*linesize), pygame.SRCALPHA ) # Alpha Surface für maximalen Platzbedarf erzeugen
        for i,surfaceline in enumerate( surfacelines ):
            messagesurface.blit( surfaceline, (0, i*linesize ) ) # Zeilen auf Messagesurface mit Abstand blit
        self.messagedisplay = ( messagesurface, time )
        
    def drawmessage( self, surface ):      # Per Frame aufrufen um die Messages auszugeben
        # Aktuelle Nachricht bearbeiten:
        if self.messagedisplay != None:  # Wird gerade eine Nachricht angezeigt?
            if pygame.time.get_ticks() > self.messageStartTime + self.messagedisplay[1]: # Displayzeit abgelaufen?
                self.messagedisplay = None  # Dann Nachricht löschen
            else:
                # Ausgabe der Nachricht:
                x = self.rect.x + self.rect.width/2 - self.messagedisplay[0].get_rect().width/2 # mittelzentriert
                y = self.rect.y - self.messagedisplay[0].get_rect().height # texthöhe berücksichtigen
                x = min(surface.get_rect().width - self.messagedisplay[0].get_rect().width - 2, max(2, x)) # clamp to border
                y = min(surface.get_rect().height - self.messagedisplay[0].get_rect().height - 2, max(2, y)) # clamp to border
                surface.blit( self.messagedisplay[0], (x,y) ) # auf die angegebene Surface kopieren

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


# Berechnet den Richtungsvektor zwischen zwei Ortsvektoren:
def v_dir( ov1, ov2 ):
    ov1x, ov1y = ov1
    ov2x, ov2y = ov2
    x = ov2x - ov1x
    y = ov2y - ov1y
    return ( x, y )

# Senkrechten Vektor berechnen:
# entspricht: ( 0  -1 )
#             ( 1  0  )
def v_ortho( vektor ):
    x,y = vektor
    return ( -y, x )

# Betrag eines Vektors berechnen:
def v_abs( vektor ):
    x,y = vektor
    return sqrt( x*x + y*y )

# Einheitsvektor berechnen:
def v_norm( vektor ):
    x,y = vektor
    laenge = v_abs( vektor )
    x = x / laenge
    y = y / laenge
    return ( x,y )

# Skalarprodukt zwischen zwei Vektoren:
def v_sprod( vektor1, vektor2 ):
    ax, ay = vektor1
    bx, by = vektor2
    sp = ax*bx + ay*by # Skalarprodukt
    return sp

# winkel eines Vektors:
# (winkel zwischen Vektor und positiver x-Achse)
# tangens ist hier blöd wegen Definitionslücke
# so geht es für 0 <= alpha <=180°
def v_ang( vektor ):
    x,y = vektor
    # Für den 3. und 4. Quadranten punktspiegeln wir das in den
    # 1. und 2., damit die Winkelberechnung mit acos auch für
    # Vektorwinkel >180° geht. Für die spätere Spiegelachse
    # ist es egal.
    if y < 0:
        x = -x
        y = -y
    return acos( x / v_abs( vektor ) )

# vektor an winkel spiegeln:
# Das scheint für 0<= angle <= 180° zu funktionieren
def v_mirror( vektor, angle ):
    x,y = vektor
    xneu = cos(2*angle) * x + sin(2*angle) * y
    yneu = sin(2*angle) * x - cos(2*angle) * y
    return (xneu, yneu)


# Lässt ein Objekt von einer SpriteGruppe abprallen:
# gibt False zurück, wenn keine Kollision stattgefunden hat
def bounce( object, spritegroup, debug=False, debug1=False ):
    collision = False
    obstacle_list = pygame.sprite.spritecollide( object, spritegroup, False ) 
    
    if obstacle_list == []: # Keine Kollision
        return collision # dann gleich beenden

    collision = True
    for obstacle in obstacle_list:

        # Bestimmung des Richtungsvektors vom Objekt zum Hindernis:
        doc_v = v_dir( object.rect.center, obstacle.rect.center )

        # Falls die Objektzentren genau aufeinanderliegen:
        if doc_v == (0,0):
            if debug:
                print( "Objekte deckungsgleich!")
            continue

        # Falls sich die Objekte berühren, aber sich voneinander entfernen
        # oder aneinander vorbeigleiten (skalarprodukt <= 0):
        if v_sprod( doc_v, (object.speedx, object.speedy) ) <= 0:
            if debug1:
                print( "Objekte entfernen sich schon!")
            continue

        if debug:
            print( "doc: {0}, speedx: {1}, speedy: {2}, x:{3}, y:{4}".format(
                    doc_v, object.speedx, object.speedy, object.x, object.y ) )

        # Winkel der Spiegelachse ermitteln:
        mirror_angle = v_ang ( v_ortho( doc_v ) )
        # Bewegungsvektor spiegeln:
        object.speedx, object.speedy = v_mirror( (object.speedx, object.speedy), mirror_angle )

        if debug:
            print( "doc: {0}, speedx: {1}, speedy: {2}, x:{3}, y:{4}, angle:{5}".format(
                   doc_v, object.speedx, object.speedy, object.x, object.y, mirror_angle/2/pi*360) )
            print( "" )
            
    return collision

