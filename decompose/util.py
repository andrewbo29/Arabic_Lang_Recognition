import cv2

# ----------- read - write routine -------------


def readGrayIm(path):
    im = cv2.imread(path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    return (255 - im).astype(float) / 255


def writeGrayIm(path, m):
    cv2.imwrite(path, 255 - (m * 255).astype(int))


# -------------- drawing routine -----------------


def toPoints(centralInd, xseq):
    """ fakin cv points has (x,y) format instead of (y,x) """
    pts = []
    i = centralInd
    for x in xseq:
        pts.append((x, i))
        i += 1
    return pts


def drawLine(m, p1, p2):
    cv2.line(m, p1, p2, 0.9)


def drawSeq(m, seq):
    p1 = seq[0]
    for i2 in range(1, len(seq)):
        p2 = seq[i2]
        drawLine(m, p1, p2)
        p1 = p2


