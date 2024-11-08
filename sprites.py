import pygame
from constants import *
import numpy as np
from animation import Animator

BASETILEWIDTH = 16
BASETILEHEIGHT = 16
DEATH = 5

class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("spritesheet_mspacman.png").convert()
        transcolor = self.sheet.get_at((0,0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))
        
    def getImage(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        self.entity = entity
        # Carrega a sequência de imagens do cachorro (já olhando para esquerda)
        self.dog_images = [
            pygame.image.load(f'dog-grande-{i}.png').convert_alpha() 
            for i in range(1, 8)  # Carrega imagens de 1 a 7
        ]
        
        # Redimensiona todas as imagens para o tamanho correto
        self.dog_images = [
            pygame.transform.scale(img, (2*TILEWIDTH, 2*TILEHEIGHT))
            for img in self.dog_images
        ]
        
        # Cria versões espelhadas das imagens para a direita
        self.dog_images_right = [
            pygame.transform.flip(img, True, False)  # Flip horizontal (True), vertical (False)
            for img in self.dog_images
        ]
        
        self.entity.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.dog_images[0]
        self.facing_right = False

    def defineAnimations(self):
        sequence = (0, 1, 2, 3, 4, 5, 6)
        self.animations[LEFT] = Animator(sequence)
        self.animations[RIGHT] = Animator(sequence)
        self.animations[UP] = Animator(sequence)
        self.animations[DOWN] = Animator(sequence)
        self.animations[DEATH] = Animator(sequence, loop=False)

    def update(self, dt):
        if self.entity.alive:
            if self.entity.direction == STOP:
                self.entity.image = self.stopimage
            else:
                anim = self.animations[self.entity.direction]
                frame = anim.update(dt)
                
                # Escolhe a imagem base na direção
                if self.entity.direction == RIGHT:
                    self.entity.image = self.dog_images_right[frame]
                    self.stopimage = self.dog_images_right[0]
                    self.facing_right = True
                elif self.entity.direction == LEFT:
                    self.entity.image = self.dog_images[frame]
                    self.stopimage = self.dog_images[0]
                    self.facing_right = False
                else:  # UP ou DOWN
                    # Mantém a última direção horizontal
                    if self.facing_right:
                        self.entity.image = self.dog_images_right[frame]
                        self.stopimage = self.dog_images_right[0]
                    else:
                        self.entity.image = self.dog_images[frame]
                        self.stopimage = self.dog_images[0]
        else:
            frame = self.animations[DEATH].update(dt)
            self.entity.image = self.dog_images[frame]

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()

    def getStartImage(self):
        return self.dog_images[0]

    def getImage(self, x, y):
        return self.entity.image


class GhostSprites(Spritesheet):
    def __init__(self, entity):
        self.entity = entity
        original_image = pygame.image.load('coleira.png').convert_alpha()
        self.entity.image = pygame.transform.scale(original_image, (2*TILEWIDTH, 2*TILEHEIGHT))

    def update(self, dt):
        pass
               
    def getStartImage(self):
        return self.entity.image

    def getImage(self, x, y):
        return self.entity.image


class FruitSprites(Spritesheet):
    def __init__(self, entity, level):
        self.entity = entity
        original_image = pygame.image.load('pipula.png').convert_alpha()
        self.entity.image = pygame.transform.scale(original_image, (2*TILEWIDTH, 2*TILEHEIGHT))

    def getStartImage(self, key):
        return self.entity.image

    def getImage(self, x, y):
        return self.entity.image

class LifeSprites(Spritesheet):
    def __init__(self, numlives):
        # Cria uma superfície com fundo verde para as vidas
        self.background_color = (0, 255, 0)  # Verde - você pode ajustar os valores RGB
        
        # Carrega e configura a imagem do cachorro
        self.image = pygame.image.load('dog-grande-1.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (2*TILEWIDTH, 2*TILEHEIGHT))
        self.resetLives(numlives)

    def removeImage(self):
        if len(self.images) > 0:
            self.images.pop(0)

    def resetLives(self, numlives):
        self.images = []
        for i in range(numlives):
            self.images.append(self.image)

    def getImage(self, x, y):
        return self.image

class MazeSprites(Spritesheet):
    def __init__(self, mazefile, rotfile):
        self.data = self.readMazeFile(mazefile)
        self.rotdata = self.readMazeFile(rotfile)

    def constructBackground(self, background, y):
        # Cores
        DARK_GRAY = (64, 64, 64)  # Cinza escuro para caminhos e certas paredes
        LIGHT_GRAY = (192, 192, 192)  # Cinza claro para o fundo da casinha dos fantasmas
        GREEN_COLOR = (0, 255, 0)  # Verde para 'X'
        ROAD_COLOR = (128, 128, 128)  # Cinza para ruas
        LINE_COLOR = (255, 255, 0)  # Amarelo para a faixa
        DARK_BLUE = (0, 0, 139)  # Azul escuro para a área dos fantasmas

        # Preenche o fundo principal com verde
        background.fill(GREEN_COLOR)

        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                cell = self.data[row][col]
                
                # Desenha paredes cinza para '2', '3', '9'
                if cell in ['5', '4']:
                    pygame.draw.rect(background, DARK_GRAY, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                    
                if cell in ['2', '3', '9']:
                    pygame.draw.rect(background, DARK_GRAY, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                
                # Desenha azul escuro para '8' (área dos fantasmas)
                elif cell == '8':
                    pygame.draw.rect(background, DARK_BLUE, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                elif cell in ['|', 'n']:
                    pygame.draw.rect(background, ROAD_COLOR, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                    if (col > 0 and self.data[row][col-1] in ['.', '+']) or (col < self.data.shape[1] - 1 and self.data[row][col+1] in ['.', '+']):
                        for offset in range(0, TILEWIDTH, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + offset, row*TILEHEIGHT + TILEHEIGHT//2), 
                                             (col*TILEWIDTH + offset + 5, row*TILEHEIGHT + TILEHEIGHT//2), 2)
                    elif (row > 0 and self.data[row-1][col] in ['.', '+']) or (row < self.data.shape[0] - 1 and self.data[row+1][col] in ['.', '+']):
                        for offset in range(0, TILEHEIGHT, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset), 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset + 5), 2)
                            
                elif cell in ['-', '=', 'P', 'p']:
                    pygame.draw.rect(background, ROAD_COLOR, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                    if (col > 0 and self.data[row][col-1] in ['.', '+']) or (col < self.data.shape[1] - 1 and self.data[row][col+1] in ['.', '+']):
                        for offset in range(0, TILEWIDTH, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + offset, row*TILEHEIGHT + TILEHEIGHT//2), 
                                             (col*TILEWIDTH + offset + 5, row*TILEHEIGHT + TILEHEIGHT//2), 2)
                    elif (row > 0 and self.data[row-1][col] in ['.', '+']) or (row < self.data.shape[0] - 1 and self.data[row+1][col] in ['.', '+']):
                        for offset in range(0, TILEHEIGHT, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset), 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset + 5), 2)


                # Desenha verde para 'X', exceto na área dos fantasmas
                elif cell == 'X':
                    pygame.draw.rect(background, GREEN_COLOR, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                
                # Desenha ruas com faixa amarela para '.' ou '+'
                elif cell in ['.', '+']:
                    pygame.draw.rect(background, ROAD_COLOR, 
                                     (col*TILEWIDTH, row*TILEHEIGHT, TILEWIDTH, TILEHEIGHT))
                    if (col > 0 and self.data[row][col-1] in ['.', '+']) or (col < self.data.shape[1] - 1 and self.data[row][col+1] in ['.', '+']):
                        for offset in range(0, TILEWIDTH, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + offset, row*TILEHEIGHT + TILEHEIGHT//2), 
                                             (col*TILEWIDTH + offset + 5, row*TILEHEIGHT + TILEHEIGHT//2), 2)
                    elif (row > 0 and self.data[row-1][col] in ['.', '+']) or (row < self.data.shape[0] - 1 and self.data[row+1][col] in ['.', '+']):
                        for offset in range(0, TILEHEIGHT, 10):
                            pygame.draw.line(background, LINE_COLOR, 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset), 
                                             (col*TILEWIDTH + TILEWIDTH//2, row*TILEHEIGHT + offset + 5), 2)

        return background

    def readMazeFile(self, mazefile):
        return np.loadtxt(mazefile, dtype='<U1')
