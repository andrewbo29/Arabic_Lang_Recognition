from util import *
import centralline as cl




#--------------- splitToPseudoAtoms & insureWhySpace in battle -------------------
def mark(m, cInd, pa):
    for z in pa.zeros:
        drawLine(m, (z[0], cInd), (z[1], cInd))
    return m


im = readGrayIm("../images/0.bmp")
pas = cl.splitToPseudoAtoms(im)
cInd = cl.centralind(im)
# for pa in pas:
#     mark(im, cInd, pa)
i = 1
for pa in pas:
    if pa.zeros:
        slices = cl.slicePA(pa, cInd)
        for slize in slices:
            writeGrayIm("../output/%s.bmp" % i, slize)
            i += 1
    else:
        writeGrayIm("../output/%s.bmp" % i, im[:, pa.border[0]:pa.border[1]])
        i += 1






#--------------------- checking doSplit -----------------------
#
# im = readGrayIm("../images/inputText.bmp")
# pieces = cl.doSplit(im)
# for i in range(len(pieces)):
#     writeGrayIm("../output/%s.bmp" % i, pieces[i])




#---------- testing insureWhySpace ----------------------------
#
# im = readGrayIm("../images/couple.bmp")
# centralInd = im.shape[0] / 2
# zeros = cl.findZeros(im[centralInd, :])
# space = zeros[2]
# (lefters, righters, centers) = cl.insureWrySpace(im, space, centralInd)
# om = im.copy()
# drawSeq(om, toPoints(centralInd, lefters))
# drawSeq(om, toPoints(centralInd, righters))
# drawSeq(om, toPoints(centralInd, centers))
# for i in range(len(lefters)):
#     print("(%s,%s,%s)" % (lefters[i], centers[i], righters[i]))
#
# writeGrayIm("../output/couple.bmp", om)


