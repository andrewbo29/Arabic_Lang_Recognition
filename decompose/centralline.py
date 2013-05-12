import numpy as np


# ------------ central line finding -------------
def centralind(arr):
    rsum = np.sum(arr, 1)
    maxInd = np.argmax(rsum)
    return maxInd


def writeCline(arr):
    orr = arr.copy()
    ind = centralind(arr)
    orr[ind: (ind + 1), :] = 1
    return orr


# ----- splitting based on central line and verticall space -----
def doSplit(m):
    """splitting based on central line, return splitted ndarrays"""
    # zero - zero interval in central line
    # space - horizontal interval - zeros on all lines in that interval
    cli = centralind(m)
    zeros = findZeros(m[cli, :])
    spaces = []
    for zero in zeros:
        space = insureSpace(m, zero)
        if space is not None:
            spaces.append(space)
    pieces = []
    ind = spaces[0][0] == 0 and spaces[0][1] or 0
    for space in spaces:
        pieces.append(m[:, ind:space[0]])
        print("piece: %s - %s" % (ind, space[0]))
        ind = space[1]
    if spaces[len(spaces) - 1][1] < m.shape[1]:
        pieces.append(m[:, ind:m.shape[1]])
        print("piece: %s - %s" % (ind, m.shape[1]))
    return pieces


def splitToPseudoAtoms(m):
    """splitting based on central line, return splitted ndarrays"""
    # zero - zero interval in central line
    # space - horizontal interval - zeros on all lines in that interval
    cli = centralind(m)
    zeros = findZeros(m[cli, :])
    spaces = []
    for zero in zeros:
        space = insureSpace(m, zero)
        if space is not None:
            spaces.append(space)
    print(zeros)
    pieces = []
    ind = 0
    if spaces[0][0] == 0:
        ind = spaces[0][1]
        spaces.pop(0)
    zInd = 0
    for space in spaces:
        piece = (ind, space[0])
        print("piece: %s - %s" % piece)
        ind = space[1]
        zInd, pieceZeros = __zerosInPiece(zeros, zInd, piece)
        pieces.append(PseudoAtom(m, piece, pieceZeros))
    if spaces[len(spaces) - 1][1] < m.shape[1]:
        piece = (ind, m.shape[1])
        print("piece: %s - %s" % piece)
        zInd, pieceZeros = __zerosInPiece(zeros, zInd, piece)
        pieces.append(PseudoAtom(m, piece, pieceZeros))
    return pieces


def __zerosInPiece(zeros, zInd, piece):
    pieceZeros = []
    for ind in range(zInd, len(zeros)):
        zero = zeros[ind]
        if zero[1] <= piece[0]:
            continue
        if zero[0] >= piece[1]:
            zInd = ind
            break
        if piece[0] <= zero[0] and zero[1] <= piece[1]:
            pieceZeros.append(zero)
    return zInd, pieceZeros


class PseudoAtom:
    def __init__(self, m, border, zeros):
        self.m = m
        self.border = border
        self.zeros = zeros

    def __repr__(self):
        repres = "border: " + str(self.border)
        if len(self.zeros) > 0:
            repres += "; zeros: " + str(self.zeros)
        return repres


def insureSpace(m, zero):
    """insure whether given zero interval contain split curve (or line)
    and if it is - return ??????"""
    a = np.sum(m[:, zero[0]:zero[1]], 0)
    tsp = findZeros(a)
    if len(tsp) > 1:
        print("Warning: %s inner-spaces found" % len(tsp))
    if len(tsp) != 0:
        return tsp[0][0] + zero[0], tsp[0][1] + zero[0]


def insureWrySpace(m, space, centralInd):
    """insure whether given ndarray have an wry-space
    and if it is - returns it"""
    ind = 0
    lefters = [space[0]]
    righters = [space[1]]
    centers = [(lefters[ind] + righters[ind]) / 2]
    y = centralInd
    while y < m.shape[0] - 1:
        y += 1
        (lefter, righter, center) = getLRC(m, (y, centers[ind]), centers[ind])
        if isShiftSignificant(lefters, lefter):
            print("Significant shift at y = %s" % y)
            zero = findZero(m[y, :], lefters[ind])
            print("Prev left: %s, new left: %s" % (lefters[ind], lefter))
            print("Zeros: ", zero)
            lefter = zero[0]
            righter = zero[1] - 1
            center = (lefter + righter) / 2
        ind += 1
        lefters.append(lefter)
        righters.append(righter)
        centers.append(center)
        if m[y, center] > 0:
            return None
        if emptyBottom(m, (y, center)):
            print("Empty bottom!!!")
            while y < m.shape[0] - 1:
                lefters.append(center)
                centers.append(center)
                righters.append(center)
                y += 1
    return lefters, righters, centers


