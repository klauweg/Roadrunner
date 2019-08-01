import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import random

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

        # funktion zur Erstellung eines zufälligen NPC Characters:
        def generate_random_npc():
            npc_surf=pygame.Surface( (16,16) )
            npc_surf.fill( pygame.Color( 164,0,0 ) )
            x = random.randint( 30, self.game_display.get_rect().width - 30)
            y = random.randint( 30, self.game_display.get_rect().height - 30)
            speedx = (random.random()-0.5) * 6 
            speedy = (random.random()-0.5) * 6
            return Character( npc_surf, x, y, speedx, speedy )

        # Erzeugen der NPCs:
        self.spritegroups['npc'] = pygame.sprite.Group()
        for npc in range( 1, 10):
            npc_character = generate_random_npc()
            npc_character.queuemessage("Ich bin\nNPC " + str(npc), 1500 )
            self.spritegroups['npc'].add( npc_character )

        # The Player himself:
        self.spritegroups['player'] = pygame.sprite.Group()
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 0,164,200 ) )
        self.player = Character( player_surf, 400, 400, 0, 0 )
        self.player.queuemessage("Ich bin\nder Spieler",5000)
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
        # ( Neue Position anhand der Geschwindigkeit wird berechnet )
        for spritegroup in self.spritegroups.values():
            spritegroup.update()
        
        # Kollisionsverarbeitung:
        hit_list = pygame.sprite.spritecollide( self.player, self.spritegroups['npc'], False)
        for hit in hit_list:
            print( hit )
            hit.queuemessage("aua!!",200)
        
        # Spielfeldbegrenzung:
        for sprite in self.spritegroups['player']:
            if not self.game_display.get_rect().contains( sprite.rect ):
                sprite.undo()
        
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
    
