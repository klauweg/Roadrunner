import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import random

from gameobjects import *


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
            
        player_speed = 2
        # Tastaturauswertung für Spielerbewegung:
        keys_pressed = pygame.key.get_pressed()
        self.movex = 0
        self.movey = 0
        if keys_pressed[ pygame.K_LEFT ]:
            self.movex = self.movex - player_speed
        if keys_pressed[ pygame.K_RIGHT ]:
            self.movex = self.movex + player_speed
        if keys_pressed[ pygame.K_UP ]:
            self.movey = self.movey - player_speed
        if keys_pressed[ pygame.K_DOWN ]:
            self.movey = self.movey + player_speed

############################### Level 1 ##########################

class Level1( Scene ):
    def __init__( self, game_display ):
        super().__init__( game_display )

        self.map_scene = load_pygame("Maps/Level1.tmx") # load data with Surfaces
        
        self.group_background = layer2tilegroup( self.map_scene, "Grasebene")
        self.group_mauern = layer2tilegroup( self.map_scene, "Mauerebene")

        self.group_inout = pygame.sprite.Group()
        self.tile_ziel = object2tile( self.map_scene, "Ziel" )
        self.tile_start = object2tile( self.map_scene, "Spawn" )
        self.group_inout.add( self.tile_ziel )
        self.group_inout.add( self.tile_start )
        

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
        self.group_npcs = pygame.sprite.Group()
        for npc in range( 1, 40):
            npc_character = generate_random_npc()
            npc_character.queuemessage("Ich bin\nNPC " + str(npc), 1500 )
            self.group_npcs.add( npc_character )

        # The Player himself:
        self.group_player = pygame.sprite.Group()
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 0,164,200 ) )
        self.character_player = Character( player_surf, 400, 400, 0, 0 )
        self.character_player.queuemessage("Ich bin\nder Spieler",5000)
        self.group_player.add( self.character_player )



    def schedule( self ):
        # Aufrufen der Elternmethode:
        super().schedule()
        
        # Player anhand der Tastatursteuerung bewegen:
        self.character_player.moveby( self.movex, self.movey )
    
        # Update Methode aller Sprites in allen Gruppen aufrufen:
        # ( Neue Position anhand der Geschwindigkeit wird berechnet )
        self.group_npcs.update()
        self.group_player.update()

        # Spielfeldbegrenzung für Spieler:
        if not self.game_display.get_rect().contains( self.character_player.rect ):
            self.character_player.undo()



        # Kollisionsverarbeitung npc -> Spieler:
        hit_list = pygame.sprite.spritecollide( self.character_player,
                                               self.group_npcs,
                                               False )
        for hit in hit_list:
            # Richtungsvektor zum Player
            bounce( hit, self.character_player )
            hit.undo()
            hit.update()
            hit.update()
            hit.queuemessage("aua!!",200)
            
            
        # Kollision npc mit wand
        for npc in self.group_npcs:
            hit_list = pygame.sprite.spritecollide( npc, self.group_mauern, False )
            
            # Iteration über die berührten Wandkacheln:
            for hit in hit_list:
                if hit.rect.x > npc.rect.x + npc.rect.width:
                    npc.speedx = -abs(npc.speedx)
                if hit.rect.x + hit.rect.width < npc.rect.x:
                    npc.speedx = abs(npc.speedx)
                if hit.rect.y > npc.rect.y + npc.rect.width:
                    npc.speedy = -abs(npc.speedy)
                if hit.rect.y + hit.rect.height < npc.rect.y:
                    npc.speedy = abs(npc.speedy)
                
                
        
        
        # Bounce on Wall (Spielfeldbegrenzung für NPC):
        maxx = self.game_display.get_rect().width - 16
        maxy = self.game_display.get_rect().height - 16
        for sprite in self.group_npcs:
            if sprite.rect.x < 0 or sprite.rect.x > maxx:
                sprite.undo()
                sprite.speedx = -sprite.speedx
            if sprite.rect.y < 0 or sprite.rect.y > maxy:
                sprite.undo()
                sprite.speedy = -sprite.speedy


        # Objekte rendern:
        self.group_background.draw( self.game_display )
        self.group_mauern.draw( self.game_display )
        self.group_npcs.draw( self.game_display )
        self.group_inout.draw( self.game_display )
        self.group_player.draw( self.game_display )
        
        # Nachrichten ausgeben
        self.character_player.drawmessage( self.game_display )
        for sprite in self.group_npcs:
            sprite.drawmessage( self.game_display )
    
        return self # die aktuelle Szene soll erstmal weiter laufen
    
