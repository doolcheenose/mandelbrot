import numpy as np
import pygame
from pygame.locals import * # for mouse stuff
import time

class MandelViewer:
    def __init__(self, W, H):
        self.W = W
        self.H = H
        self.size = (W, H)
        self.THRESHOLD = 2
        self.xRange = 4.0
        self.yRange = 4.0
        self.tl = -2.0 + 2.0j
        self.reals = np.linspace(self.tl.real + 0j, self.tl.real + self.xRange + 0j, W)
        self.imags = np.linspace(0 + 1.0j * self.tl.imag, 0 + 1.0j * (self.tl.imag - self.yRange), H)
        self.region = self.reals[:, np.newaxis] + self.imags
        self.MAX_IT = 200
        self.CONV = np.iinfo(np.uint32).max // self.MAX_IT
        self.pixels = (self.CONV * self.MAX_IT) * (np.ones(W * H).reshape(W, H))
        self.z = self.region.copy()
        self.i = 1

    def update_pixels(self, step):
        if self.i >= self.MAX_IT:
            return
        print('update called')
        print(self.pixels)
        for _ in range(step):
            if self.i > self.MAX_IT:
                break
            else:
                self.z = np.where(np.absolute(self.z) > self.THRESHOLD,
                                  self.z,
                                  self.z ** 2 + self.region)
                self.pixels = np.where((np.absolute(self.z) > self.THRESHOLD) & (self.pixels == (self.CONV * self.MAX_IT)),
                                       self.CONV * self.i,
                                       self.pixels)
                self.i += 1

    def zoom(self, anchor_x, anchor_y, scale=0.1): # negative scale -> zoom out
        self.i = 1
        self.reals = np.add((1 - scale)*self.reals, scale * self.reals[anchor_x])
        self.imags = np.add((1 - scale)*self.imags, scale * self.imags[anchor_y])
        self.region = self.reals[:, np.newaxis] + self.imags
        self.z = self.region.copy()
        self.pixels = (self.CONV * self.MAX_IT) * (np.ones(self.W * self.H).reshape(self.W, self.H))

    def run(self):
        self.screen = pygame.display.set_mode(self.size)

        done = False
        while True:
            self.update_pixels(step=10)
            pygame.surfarray.blit_array(self.screen, self.pixels)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == MOUSEWHEEL:
                    print('scroll = {0}'.format(event.y))
                    self.zoom(*pygame.mouse.get_pos(), scale=(0.1 * event.y))

if __name__ == '__main__':
    M = MandelViewer(600, 600)
    M.run()
