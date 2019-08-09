import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import random

from gameobjects import *


# Base Class:
class Scene(object):
    def __init__( self, game_display ):
        self.game_display = game_display
        
        # Den spieler erzeugen wir für alle Level:
        player_surf=pygame.Surface( (16,16) )
        player_surf.fill( pygame.Color( 0,164,200 ) )
        self.character_player = Character( player_surf, 100, 100, 0, 0 )
        self.character_player.showmessage("Lets go!",5000)
        self.group_player = pygame.sprite.Group()
        self.group_player.add( self.character_player )
        self.character_player.speed = 2
        
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

        # Hier berechnen wir den neuen Geschwindikeitsvektor
        # des Spielers aus Schwindikeitsbetrag und Tastenzustand:
        speedx = 0
        speedy = 0
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[ pygame.K_LEFT ]:
            speedx = speedx - self.character_player.speed
        if keys_pressed[ pygame.K_RIGHT ]:
            speedx = speedx + self.character_player.speed
        if keys_pressed[ pygame.K_UP ]:
            speedy = speedy - self.character_player.speed
        if keys_pressed[ pygame.K_DOWN ]:
            speedy = speedy + self.character_player.speed
        self.character_player.speedx = speedx
        self.character_player.speedy = speedy

        # Der Spieler wird immer neu berechnet:
        self.character_player.update()

        # Spielfeldbegrenzung für Spieler:
        # (sollte normal nicht vorkommen, weil das Spielfeld durch
        # Wände o.ä. begrenzt ist. Nur zur Sicherheit:
        self.character_player.x = max(
            0, min( self.character_player.x, self.game_display.get_rect().width - self.character_player.rect.width) )
        self.character_player.y = max(
            0, min( self.character_player.y, self.game_display.get_rect().height - self.character_player.rect.height) )

        # Kollision Spieler mit Wand
        while bounce( self.character_player, self.group_mauern, True ):
            print("update")
            self.character_player.update()
               


############################### Level 1 ##########################

class Level1( Scene ):
    def __init__( self, game_display, mapfile ):
        super().__init__( game_display )

        self.character_player.speed = 2.5
        self.map_scene = load_pygame( mapfile ) # load data with Surfaces
        
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
            speedx = (random.random()-0.5) * 3
            speedy = (random.random()-0.5) * 3
            return Character( npc_surf, x, y, speedx, speedy )

        # Erzeugen der NPCs:
        self.group_npcs = pygame.sprite.Group()
        for npc in range( 1, 20):
            npc_character = generate_random_npc()
            npc_character.showmessage("Ich bin\nNPC " + str(npc), 1500 )
            self.group_npcs.add( npc_character )


    def schedule( self ):
        # Aufrufen der Elternmethode:
        super().schedule()
        
        # Update Methode aller Sprites in allen Gruppen aufrufen:
        # ( Neue Position anhand der Geschwindigkeit wird berechnet )
        self.group_npcs.update()

        # Kollisionsverarbeitung npc -> Spieler:
        for npc in self.group_npcs:
            bounce( npc, self.group_player )

        # Kollision npc mit wand
        for npc in self.group_npcs:
            bounce( npc, self.group_mauern )

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
    
        if self.character_player.rect.colliderect( self.tile_ziel.rect ):
            return Level1( self.game_display, "Maps/Level2.tmx" )
        return self # die aktuelle Szene soll erstmal weiter laufen
    
