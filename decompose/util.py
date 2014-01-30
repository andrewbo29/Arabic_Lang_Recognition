# import cv2.cv as cv
from shutil import rmtree
from os import mkdir
import scipy.misc
import numpy

# ------ create - delete folders routine -------


def deleteDir(path):
    rmtree(path)
    return path


def makeDir(path):
    mkdir(path)
    return path


def remakeDir(path):
    rmtree(path, True)
    mkdir(path)
    return path

# ----------- read - write routine -------------


def readGrayIm(path):
    path_str = path.encode('cp1251')
    # read_im = cv.LoadImage(path_str, cv.CV_LOAD_IMAGE_GRAYSCALE)
    read_im = scipy.misc.imread(path_str)
    im = numpy.asarray(read_im[:, :])
    return (255 - im).astype(float) / 255


def writeGrayIm(path, m):
    # cv2.imwrite(path, 255 - (m * 255).astype(int))
    scipy.misc.imsave(path, 255 - (m * 255).astype(int))


# -------------- drawing routine -----------------


def toPoints(v_from, xseq):
    """ fakin cv points has (x,y) format instead of (y,x) """
    pts = []
    i = v_from
    for x in xseq:
        pts.append((x, i))
        i += 1
    return pts


# def drawLine(m, p1, p2):
#     cv2.line(m, p1, p2, 0.9)


# def drawSeq(m, seq):
#     p1 = seq[0]
#     for i2 in range(1, len(seq)):
#         p2 = seq[i2]
#         drawLine(m, p1, p2)
#         p1 = p2


