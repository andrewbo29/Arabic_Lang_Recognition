import cv2
import numpy as np


im = readGrayIm("couple.bmp") 
centralInd = im.shape[0] / 2
zeros = findzeros(im[centralInd, :])
space = zeros[2]
(lefters, righters, centers) = insureWrySpace(im, space, centralInd)
om = im.copy()
drawSeq(om, toPoints(centralInd,lefters))
drawSeq(om, toPoints(centralInd,righters))
drawSeq(om, toPoints(centralInd,centers))


def toPoints(centralInd, seq):
    pts = []
    i = centralInd
    for s in seq:
        pts.append((i, s))
        i += 1
    return pts



def drawLine(m, p1, p2):
    cv2.line(m, p1, p2, 0.5)



def drawSeq(m, seq):
    p1 = seq[0]
    for i2 in range(1, len(seq)):
        p2 = seq[i2]
        drawLine(m, p1, p2)
        p1 = p2

 
