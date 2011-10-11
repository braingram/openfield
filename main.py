#!/usr/bin/env python

import logging, sys

import numpy as np

import cv

logging.basicConfig(level=logging.DEBUG)

fn = 'h2fly2-0000.mp4'
if len(sys.argv) > 1:
    fn = sys.argv[1]

bgfn = 'bg.png'
if len(sys.argv) > 2:
    bgfn = sys.argv[2]

corners = [[259, 117], [720, 98], [725, 567], [268, 567]] # clockwise from top left

corners = np.array(corners)
mazebb = np.array([[np.min(corners[:,0]), np.min(corners[:,1])], [np.max(corners[:,0]), np.max(corners[:,1])]])
mazexbb = [mazebb[0,0], mazebb[1,0]]
mazeybb = [mazebb[0,1], mazebb[1,1]]

cap = cv.CreateFileCapture(fn)
width = int(np.round(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH)))
height = int(np.round(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT)))
size = (int(width), int(height))
logging.debug("Frame size: %i %i" % size)
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_POS_AVI_RATIO, 1.0)
nframes = int(np.round(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_POS_FRAMES)))
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_POS_AVI_RATIO, 0.0)
#nframes = int(cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT)) # doesn't seem to work
logging.debug("NFrames: %i" % nframes)

# make scratch images
gim = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
fgim = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
fim = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
bim = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

# get background
if bgfn is None:
    nbg = 100
    logging.debug("Calculating background from %i images" % nbg)
    pos = np.linspace(0., 1., nbg)
    acc = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
    gim = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    # accumulate several images across session
    for p in pos:
        cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_POS_AVI_RATIO, p)
        im = cv.QueryFrame(cap)
        cv.CvtColor(im, gim, cv.CV_RGB2GRAY)
        cv.Acc(gim, acc)
    # scale bg
    cv.Scale(acc, acc, 1./float(nbg))
    bg = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.ConvertScale(acc, bg, 1.)
    # save bg
    logging.debug("Saving background to bg.png")
    cv.SaveImage('bg.png', bg)
else: # background was already found, just load from file
    logging.debug("Loading background from file %s" % bgfn)
    bg = cv.LoadImage(bgfn, False)

fbg = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
cv.ConvertScale(bg, fbg, 1./255.)

logging.debug("Processing frames")
cv.SetCaptureProperty(cap, cv.CV_CAP_PROP_POS_FRAMES, 0)

#for i in xrange(nframes):
frameNumber = 0
#xym = []
outfile = open('locs.csv','w')
#while True:
frameNumber = 0
im = None
for frameNumber in xrange(nframes):
#for i in xrange(100):
    im = cv.QueryFrame(cap)
    if im is None: break
    if (frameNumber % 100) == 0: logging.debug("Frame %i" % frameNumber)
    cv.CvtColor(im, gim, cv.CV_RGB2GRAY)
    cv.ConvertScale(gim, fgim, 1./255.)
    cv.Sub(fgim, fbg, fim)
    cv.Scale(fim, fim, -255.)
    #print cv.MinMaxLoc(fim)
    cv.Threshold(fim, bim, 100., 255, cv.CV_THRESH_BINARY)
    cv.Erode(bim, bim, iterations=1)
    cbim = bim[mazeybb[0]:mazeybb[1],mazexbb[0]:mazexbb[1]]
    #pts = cv.FindContours(cbim, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_LINK_RUNS)
    #area = cv.ContourArea(pts)
    rect = cv.BoundingRect(cbim)
    if False:#len(pts) >= 6:
        logging.debug("Ellipse")
        m = cv.CreateMat(1, len(pts), cv.CV_32FC2)
        for (i, (x,y)) in enumerate(pts):
            m[0,i] = (x,y)
        e = cv.FitEllipse2(m)
        (ecenter, esize, eangle) = e
        cv.Ellipse(im, (int(ecenter[0]+mazexbb[0]), int(ecenter[1]+mazeybb[0])), (int(esize[0]*0.5), int(esize[1]*0.5)), -eangle, 0, 360, (0,0,255), 2, cv.CV_AA, 0)
        x = ecenter[0] + mazexbb[0]
        y = ecenter[1] + mazeybb[0]
        m = 1
    else:
        #logging.debug("Rectangle")
        x, y = (int(mazexbb[0] + rect[0]), int(mazeybb[0] + rect[1]))
        w, h = (rect[2], rect[3])
        cv.Rectangle(im, (x,y), (x+w, y+h), (255,0,0))
        x = x + w/2.
        y = y + h/2.
        m = 2
        outfile.write("%i, %.3f, %.3f, %.3f, %.3f\n" % (frameNumber, x, y, w, h))
    #xym.append([x,y,m])
    if (frameNumber % 1000) == 0:
        cv.SaveImage('frames/%03i.png' % frameNumber, im)
    #fn = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_POS_FRAMES)
    #if np.round(fn) != frameNumber:
    #    # for some reason opencv likes to just keep looping through the damn file
    #    logging.debug("Reached end: %i %f" % (frameNumber, fn))
    #    break
    #frameNumber += 1
cv.SaveImage('frames/%03i.png' % frameNumber, im)
#np.savetxt('locs.csv',np.array(xym))
