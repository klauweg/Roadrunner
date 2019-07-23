
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode((320, 320))
pytmx_map = load_pygame("Fertigtest.tmx") 

# create sprite
boot = pygame.Surface( (16,16) )
boot.fill( pygame.Color(153,0,0) )
bootpos = boot.get_rect()
bootpos.x = 166
bootpos.y = 2

# create Spielfeld:
background = pygame.Surface((25*32, 25*32))

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
    collision = False
    baselayer = pytmx_map.get_layer_by_name("Kachelebene 1") # Layer nach Name auswählen
    for x, y, gid in baselayer:  # Iteriert über alle Kacheln in dem Layer
        image = pytmx_map.get_tile_image_by_gid( gid ) # Hier wird die tmx gid verwendet um die Grafik zu bekommen
        background.blit(image, (32*x, 32*y))    # Grafik auf den Hintergrund an die entsprechende Stelle kopieren
        if pytmx_map.map_gid(3)[0][0] != gid:  # tlied gid auf tmx gid mappen und vergleichen ob kein wasser
            if pygame.Rect( 32*x, 32*y, 32, 32).colliderect(bootpos): # Kollision neuer Bootposition mit Kachel prüfen
                collision = True

    if collision: # Falls kollision wird die alte Bootposition verwendet
        bootpos = oldbootpos
    if bootpos.x < 0 or bootpos.x > 308 or bootpos.y < 0 or bootpos.y > 308:
        bootpos = oldbootpos
        
    game_display.blit(background, (0,0)) # Hintergrund aufs Gamedisplay kopieren
    game_display.blit(boot, bootpos)     # Das Boot ins Gamedisplay kopieren
    pygame.time.Clock().tick(70)
    pygame.display.update()