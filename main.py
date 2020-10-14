import numpy as np
import pyglet as pg
from pyglet.gl import *
from OpenGL.GLUT import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import time


THRESHOLD = 2 # pre-chosen
topleft = (-2.0, 2.0)
xRange = 4.0
yRange = 4.0
W = 600
H = 600

# use broadcasting to create the screen
region = np.linspace(topleft[0] + 0j,
    topleft[0]+xRange + 0j, 2*W)[:, np.newaxis] + np.linspace(0 + 1.0j*topleft[1],
    0 + 1.0j*(topleft[1]-yRange), 2*H)

print(region.shape)

def iterate(numIterations):
    z = region.copy()
    reg = region.copy()
    pixels = numIterations * np.ones(4 * W * H).reshape(region.shape)
    for i in range(1, numIterations):
        z = np.where(np.absolute(z) < THRESHOLD, z ** 2 + reg, z)
        pixels = np.where((pixels == numIterations) & (np.absolute(z) > THRESHOLD), i, pixels)
    return pixels

class M_Window(pg.window.Window):
    def __init__(self, W, H, precision):
        super(M_Window, self).__init__(W, H)
        self.W = W
        self.H = H
        self.THRESHOLD = 2
        self.xRange = 4.0
        self.yRange = 4.0
        self.tl = -2.0 + 2.0j
        self.region = np.linspace(self.tl.real + 0j,
            self.tl.real+self.xRange + 0j, 2*W)[:, np.newaxis] + np.linspace(0 + 1.0j*self.tl.imag,
            0 + 1.0j*(self.tl.imag-self.yRange), 2*H)
        self.pixels = precision * np.ones(4 * W * H).reshape(self.region.shape)
        self.z = self.region.copy()
        self.reg = self.region.copy() # bad code, might be unnecessary
        self.i = 1
        self.NUM_IT = precision
        self.cmap = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(vmin=1, vmax=self.NUM_IT), cmap=mpl.cm.jet)

    # called every 1/10.0 seconds, update 10 frames
    def update_region(self):
        if self.i < self.NUM_IT:
            start = time.time()
            for _ in range(10): # do 10 iterations every update, can be customizable
                self.z = np.where(np.absolute(self.z) < self.THRESHOLD, self.z ** 2 + self.reg, self.z)
                self.pixels = np.where((self.pixels == self.NUM_IT) & (np.absolute(self.z) > self.THRESHOLD), self.i, self.pixels)
                self.i = self.i + 1
            print('calculations took {0} seconds'.format(time.time() - start))


    def update_frame(self, x, y):
        start = time.time()
        self.update_region()
        self.color_pixels = self.cmap.to_rgba(self.pixels).flatten()
        print('update_frame took {0} seconds'.format(time.time() - start))

    """
    Turns out, using the rgba format with float values is wildly inneficient,
    taking ~1.5s to just draw the image to the screen, by far the biggest bottleneck
    in the system. Working on using a more efficient format, may just map manually
    without using the cmap feature of matplotlib

    apparently, glDrawPixels will always be slow, and i should use textures to
    accomplish this task. I will try the first fix in the paragraph above to see
    if the problem persists, and if so i will use textures or try a different
    route. It seems as though i should be able to accomplish this without
    directly accessing the openGL code, and just use pyglet. We will see...
    """
    def on_draw(self):

        start = time.time()
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawPixels(2 * self.W, 2 * self.H, GL_RGBA, GL_FLOAT, (GLfloat * len(self.color_pixels))(*self.color_pixels))
        glutSwapBuffers()
        print('on_draw took {0} seconds'.format(time.time() - start))


if __name__ == '__main__':
    window = M_Window(W, H, precision=200)

    pyglet.clock.schedule(window.update_frame, 1/10.0)
    pyglet.app.run()
