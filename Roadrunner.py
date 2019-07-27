

import pygame
import pytmx
from pytmx.util_pygame import load_pygame

from character import Character

# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode( (640,640) )

# Load the Maps:
# Das funktioniert erst nach dem Game Display init (wegen Videomode)
level1_map = load_pygame("Level1.tmx") 


# create background surface aus der Tilemap
background_surf = pygame.Surface((20*32, 20*32))
for x, y, gid in level1_map.get_layer_by_name("Kachelebene"):
    image = level1_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
    background_surf.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren

# create sprite groups aus der Tilemap
spritegroups={}
for objectgroup in level1_map.objectgroups:
    spritegroups[objectgroup.name]=pygame.sprite.Group()
    for object in objectgroup:
        spritegroups[objectgroup.name].add( Character( object.image, object.x, object.y, 0, 0 ) )


#########################################################################################



spritegroups['npc'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 164,0,0 ) )
npc1 = Character( player_surf, 75, 10, 0.5, 0.5 )
npc1.queuemessage("ich bin\nnpc1", 20000)
npc2 = Character( player_surf, 400, 30, 0.2, 0.1 )
npc2.queuemessage("ich bin\nnpc2", 22000)
npc3 = Character( player_surf, 100, 30, -0.2, 0.1 )
npc3.queuemessage("ich bin\nnpc3", 24000)
npc4 = Character( player_surf, 400, 300, -0.2, -0.1 )
npc4.queuemessage("ich bin\nnpc4",26000)
spritegroups['npc'].add( npc1 )
spritegroups['npc'].add( npc2 )
spritegroups['npc'].add( npc3 )
spritegroups['npc'].add( npc4 )

spritegroups['player'] = pygame.sprite.Group()
player_surf=pygame.Surface( (16,16) )
player_surf.fill( pygame.Color( 0,164,200 ) )
player = Character( player_surf, 400, 400, 0, 0 )
player.queuemessage("hallo\n2.zeile",5000)
player.queuemessage("2. nachricht",15000)
player.queuemessage("3. nachricht",15000)
spritegroups['player'].add( player )

########################################################################################

loop = True
event = None
lastkey = None
while(loop):
    # Bearbeiten der Message Queue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            lastkey = event.key
        if event.type == pygame.KEYUP:
            lastkey = None
    
    # Tasten verarbeiten:
    if lastkey == pygame.K_ESCAPE:
        pygame.quit()
        quit()
    elif lastkey == pygame.K_LEFT:
        player.moveby( -2, 0 )
    elif lastkey == pygame.K_RIGHT:
        player.moveby( 2, 0 )
    elif lastkey == pygame.K_DOWN:
        player.moveby( 0, 2 )
    elif lastkey == pygame.K_UP:
        player.moveby( 0, -2 )


##################################################################################
        
    
    for spritegroup in spritegroups.values():
        spritegroup.update()
        
    game_display.blit(background_surf, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    
    for spritegroup in spritegroups.values():  # Objekte darstellen
        spritegroup.draw( game_display )
    
    for sprite in spritegroups['player']:    # Nachrichten ausgeben
        sprite.drawmessage( game_display )
    for sprite in spritegroups['npc']:    # Nachrichten ausgeben
        sprite.drawmessage( game_display )
    
    
    pygame.time.Clock().tick(70)
    pygame.display.update()
