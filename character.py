import pygame

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
                x = min(surface.get_rect().width - self.messagedisplay[0].get_rect().width - 2, max(2, x)) # clamp to border
                y = min(surface.get_rect().height - self.messagedisplay[0].get_rect().height - 2, max(2, y)) # clamp to border
                surface.blit( self.messagedisplay[0], (x,y) ) # auf die angegebene Surface kopieren
        # Neue Nachricht zur Ausgabe vorbereiten:
        if len( self.messagequeue ) > 0 and self.messagedisplay == None: # Noch Nachrichten in der Queue und Platz dafür?
            fontss = pygame.font.SysFont('Arial',15)
            self.messageStartTime = pygame.time.get_ticks() # Startzeit der neuen Message merken
            message = self.messagequeue.pop() # Oberste Nachricht aus der Queue holen (string, time)
            lines = message[0].split("\n")[:3] # Nachricht in Zeilen aufteilen, die ersten drei Zeilen verwenden
            lines_surf = [ fontss.render(line[:20], True, (0,0,0) ) for line in lines ] # Render ersten 20 zeichen pro Zeile
            message_surf = pygame.Surface( (300, 50), pygame.SRCALPHA ) # Alpha Surface für maximalen Platzbedarf erzeugen
            for i in range(0, len(lines_surf)): # traverse over lines index
                message_surf.blit( lines_surf[i], (0, i*fontss.get_linesize() ) ) # Zeilen auf Messagesurface mit Abstand blit
            self.messagedisplay = ( message_surf.subsurface( message_surf.get_bounding_rect() ), message[1] ) # Zuschneiden
