import cv2
import numpy as np

# ----------- read - write routine ------------- 
def readGrayIm(ifile):
    im = cv2.imread(ifile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    return (255 - im).astype(float) / 255


def writeGrayIm(ofile, m):
    cv2.imwrite(ofile, 255 - (m * 255).astype(int))


# ------------ central line finding -------------
def centralind(arr):
    rsum = np.sum(arr, 1)
    maxInd = np.argmax(rsum)
    return maxInd


def writeCline(arr):
    orr = arr.copy()
    ind = centralline(arr)
    orr[(ind):(ind + 1),:] = 1
    return orr


# ----- splitting based on central line and verticall space -----
def dosplit(m):
    cli = centralline(m)
    zeros = findzeros(m[cli,:])
    spaces = []
    for zero in zeros:
        a = np.sum(m[:,zero[0]:zero[1]], 0)
        #print("PreSpaces: %s" % a)
        tsp = findzeros(a)
        #print("Spaces: %s" % tsp)
        if len(tsp) > 1:
            print("Warning: %s inner-spaces found" % len(tsp))        
        if len(tsp) != 0: 
            spaces.append((tsp[0][0] + zero[0], tsp[0][1] + zero[0]))
    pieces = []
    ind = spaces[0][0] == 0 and spaces[0][1] or 0
    for space in spaces:
        pieces.append(m[:,ind:space[0]])
        print("piece: %s - %s" % (ind, space[0]))
        ind = space[1]
    if spaces[len(spaces) - 1][1] < m.shape[1]:
        pieces.append(m[:, ind:m.shape[1]])
        print("piece: %s - %s" % (ind, m.shape[1]))
    return pieces


def findzeros(a):
    zeros = []
    zero = findzero(a, 0)
    while zero is not None:
        zeros.append(zero)
        zero = findzero(a, zero[1])
    return zeros


def findzero(a, s):
    while (s < len(a) and a[s] != 0):
        s += 1
    if (s < len(a)):
        start = s
        while (s < len(a) and a[s] == 0):
            s += 1
        return (start, s)
    return None

# ------------- do staff --------------------

def doLine(ifile, ofile):
    im = readGrayIm(ifile)
    linedim = writeCline(im)
    writeGrayIm(ofile, linedim)

def do(ifile, ofolder):
    im = readGrayIm(ifile)
    splits = dosplit(im)
    print("Splis found: %s" % len(splits))
    i = 1
    for split in splits:
        writeGrayIm(ofolder + "/%s.bmp" % i, split)
        i += 1
    

   


