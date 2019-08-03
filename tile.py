
import pygame
import pytmx

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
def layer2spritegroup( tmx_map, layername ):
    spritegroup = pygame.sprite.Group() # Neues Spritegroup Layer erzeugen
    tilewidth = tmx_map.tilewidth
    tileheight = tmx_map.tileheight
    for x, y, image in tmx_map.get_layer_by_name( layername ).tiles():
        spritegroup.add( Tile( x*tilewidth, y*tileheight, image ) )
    return spritegroup
                        
