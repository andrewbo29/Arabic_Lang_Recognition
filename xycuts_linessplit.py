import cv2
import numpy
from shutil import rmtree
from os import mkdir


rowsSum = lambda m : numpy.sum(m, 0)
colsSum = lambda m : numpy.sum(m, 1)


def binarize(path):
    bim = cv2.imread(path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    im = abs(bim / 255 - 1);
    return im
 

def xy_cuts(m):
    out = []
    tosplit = [m];
    itt = 0
    for b in tosplit:
        ls = cuts(b, itt % 2)
        [out.append(v) for v in split(b, ls, itt % 2)]
    itt += 1;
    return out        
       

def cuts(m, d):
    ssum = d == 1 and rowsSum or colsSum
    s = ssum(m)
    ls = []
    if s[0] > 0: 
        ls.append(0)
    for i in range(s.size - 1):
        if s[i] == 0 and s[i + 1] > 0:
            ls.append(i + 1)
        elif s[i] > 0 and s[i + 1] == 0:
            ls.append(i)                    
    if s[s.size - 1] > 0: 
        ls.append(s.size - 1)
    return ls




def split(m, ls, d):
    if d == 0:
        return [m[ls[2*i] : ls[2*i+1], :]  for i in range(len(ls) / 2)]
    elif d == 1:
        return [m[:, ls[2*i] : ls[2*i+1]]  for i in range(len(ls) / 2)]



def do_all_the_staff(imgfile, outpath):
    rmtree(outpath, 1)
    mkdir(outpath)
    mage = binarize(imgfile)
    out = xy_cuts(mage)
    for i in range(len(out)):
        cv2.imwrite(outpath + "/%s.bmp" % i, 255 - out[i])



def splitlines(imgfile):
    do_all_the_stuff(imfgile, imgfile + "_lines")



    



