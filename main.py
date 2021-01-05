import numpy as np
import pygame
from pygame.locals import * # for mouse stuff
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

cl = np.clongdouble # precision difficulties...
THRESHOLD = 4.0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (70, 70, 70)
LIGHT_GREY = (180, 180, 180)

class MandelViewer:
    def __init__(self, W, H):
        self.W = W
        self.H = H
        self.size = (W, H)
        self.reals = np.linspace(-2.0 + 0j, 2.0 + 0j, W)
        self.imags = np.linspace(0 + 2.0j, 0 + -2.0j, H)
        self.region = self.reals[:, np.newaxis] + self.imags
        self.MAX_IT = 64
        self.IT_INC = 64
        # color stuff, basically color dict maps each 0 < i <= MAX_IT to int32 val
        self.cmap = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=1, vmax=self.IT_INC), cmap=mpl.cm.jet)
        self.color_dict = [self.rgba_to_int32(self.cmap.to_rgba(j+1)) for j in range(self.IT_INC)]
        self.pixels = (self.color_dict[self.IT_INC-1]) * (np.ones(W * H).reshape(W, H))
        pygame.font.init()
        self.font = pygame.font.Font('./fonts/PressStart2P.ttf', 8)
        self.zoom_factor = 1.0

    # helper function to convert float rgba -> int32
    def rgba_to_int32(self, rgba):
        return sum((256 ** i) * int(rgba[(2 - i) % 4]*255) for i in range(4)) # rgba -> a r g b (thats why (2 - i) % 4)

    # this is where the math happens
    def update_pixels(self):
        z = self.region.copy()
        self.pixels = (self.color_dict[(self.MAX_IT-1) % 64]) * (np.ones(self.W * self.H).reshape(self.W, self.H))
        for i in range(self.MAX_IT):
            magsqr = z.imag*z.imag + z.real*z.real
            z = np.where(magsqr > THRESHOLD,
                              z,
                              z * z + self.region)
            self.pixels = np.where((magsqr > THRESHOLD)
                                        & (self.pixels == self.color_dict[(self.MAX_IT-1) % 64]),
                                   self.color_dict[i % 64],
                                   self.pixels)



    def zoom(self, anchor_x, anchor_y, scale=0.1): # negative scale -> zoom out
        self.reals = np.add((1 - scale)*self.reals, scale * self.reals[anchor_x])
        self.imags = np.add((1 - scale)*self.imags, scale * self.imags[anchor_y])
        self.region = self.reals[:, np.newaxis] + self.imags

    # def zoom2(self, anchor_x, anchor_y, scale=0.1):
    #     self.i = 0
    #

    def run(self):
        self.screen = pygame.display.set_mode(self.size)

        while True:
            start = time.time()
            self.update_pixels()
            time_to_update = round(time.time() - start, 5)
            pygame.surfarray.blit_array(self.screen, self.pixels) # blit_array must use numpy


            update_time_text = self.font.render("Calculation Time: " + str(time_to_update) + 's', True, LIGHT_GREY)
            pos_str = "Location: " + str(self.region[self.H//2][self.W//2].real) + "  +  " + str(self.region[self.H//2][self.W//2].imag) + "i"
            iteration_str = 'Iterations: {}'.format(self.MAX_IT)
            position_text = self.font.render(pos_str, True, LIGHT_GREY)
            iteration_text = self.font.render(iteration_str, True, LIGHT_GREY)
            
            pygame.draw.rect(self.screen, BLACK, pygame.Rect(5, 5, 500, 35))
            self.screen.blit(update_time_text, (10, 10))
            self.screen.blit(position_text, (10, 30))
            self.screen.blit(iteration_text, (300, 10))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == MOUSEWHEEL:
                    self.zoom(*pygame.mouse.get_pos(), scale=(0.1 * event.y))
                elif event.type == pygame.KEYDOWN and event.mod == KMOD_NONE:
                    if event.key == pygame.K_UP:
                        self.MAX_IT = self.MAX_IT + self.IT_INC
                        print(self.MAX_IT)
                    elif event.key == pygame.K_DOWN:
                        self.MAX_IT = self.MAX_IT - self.IT_INC if self.MAX_IT > 0 else 0
                        print(self.MAX_IT)

if __name__ == '__main__':
    M = MandelViewer(600, 600)
    M.run()
