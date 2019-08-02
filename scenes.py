import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import random
import numpy
from numpy.linalg import norm

import character
import tile


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

        self.map_scene = load_pygame("Maps/Level1.tmx") # load data with Surfaces
        
        self.group_background = tile.layer2spritegroup( self.map_scene, "Grasebene")
        self.group_mauern = tile.layer2spritegroup( self.map_scene, "Mauerebene")

        # create sprite groups aus der Tilemap
        self.spritegroups={}
        for objectgroup in self.map_scene.objectgroups:
            self.spritegroups[objectgroup.name]=pygame.sprite.Group()
            for object in objectgroup:
                self.spritegroups[objectgroup.name].add( character.Character( object.image, object.x, object.y, 0, 0 ) )

        # funktion zur Erstellung eines zufälligen NPC Characters:
        def generate_random_npc():
            npc_surf=pygame.Surface( (16,16) )
            npc_surf.fill( pygame.Color( 164,0,0 ) )
            x = random.randint( 30, self.game_display.get_rect().width - 30)
            y = random.randint( 30, self.game_display.get_rect().height - 30)
            speedx = (random.random()-0.5) * 6 
            speedy = (random.random()-0.5) * 6
            return character.Character( npc_surf, x, y, speedx, speedy )

        # Erzeugen der NPCs:
        self.spritegroups['npc'] = pygame.sprite.Group()
        for npc in range( 1, 40):
            npc_character = generate_random_npc()
            npc_character.queuemessage("Ich bin\nNPC " + str(npc), 1500 )
            self.spritegroups['npc'].add( npc_character )

        # The Player himself:
        self.spritegroups['player'] = pygame.sprite.Group()
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 0,164,200 ) )
        self.player = character.Character( player_surf, 400, 400, 0, 0 )
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
        hit_list = pygame.sprite.spritecollide( self.player, self.spritegroups['npc'],
                                               False, pygame.sprite.collide_circle_ratio(1.5))
        for hit in hit_list:
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
            
            hit.undo()


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
                
        self.group_background.draw( self.game_display )
        self.group_mauern.draw( self.game_display )
        
        # Objekte darstellen
        for spritegroup in self.spritegroups.values():
            spritegroup.draw( self.game_display )
    
        for sprite in self.spritegroups['player']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
        for sprite in self.spritegroups['npc']:    # Nachrichten ausgeben
            sprite.drawmessage( self.game_display )
    
        return self # die aktuelle Szene soll erstmal weiter laufen
    
