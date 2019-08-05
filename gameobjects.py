
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
        self.x = self.rect.x   # float position mit pixelposition initialiseren
        self.y = self.rect.y   # float position mit pixelposition initialisieren
        self.oldx = self.x     # alte float position (für undo) initialisieren
        self.oldy = self.y     # alte float position (für undo) initialisieren
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
    def showmessage(self, message, time):
        self.messageStartTime = pygame.time.get_ticks() # Startzeit der neuen Message merken
        lines = message.split("\n")[:3] # Nachricht in Zeilen aufteilen, die ersten drei Zeilen verwenden
        lines_surf = [ fontss.render(line[:20], True, (0,0,0) ) for line in lines ] # Render ersten 20 zeichen pro Zeile
        max_width = max( [ surface.get_rect().width for surface in lines_surf ] ) # breiteste Zeile bestimmen
        message_surf = pygame.Surface( (max_width, len(lines)*fontss.get_linesize()), pygame.SRCALPHA ) # Alpha Surface für maximalen Platzbedarf erzeugen
        for i in range(0, len(lines_surf)): # traverse over lines index
            message_surf.blit( lines_surf[i], (0, i*fontss.get_linesize() ) ) # Zeilen auf Messagesurface mit Abstand blit
        self.messagedisplay = ( message_surf, time )
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

# Winkel zwischen zwei Vektoren berechnen:
# (Geht logischerweise nur bis 180°, Drehsinn ist egal,
#  Ergebnis ist immer positiv)
def v_diff_ang( vektor1, vektor2 ):
    sp = v_sprod( vektor1, vektor2 )
    winkel = acos( sp / ( v_abs( vektor1 ) * v_abs( vektor2 ) ) )
    return winkel

# winkel eines Vektors:
# (winkel zwischen Vektor und positiver x-Achse)
# tangens ist hier blöd wegen Definitionslücke
# Ergebnis immer positiv, max. 180°
def v_ang( vektor ):
    return acos( vektor[0] / v_abs( vektor ) )

# vektor an winkel spiegeln:
# Das scheint für 0<= angle <= 180° zu funktionieren
def v_mirror( vektor, angle ):
    x,y = vektor
    xneu = cos(2*angle) * x + sin(2*angle) * y
    yneu = sin(2*angle) * x - cos(2*angle) * y
    return (xneu, yneu)

# Berechnet den Richtungsvektor zweier kollidierender Objekte:
# Vom Zentrum des ersten Objekts zum Zentrum des zweiten
def v_collision( object, obstacle ):
    doc = v_dir( v_center(object.rect), v_center(obstacle.rect) )
    return doc

# Lässt ein Objekt von einer SpriteGruppe abprallen:
def bounce( object, spritegroup ):
    obstacle_list = pygame.sprite.spritecollide( object, spritegroup, False, 
                                pygame.sprite.collide_circle_ratio(0.85))
    
    if obstacle_list == []: # Keine Kollision
        return # dann gleich beenden

    # Wir bearbeiten immer nur das erste Hindernis der Liste
    obstacle = obstacle_list[0]

    # Bestimmung des Richtungsvektors vom Objekt zum Berührpunkt
    direction_of_collision = v_collision( object, obstacle )

    # Falls die Objektzentren genau aufeinanderliegen:
    if direction_of_collision == (0,0):
        print( "Objekte deckungsgleich!")
        return

    # Falls sich die Objekte berühren, aber sich voneinander entfernen
    # oder aneinander vorbeigleiten (skalarprodukt <= 0):
    if v_sprod( direction_of_collision, (object.speedx, object.speedy) ) <= 0:
        print( "Objekte entfernen sich schon!")
        return
    
    # Winkel der Spiegelachse ermitteln:
    mirror_angle = v_ang ( v_ortho( direction_of_collision ) )
    # Bewegungsvektor spiegeln:
    object.speedx, object.speedy = v_mirror( (object.speedx, object.speedy), mirror_angle )

    print( "doc: {0}, speedx: {1}, speedy: {2}, angle: {3}".format(
    direction_of_collision, object.speedx, object.speedy, mirror_angle/2/pi*360) )

    # Letzte Bewegung rückgängig machen
    object.undo()
    # Falls sich die Objekte trotz rückgängig gemachter letzer Bewegung noch
    # berühren:
    while pygame.sprite.spritecollide( object, [obstacle], False, 
                                pygame.sprite.collide_circle_ratio(0.85)):
        print( "Rettungsvesuch" )
        object.update()

