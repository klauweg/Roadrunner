import pygame

# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode( (640,640) )

# Eigene Module:
import scenes

###################### Main Loop ##############################

# Festlegen mit welcher Szene gestartet werden soll:
running_scene = scenes.Level1( game_display )

# Ausführen und auf Szenenwechsel bzw. Ende warten:
while(running_scene):
    running_scene = running_scene.schedule()
    pygame.time.Clock().tick(70)
    pygame.display.update()

