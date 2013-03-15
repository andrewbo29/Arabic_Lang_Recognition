import cv
import cv2
from sets import Set
from random import randint as rand
from shutil import rmtree
from os import mkdir
import numpy as np
import copy as cp

def decompose(imagePath, outputPath):
    """decompose input image smaller parts"""
    """reading input image and extracting contours"""
    rmtree(outputPath)
    mkdir(outputPath)
    mkdir(outputPath + "/dummies")
    im = cv.LoadImageM(imagePath, cv.CV_LOAD_IMAGE_GRAYSCALE)
    seq = cv.FindContours(im, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_LINK_RUNS)
    #seq = cv.FindContours(im, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE)    
    ls = seq_to_list(seq)
    print("seq num: %s" % len(ls))
    ls = filter(lambda l : max(l)[0] - min(l)[0] < im.width / 2, ls)
    print("filtered of big seq num: %s" % len(ls))
    ls = filter(lambda l : max(l)[0] - min(l)[0] > 5, ls)
    print("filtered of big and small seq num: %s" % len(ls))
    ls.sort()
    cseqs = brute_crossing(ls)
    """writing crossed sorted sequences"""
    im_array = np.asarray(im[:,:])
    write_it_out_cv2(outputPath, im_array, sorted(cseqs, key = lambda cs : cs.min)) 
    total = CrossSeq(cseqs[0].cross[0])
    [total.addAll(cs.cross) for cs in cseqs]
    dummies = sorted([CrossSeq(l) for l in ls], key = lambda cs : cs.min)
    write_it_out_cv2(outputPath + "/dummies", im_array, dummies)
    cv2.imwrite(outputPath + "/total.bmp", makeIm(im_array, total))
    #cv.SaveImage(outputPath + "/total.bmp", total.makeCvMat())
    

def seq_to_list(seq):
    ls = []
    t = seq
    while t:
        ls.append(list(t))
        t = t.h_next()
    return ls


def brute_crossing(ls):
    """crossing in-list sequences horizontaly"""
    cseqs = []
    ll = filter(lambda l : max(l)[0] - min(l)[0] < 250, ls)
    ll.sort()
    for l in ll:
        crossed = filter(lambda cs : cs.intersects(l), cseqs)
        #print("Crossed num: %s" % len(crossed)) # debug code
        if len(crossed) > 1:
            cseqs = filter(lambda cs : not cs.intersects(l), cseqs)
            ncs = CrossSeq(l)
            [ncs.addAll(cs.cross) for cs in cseqs]
            cseqs.append(ncs)
        elif len(crossed) == 1:
            crossed[0].add(l)
        else:
            cseqs.append(CrossSeq(l))
    return cseqs     


def write_it_out(outputPath, cseqs):
    i = 0
    for cseq in cseqs:
        cv.SaveImage("%s/out%s.bmp" % (outputPath,i), cseq.makeCvMat())
        i += 1


def write_it_out_cv2(outputPath, source, cseqs):
    i = 0
    for cseq in cseqs:
        cv2.imwrite("%s/out%s.bmp" % (outputPath,i), makeIm(source, cseq))
        i += 1


class CrossSeq:
    def __init__(self, l):
        self.cross = [l]
        self.min = min(l)[0] 
        self.max = max(l)[0]
    def add(self, l):
        self.cross.append(l)
        self.min = min([min(l)[0], self.min])        
        self.max = max([max(l)[0], self.max])
    def addAll(self, ll):
        for l in ll:
            self.add(l)
    def intersects(self, l):
        lmin = min(l)[0]
        lmax = max(l)[0] 
        inter = float(min(self.max, lmax) - max(lmin, self.min)) 
        rng = float(max(self.max - self.min, lmax - lmin))
        return (not self.max <= lmin) and (not lmax <= self.min)
        #return inter/rng > 0.05
    def makeCvMat(self):
        """create cvMat object containing all crossed contours"""
        m = cv.CreateMat(100,self.max-self.min + 5, 22)#cv.CV_16UC3)#self.max - self.min, 100, cv.CV_16UC3)
        cv.Set(m, (255,255,255))
        for l in self.cross:
            points = [[(d[0] - self.min, d[1] - 0) for d in l]]
            cv.FillPoly(m, points, cv.RGB(0, 0, 0))#rand(0, 255),rand(0, 255),rand(0, 255)))
        return m
   


def makeIm(source, cs):
    #print("FUCCCCK!!")
    bounds = []
    #print("cross: %s" % len(cs.cross))
    for l in cs.cross:
        bound = bounding_rect(l)
        #print("bounds: %s" % bound)
        bounds.append(bound)
    rmin = min([i[0] for i in bounds])
    cmin = min([i[2] for i in bounds])
    rmax = max([i[1] for i in bounds])
    cmax = max([i[3] for i in bounds])
    #print([rmin,rmax,cmin,cmax])
    rlen = rmax - rmin
    clen = cmax - cmin
    #m = np.zeros((rlen,clen)) + 255; m = source[cmin:cmax,rmin:rmax]
    m = np.zeros(source.shape) + 255
    m[cmin:cmax,rmin:rmax] = source[cmin:cmax,rmin:rmax]
    return m


def bounding_rect(l):
    rs = [i[0] for i in l]
    cs = [i[1] for i in l]
    rmin = min(rs)
    rmax = max(rs)
    cmin = min(cs)
    cmax = max(cs)
    rl = rmax - rmin
    cl = cmax - cmin
    a = 1
    return [rmin - rl*a, rmax + rl*a, cmin - cl*a, cmax + cl*a]
    


decompose("arabic_borodion.bmp", "puppets") 
#decompose("inputText.bmp", "puppets") 



            


                     

