
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.KEYUP:
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
        # Aufrufen der Elternmethode:
        super().schedule()
        
        # Tastaturauswertung für Spielerbewegung:
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[ pygame.K_LEFT ]:
            self.player.moveby( -2, 0 )
        if keys_pressed[ pygame.K_RIGHT ]:
            self.player.moveby( 2, 0 )
        if keys_pressed[ pygame.K_UP ]:
            self.player.moveby( 0, -2 )
        if keys_pressed[ pygame.K_DOWN ]:
            self.player.moveby( 0, 2 )
    
    
        # Update Methode aller Sprites in allen Gruppen aufrufen:
        # ( Neue Position wird berechnet )
        for spritegroup in self.spritegroups.values():
            spritegroup.update()
        
        # Hintergrund aufs Gamedisplay kopieren
        self.game_display.blit(self.background_surf, (0,0))
    
        # Objekte darstellen
        for spritegroup in self.spritegroups.values():
            spritegroup.draw( self.game_display )
    
        for sprite in self.spritegroups['player']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
        for sprite in self.spritegroups['npc']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
    
        return self # die aktuelle Szene soll erstmal weiter laufen
    
