import numpy as np
import glob as gb

import scipy.cluster.vq as vq

import decompose.util as util


SUB_SIZE = 8


class FeatureLearner(object):
    def __init__(self, image_it):
        self.image_it = image_it

    def sub_image(self, im, v_from, h_from):
        h_to, v_to = h_from + SUB_SIZE, v_from + SUB_SIZE
        return im[v_from:v_to, h_from:h_to].flatten()

    def gen_sub_images(self, im):
        for v_i in range(im.shape[0] - SUB_SIZE):
            for h_i in range(im.shape[1] - SUB_SIZE):
                yield self.sub_image(im, v_i, h_i)

    def gen_sub_images_total(self):
        for im in self.image_it:
            for sub in self.gen_sub_images(im):
                yield sub

    def make_ndarray(self):
        data = [sub for sub in self.gen_sub_images_total() if sum(sub) > 0]
        print len(data)
        nd_data = np.zeros((len(data), SUB_SIZE * SUB_SIZE), dtype=float)
        for i in range(len(data)):
            nd_data[i, :] = data[i]
        return nd_data

    def clusterize(self, K):
        centers, labels = vq.kmeans2(self.make_ndarray(), k=K, iter=10, minit='points')
        return centers

    @classmethod
    def learn_features(cls, image_it, K):
        fl = FeatureLearner(image_it)
        return fl.clusterize(K)


def read_images(images_dir):
    images_files = gb.glob(images_dir + "/*.bmp")
    for iFile in images_files:
        yield util.readGrayIm(iFile)


def learn_features(images_dir, features_dir, K):
    centers = FeatureLearner.learn_features(read_images(images_dir), K)
    i = 0
    for c in centers:
        c.resize((SUB_SIZE, SUB_SIZE))
        util.writeGrayIm(features_dir + "/%s.bmp" % i, c)
        i += 1


learn_features("../images/lines", "some empty folder", 100500)
