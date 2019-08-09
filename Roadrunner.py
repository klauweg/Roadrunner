import pygame

# initialize pygame
pygame.init()

# create game display
game_display = pygame.display.set_mode( (640,640) )
game_clock = pygame.time.Clock()

# Eigene Module:
import scenes

###################### Main Loop ##############################

# Festlegen mit welcher Szene gestartet werden soll:
running_scene = scenes.Level1( game_display, "Maps/Level1.tmx" )

last_ticks = pygame.time.get_ticks()
# Ausführen und auf Szenenwechsel bzw. Ende warten:
while(running_scene):
    running_scene = running_scene.schedule()
    game_clock.tick(60)
    pygame.display.update()
    
    # Framerate ausgeben:
    now_ticks = pygame.time.get_ticks()
    if now_ticks-last_ticks > 2000:
        print( "FPS: {0:.2f}".format(game_clock.get_fps()) )
        last_ticks = now_ticks
        
    # Mit Spacetaste anhalten:
    while pygame.key.get_pressed()[ pygame.K_SPACE ]:
        pygame.event.get() # anscheinend nötig für get_pressed()
        if pygame.key.get_pressed()[ pygame.K_b ]:
            pygame.quit()
            
