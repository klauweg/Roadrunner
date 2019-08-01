import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import random
import numpy
from numpy.linalg import norm

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
        for npc in range( 1, 3800):
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
        
        # Kollisionsverarbeitung npc -> Spieler:
        hit_list = pygame.sprite.spritecollide( self.player, self.spritegroups['npc'], False)
        for hit in hit_list:
            hit.undo()
            # Richtungsvektor zum Player
            r_player = numpy.array(
              [ (self.player.x + self.player.rect.width/2) - ( hit.x + hit.rect.width / 2 ),
                (self.player.y + self.player.rect.height/2) - ( hit.y + hit.rect.height / 2 ) ]
                          )
            # Senkrechte:
            m_rot = numpy.array( [ [0,1], [-1,0] ] )
            v_mirror = numpy.matmul( m_rot, r_player )

            # Einheitsvektor der Spiegelachse
            v_mirror = v_mirror/norm(v_mirror)
            
            # Spiegelmatrix bauen:
            m_mirror = numpy.array( [  [ v_mirror[0], v_mirror[1] ], [ v_mirror[1], -v_mirror[0] ] ] )
            # Geschwindigkeitsvektor des npc:
            v_npc = numpy.array( [ hit.speedx, hit.speedy ] )
            
            # Neuen geschwindigkeitsvektor:
            vneu_npc = numpy.matmul( m_mirror, v_npc )
            
            # Neue geschwindigkeit setzen:
            hit.speedx = vneu_npc[0]
            hit.speedy = vneu_npc[1]
        
            hit.queuemessage("aua!!",200)
        
        # Spielfeldbegrenzung für Spieler:
        for sprite in self.spritegroups['player']:
            if not self.game_display.get_rect().contains( sprite.rect ):
                sprite.undo()
        
        # Bounce on Wall (Spielfeldbegrenzung für NPC):
        maxx = self.game_display.get_rect().width - 16
        maxy = self.game_display.get_rect().height - 16
        for sprite in self.spritegroups['npc']:
            if sprite.rect.x < 0 or sprite.rect.x > maxx:
                sprite.undo()
                sprite.speedx = -sprite.speedx
            if sprite.rect.y < 0 or sprite.rect.y > maxy:
                sprite.undo()
                sprite.speedy = -sprite.speedy
        
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
    