def slicePA(pa, cInd):
    rSeq = [(i, pa.border[1]) for i in range(pa.m.shape[0])]
    pa.zeros.reverse()
    slices = []
    for zero in pa.zeros:
        x = insureWrySpace(pa.m, zero, cInd)
        if x is None:
            continue
        centers = x[2]
        lSeq = [(i, centers[0]) for i in range(cInd)]
        lSeq.extend([(i + cInd, centers[i]) for i in range(len(centers))])
        slices.append(cut(pa.m, lSeq, rSeq))
        rSeq = lSeq
    lSeq = [(i, pa.border[0]) for i in range(pa.m.shape[0])]
    slices.append(cut(pa.m, lSeq, rSeq))
    slices.reverse()
    return slices


def cut(im, lSeq, rSeq):
    high = im.shape[0]
    seqValid = lambda seq: seq[0][0] == 0 and seq[len(seq) - 1][0] == high - 1
    if not seqValid(lSeq):
        raise BaseException("Invalid left sequence")
    if not seqValid(rSeq):
        raise BaseException("Invalid right sequence")
    lv = min([p[1] for p in lSeq])
    rv = max([p[1] for p in rSeq])
    om = np.zeros(shape=(high, rv - lv))
    trans = lambda x: x - lv
    for i in range(high):
        om[i, trans(lSeq[i][1]):trans(rSeq[i][1])] = im[i, lSeq[i][1]:rSeq[i][1]]
    return om



def isShiftSignificant(seq, new):
    n = len(seq)
    if n <= 1:
        return False
    print("%s, %s" % (seq, new))
    print(diffs(seq))
    print([abs(x) for x in diffs(seq)])
    m = max([abs(x) for x in diffs(seq)])
    print(m)
    ndiff = new - seq[n - 1]
    return ndiff > 2 * m and ndiff > 2


def diffs(seq):
    """computes differences of a list"""
    ds = []
    prev = seq[0]
    for s in seq:
        ds.append(s - prev)
        prev = s
    return ds


def getLRC(m, coord, center):
    lg = leftGap(m, coord)
    rg = rightGap(m, coord)
    lefter = center - lg
    righter = center + rg
    center = (lefter + righter) / 2#lefter + __M2
    return (lefter, righter, center)


def leftGap(m, coord):
    rng = range(0,coord[1])
    rng.reverse()
    for i in rng:
        if m[coord[0], i] != 0:
            return abs(rng[0] - i)
    return abs(rng[len(rng) - 1] - rng[0])


def rightGap(m, coord):
    rng = range(coord[1] + 1,m.shape[1])
    for i in rng:
        if m[coord[0], i] != 0:
            return i - rng[0]
    return rng[len(rng) - 1] - rng[0]


def emptyBottom(m, coord):
    return sum(m[coord[0]:m.shape[0], coord[1]]) == 0


def findZeros(a):
    zeros = []
    x = findZero(a, 0)
    while x is not None:
        zeros.append(x)
        if x[1] >= len(a):
            break
        x = findZero(a, x[1])
    return zeros


def findZero(a, s):
    while s < len(a) and a[s] != 0:
        s += 1
    if s < len(a):
        start = s
        while s < len(a) and a[s] == 0:
            s += 1
        return start, s
    return None

# ------------- do staff --------------------
#
#
# def doLine(ifile, ofile):
#     im = readGrayIm(ifile)
#     linedim = writeCline(im)
#     writeGrayIm(ofile, linedim)
#
#
# def do(ifile, ofolder):
#     im = readGrayIm(ifile)
#     splits = doSplit(im)
#     print("Splis found: %s" % len(splits))
#     i = 1
#     for split in splits:
#         writeGrayIm(ofolder + "/%s.bmp" % i, split)
#         i += 1





