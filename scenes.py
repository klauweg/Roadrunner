
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from character import Character

# Load the Maps:
# Das funktioniert erst nach dem Game Display init (wegen Videomode)
level1_map = load_pygame("Level1.tmx")

# Base Class:
class Scene(object):
    def __init__( self, game_display ):
        self.game_display = game_display
    def schedule( self ):
        pass

class Level1( Scene ):
    def __init__( self, game_display ):
        super().__init__( game_display )
        self.lastkey = None
        
        # create background surface aus der Tilemap
        self.background_surf = pygame.Surface((20*32, 20*32))
        for x, y, gid in level1_map.get_layer_by_name("Kachelebene"):
            image = level1_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
            self.background_surf.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren

        # create sprite groups aus der Tilemap
        self.spritegroups={}
        for objectgroup in level1_map.objectgroups:
            self.spritegroups[objectgroup.name]=pygame.sprite.Group()
            for object in objectgroup:
                self.spritegroups[objectgroup.name].add( Character( object.image, object.x, object.y, 0, 0 ) )

        # generate some Characters:
        self.spritegroups['npc'] = pygame.sprite.Group()
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 164,0,0 ) )
        self.npc1 = Character( player_surf, 75, 10, 0.5, 0.5 )
        self.npc1.queuemessage("ich bin\nnpc1", 20000)
        self.npc2 = Character( player_surf, 400, 30, 0.2, 0.1 )
        self.npc2.queuemessage("ich bin\nnpc2", 22000)
        self.npc3 = Character( player_surf, 100, 30, -0.2, 0.1 )
        self.npc3.queuemessage("ich bin\nnpc3", 24000)
        self.npc4 = Character( player_surf, 400, 300, -0.2, -0.1 )
        self.npc4.queuemessage("ich bin\nnpc4",26000)
        self.spritegroups['npc'].add( self.npc1 )
        self.spritegroups['npc'].add( self.npc2 )
        self.spritegroups['npc'].add( self.npc3 )
        self.spritegroups['npc'].add( self.npc4 )

        # The Player himself:
        self.spritegroups['player'] = pygame.sprite.Group()
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 0,164,200 ) )
        self.player = Character( player_surf, 400, 400, 0, 0 )
        self.player.queuemessage("hallo\n2.zeile",5000)
        self.player.queuemessage("2. nachricht",15000)
        self.player.queuemessage("3. nachricht",15000)
        self.spritegroups['player'].add( self.player )
    
    def schedule( self ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                self.lastkey = event.key
            if event.type == pygame.KEYUP:
                self.lastkey = None

        # Tasten verarbeiten:
        if self.lastkey == pygame.K_ESCAPE:
            pygame.quit()
            quit()
        elif self.lastkey == pygame.K_LEFT:
            self.player.moveby( -2, 0 )
        elif self.lastkey == pygame.K_RIGHT:
            self.player.moveby( 2, 0 )
        elif self.lastkey == pygame.K_DOWN:
            self.player.moveby( 0, 2 )
        elif self.lastkey == pygame.K_UP:
            self.player.moveby( 0, -2 )

    
        for spritegroup in self.spritegroups.values():
            spritegroup.update()
        
        self.game_display.blit(self.background_surf, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    
        for spritegroup in self.spritegroups.values():  # Objekte darstellen
            spritegroup.draw( self.game_display )
    
        for sprite in self.spritegroups['player']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
        for sprite in self.spritegroups['npc']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
    
        return self # die aktuelle Szene soll erstmal weiter laufen
    
