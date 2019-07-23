
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode((640, 640))
pytmx_map = load_pygame("Fertigtest.tmx") 

# create sprite
boot = pygame.Surface( (16,16) )
boot.fill( pygame.Color(153,0,0) )
bootpos = boot.get_rect()
bootpos.x = 475
bootpos.y = 30

# create Spielfeld:
background = pygame.Surface((20*32, 20*32))

loop = True
event = None
lastkey = None

while(loop):
    oldbootpos = bootpos.copy() # Merken falls Kollision stattfindet
    
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
        bootpos.x += -2
    elif lastkey == pygame.K_RIGHT:
        bootpos.x += 2
    elif lastkey == pygame.K_DOWN:
        bootpos.y += 2
    elif lastkey == pygame.K_UP:
        bootpos.y += -2

    # Darstellung der Hintergrundkacheln und Kollisionsprüfung:
    backgroundlayer = pytmx_map.get_layer_by_name("Kachelebene")
    playerground = backgroundlayer
    for x, y, gid in backgroundlayer:
        image = pytmx_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
        background.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren
    for objectgroup in pytmx_map.objectgroups:
        for object in objectgroup:
            background.blit( object.image, ( object.x, object.y ) )
            if pygame.Rect( object.x, object.y, 32, 32 ).colliderect(bootpos):
                playerground = objectgroup
                
    if playerground.name != "weg":
        bootpos = oldbootpos
        print("WIllst du das wirklich?")
    if bootpos.x < 0 or bootpos.x > 640-32 or bootpos.y < 0 or bootpos.y > 640-32:
        bootpos = oldbootpos
        print("nein")
        
    game_display.blit(background, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    game_display.blit(boot, bootpos)     # Das Boot ins Gamedisplay kopieren
    pygame.time.Clock().tick(70)
    pygame.display.update()