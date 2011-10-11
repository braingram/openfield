#!/usr/bin/env python

# functions to be use:
#   StereoCalibrate
#   StereoRectify (post-StereoCalibrate)
#   StereoRectifyUncalibrated (if no StereoCalibrate,
#       should still use CalibrateCamera2 on each camera and Undistort2/UndistortPoints

import logging
import sys
import time
import os
import optparse

#import numpy
import cv
#import dc1394simple

# kinect grid
gridSize = (8,6)
gridBlockSize = 108 # mm

# parse options
gridFiles = []

logging.basicConfig(level=logging.DEBUG)
#cv.Undistort2(image, undistortedImage, self.camMatrix, self.distCoeffs)

def calibrate(gridFiles, gridSize, gridBlockSize):
    cpts = []
    imageSize = None
    for gf in gridFiles:
        image = cv.LoadImage(gf,False)
        success, corners = cv.FindChessboardCorners(image, gridSize)
        corners = cv.FindCornerSubPix(image, corners, (5,5), (-1,-1),
                    (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1))
        gridN = gridSize[0] * gridSize[1]
        if len(corners) != gridN:
            logging.debug("File failed: %s" % gf)
            continue
        # fix corners so that the first point is top left
        # compare corner[0] to corner[-1]
        if corners[0][0] > corners[1][0]:
            # flip left/right
            logging.debug("Grid is horizontally flipped")
            flipped = []
            for x in xrange(gridSize[0]):
                for y in xrange(gridSize[1]):
                    cx = gridSize[0] - x - 1
                    cy = y
                    flipped.append(corners[cx + cy * gridSize[0]])
            corners = flipped
        if corners[0][1] > corners[-1][1]:
            # flip top/bottom
            logging.debug("Grid is vertically flipped")
            flipped = []
            for x in xrange(gridSize[0]):
                for y in xrange(gridSize[1]):
                    cx = x
                    cy = gridSize[1] - y - 1
                    flipped.append(corners[cx + cy * gridSize[0]])
            corners = flipped
        cpts.append(corners)
        imageSize = cv.GetSize(image)

    nGrids = len(cpts)
    logging.debug("Found %i grids" % nGrids)
    if nGrids < 7:
        logging.warning("Few grids found: %i" % nGrids)
    if nGrids < 5:
        raise ValueError("Too few grids: %i" % nGrids)

    camMatrix = cv.CreateMat(3, 3, cv.CV_64FC1)
    cv.SetZero(camMatrix)
    camMatrix[0,0] = 1.
    camMatrix[1,1] = 1.

    distCoeffs = cv.CreateMat(5, 1, cv.CV_64FC1)
    cv.SetZero(distCoeffs)

    gridN = gridSize[0] * gridSize[1]
    
    imPts = cv.CreateMat(nGrids*gridN, 2, cv.CV_64FC1)
    objPts = cv.CreateMat(nGrids*gridN, 3, cv.CV_64FC1)
    ptCounts = cv.CreateMat(nGrids, 1, cv.CV_32SC1)
        
    # organize self.calibrationImgPts (to imPts) and construct objPts and ptCounts
    for (i,c) in enumerate(cpts):
        for j in xrange(gridN):
            imPts[j+i*gridN, 0] = c[j][0]
            imPts[j+i*gridN, 1] = c[j][1]
            # TODO should thes be actual points? how do I know what they are?
            objPts[j+i*gridN, 0] = j % gridSize[0] * gridBlockSize
            objPts[j+i*gridN, 1] = j / gridSize[0] * gridBlockSize
            objPts[j+i*gridN, 2] = 0.
        ptCounts[i,0] = len(c)
    
    cv.CalibrateCamera2(objPts, imPts, ptCounts, imageSize,
        camMatrix, distCoeffs,
        cv.CreateMat(nGrids, 3, cv.CV_64FC1),
        cv.CreateMat(nGrids, 3, cv.CV_64FC1), 0)
    
    cv.Save("camMatrix.xml", camMatrix)
    cv.Save("distCoeffs.xml", distCoeffs)
    
    #self.camMatrix = cv.Load("%s/camMatrix.xml" % directory)
    #self.distCoeffs = cv.Load("%s/distCoeffs.xml" % directory)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-s','--blocksize',
            help = "size of grid blocks",
            type = "float", default = 108.)
    parser.add_option('-x','--gridx',
            help = "grid x size (number of internal corners)",
            type = "int", default = 8)
    parser.add_option('-y','--gridy',
            help = "grid y size (number of internal corners)",
            type = "int", default = 6)
    options, args = parser.parse_args()
    gridFiles = args
    if len(gridFiles) == 0:
        raise ValueError("grid files not supplied: %s" % str(gridFiles))
    
    calibrate(gridFiles, (options.gridx, options.gridy), options.blocksize)
