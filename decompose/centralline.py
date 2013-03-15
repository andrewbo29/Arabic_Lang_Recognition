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
    """splitting based on central line, return splitted ndarrays"""
    cli = centralline(m)
    zeros = findzeros(m[cli,:])
    spaces = []
    for zero in zeros:
        space = insureSpace(m, zero)
        if space is not None:
            spaces.append(space)
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


def insureSpace(m, zero):
    """insure whether given zero interval contain split curve (or line)
    and if it is - return ??????"""
    a = np.sum(m[:,zero[0]:zero[1]], 0)
    tsp = findzeros(a)
    if len(tsp) > 1:
        print("Warning: %s inner-spaces found" % len(tsp))
    if len(tsp) != 0:
        return (tsp[0][0] + zero[0], tsp[0][1] + zero[0])

__M1 = 10# magic number 1
__M2 = 5# magic number 2
def insureWrySpace(m, space, centralInd):
    """insure wheter given ndarray have an wry-space and if it is - returns it"""
    ind = 0
    lefters = [space[0]]
    righters = [space[1]]
    centers = [(lefters[ind] + righters[ind]) / 2]#[lefters[ind] + __M2]
    coord = (centralInd, centers[ind])
    try:
        while (ind < m.shape[0] - centralInd - 1):
            (lefter, righter, center) = getLRC(m, (coord[0] + 1, coord[1]), centers[ind])
            ind += 1
            lefters.append(lefter)
            righters.append(righter)
            centers.append(center)
            if abs(lefters[ind] - lefters[ind - 1]) > __M1:
                print("left out at %s" % ind)
                coord = (coord[0], lefter - __M2)
            elif abs(righters[ind] - righters[ind - 1]) > __M1:
                coord = (coord[0], righter + __M2)
                print("right out at %s" % ind)
            else:
                coord = (coord[0] + 1, centers[ind])
            print(ind)
    finally:
        return (lefters, righters, centers)




def getLRC(m, coord, center):
    lg = leftGap(m, coord)
    rg = rightGap(m, coord)
    lefter = center - lg
    righter = center + rg
    center = (lefter + righter) / 2#lefter + __M2
    return (lefter, righter, center)



def leftGap(m, coord):
    count = 0
    rng = range(0,coord[1])
    rng.reverse()
    print("leftGap coord: (%s, %s)" % coord)
    print("left gap in: [%s, %s]" % (rng[0], rng[len(rng) - 1]))
    for i in rng:
        if m[coord[0], i] != 0:
            break
        count += 1
    return count


def rightGap(m, coord):
    count = 0
    rng = range(coord[1] + 1,m.shape[1])
    print("rightGap coord: (%s, %s)" % coord)
    print("right gap in: [%s, %s]" % (rng[0], rng[len(rng) - 1]))
    for i in rng:
        if m[coord[0], i] != 0:
            break
        count += 1
    return count


a = [
[1,1,0,0,0,0,0,0,1],
[1,0,1,0,0,0,0,1,1],
[0,1,1,0,0,0,0,0,1],
[0,0,1,0,0,0,0,0,1],
[0,1,0,0,0,0,0,1,1],
[1,0,0,0,0,1,1,1,0],
[1,0,0,1,1,1,0,0,0],
[1,0,0,1,0,0,0,0,0],
[1,0,1,1,0,0,0,0,0],
[1,0,1,0,0,0,0,0,0]
]

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





