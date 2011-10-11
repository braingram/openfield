#!/usr/bin/env python

import cv

cm = cv.Load('calibration/camMatrix.xml')
dc = cv.Load('calibration/distCoeffs.xml')

bg = cv.LoadImage('bg.png', False)

uim = cv.CreateImage(cv.GetSize(bg), bg.depth, bg.nChannels)
cv.Undistort2(bg, uim, cm, dc)

cv.SaveImage('uim.png', uim)

