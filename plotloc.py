#!/usr/bin/env python

import sys

import numpy as np
import pylab as pl

#corners = [[259, 117], [720, 98], \
#        [725, 567], [268, 567]] # clockwise from top left
corners = [[300, 65], [760, 73], \
        [732, 528], [291, 505]]

corners = np.array(corners)
mazebb = np.array([[np.min(corners[:, 0]), np.min(corners[:, 1])], \
        [np.max(corners[:, 0]), np.max(corners[:, 1])]])
mazexbb = [mazebb[0, 0], mazebb[1, 0]]
mazeybb = [mazebb[0, 1], mazebb[1, 1]]

frames, xs, ys, ws, hs = locs = \
        np.loadtxt('locs.csv', delimiter=',', unpack=True)

if len(sys.argv) > 1:
    bg = pl.imread(sys.argv[1])
    if '.jpg' in sys.argv[1].lower():
        bg = bg[::-1]
else:
    bg = pl.imread('bg.png')

pl.subplot(121)
pl.imshow(bg)
pl.gray()
pl.plot(xs, ys)
pl.xlim(mazexbb)
pl.ylim(mazeybb)

pl.subplot(122)
pl.plot(frames, ws, label='width')
pl.plot(frames, hs, label='height')
pl.legend()
pl.xlabel('Frames')
pl.ylabel('Size(pixels)')

pl.show()
