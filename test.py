import numpy as np
import pygame
from pygame.locals import * # for mouse stuff
import time
import matplotlib.pyplot as plt
import matplotlib as mpl

class MandelViewer:
    def __init__(self, W, H):
        self.W = W
        self.H = H
        self.size = (W, H)
        self.THRESHOLD = 2
        self.xRange = 4.0 # just used for initialization
        self.yRange = 4.0 # same with this
        self.tl = -2.0 + 2.0j # and this
        self.reals = np.linspace(self.tl.real + 0j, self.tl.real + self.xRange + 0j, W)
        self.imags = np.linspace(0 + 1.0j * self.tl.imag, 0 + 1.0j * (self.tl.imag - self.yRange), H)
        self.region = self.reals[:, np.newaxis] + self.imags
        self.MAX_IT = 200
        self.z = self.region.copy()
        # color stuff, basically color dict maps each 0 < i <= MAX_IT to int32 val
        self.cmap = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=1, vmax=self.MAX_IT), cmap=mpl.cm.jet)
        self.color_dict = {j:self.rgba_to_int32(self.cmap.to_rgba(j)) for j in range(1, self.MAX_IT+1)}
        self.pixels = (self.color_dict[self.MAX_IT]) * (np.ones(W * H).reshape(W, H))
        self.i = 1

    def rgba_to_int32(self, rgba):
        return sum((256 ** i) * int(rgba[(2 - i) % 4]*255) for i in range(4)) # rgba -> a r g b (thats why (2 - i) % 4)

    def update_pixels(self, step):
        if self.i >= self.MAX_IT:
            return
        for _ in range(step):
            if self.i > self.MAX_IT:
                break
            else:
                self.z = np.where(np.absolute(self.z) > self.THRESHOLD,
                                  self.z,
                                  self.z ** 2 + self.region)
                self.pixels = np.where((np.absolute(self.z) > self.THRESHOLD) & (self.pixels == self.color_dict[self.MAX_IT]),
                                       self.color_dict[self.i],
                                       self.pixels)
                self.i += 1

    def zoom(self, anchor_x, anchor_y, scale=0.1): # negative scale -> zoom out
        self.i = 1
        self.reals = np.add((1 - scale)*self.reals, scale * self.reals[anchor_x])
        self.imags = np.add((1 - scale)*self.imags, scale * self.imags[anchor_y])
        self.region = self.reals[:, np.newaxis] + self.imags
        self.z = self.region.copy()
        self.pixels = (self.color_dict[self.MAX_IT]) * (np.ones(self.W * self.H).reshape(self.W, self.H))

    def run(self):
        self.screen = pygame.display.set_mode(self.size)

        while True:
            self.update_pixels(step=10)
            pygame.surfarray.blit_array(self.screen, self.pixels) # blit_array must use numpy
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == MOUSEWHEEL:
                    self.zoom(*pygame.mouse.get_pos(), scale=(0.1 * event.y))
                elif event.type == pygame.KEYDOWN and event.mod == KMOD_NONE:
                    print('key pressed')

if __name__ == '__main__':
    M = MandelViewer(600, 600)
    M.run()
