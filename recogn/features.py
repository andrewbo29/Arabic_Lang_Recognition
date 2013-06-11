import numpy as np
import glob as gb

import scipy.cluster.vq as vq
import scipy.spatial.distance as sp_dist

import decompose.util as util


_SUB_SIZE = 8


class ImageToBlocks(object):
    @classmethod
    def sub_image(cls, im, v_from, h_from):
        h_to, v_to = h_from + _SUB_SIZE, v_from + _SUB_SIZE
        return im[v_from:v_to, h_from:h_to]

    @classmethod
    def gen_overlapping_blocks(cls, im):
        for v_i in range(im.shape[0] - _SUB_SIZE):
            for h_i in range(im.shape[1] - _SUB_SIZE):
                yield cls.sub_image(im, v_i, h_i)

    @classmethod
    def gen_non_overlapping_blocks(cls, im):
        for v_i in range(0, im.shape[0] - _SUB_SIZE, _SUB_SIZE):
            for h_i in range(0, im.shape[1] - _SUB_SIZE, _SUB_SIZE):
                yield cls.sub_image(im, v_i, h_i)
        if im.shape[0] % _SUB_SIZE:
            v_i = im.shape[0] - _SUB_SIZE
            for h_i in range(0, im.shape[1] - _SUB_SIZE, _SUB_SIZE):
                yield cls.sub_image(im, v_i, h_i)
        if im.shape[1] % _SUB_SIZE:
            h_i = im.shape[1] - _SUB_SIZE
            for v_i in range(0, im.shape[0] - _SUB_SIZE, _SUB_SIZE):
                yield cls.sub_image(im, v_i, h_i)
        if im.shape[0] % _SUB_SIZE and im.shape[1] % _SUB_SIZE:
            yield cls.sub_image(im, im.shape[0] - _SUB_SIZE, im.shape[1] - _SUB_SIZE)


class FeatureMaker(object):
    """
    Feature maker - extract features vector from input image
    At initialization it reads centroids (features) from specified path
    """

    def __init__(self, centroids_path):
        self.feature_images = [util.readGrayIm(path) for path in read_images(centroids_path)]

    def _similarity(self, a1, a2):
        return sp_dist.cosine(a1, a2)

    def _compute_similarities(self, im):
        max_similarities = np.zeros(len(self.feature_images))
        for block in ImageToBlocks.gen_non_overlapping_blocks(im):
            if sum(block) == 0:
                continue
            for i in range(len(self.feature_images)):
                max_similarities[i] = max(max_similarities[i], self._similarity(block, self.feature_images[i]))
        return max_similarities

    def makeFeatures(self, im, central_ind):
        ratio = im.shape[0] / im.shape[1]
        scale = im.shape[0]  # symbol height is more "stable" then its width
        upper_im = im[0:central_ind, :]
        lower_im = im[central_ind:im.shape[0], :]
        features = [ratio, scale]
        features.extend(self._compute_similarities(upper_im))
        features.extend(self._compute_similarities(lower_im))
        return features


class FeatureLearner(object):
    """
    Feature learner - learn features from input images via following steps
    1. read input images
    2. break them into 8x8 blocks
    3. transform 8x8 blocks into 64-dimensional vectors
    4. run K-means over these vectors
    5. write resulting centroids into output directory
    centroids are resulted features

    """

    def __init__(self, image_it):
        self.image_it = image_it

    def gen_blocks_from_all_images(self):
        for im in self.image_it:
            for block in ImageToBlocks.gen_overlapping_blocks(im):
                yield block

    def make_ndarray(self):
        data = [block for block in self.gen_blocks_from_all_images() if block.sum() > 0]
        print len(data)
        nd_data = np.zeros((len(data), _SUB_SIZE * _SUB_SIZE), dtype=float)
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
        c.resize((_SUB_SIZE, _SUB_SIZE))
        util.writeGrayIm(features_dir + "/%s.bmp" % i, c)
        i += 1


if __name__ == "__main__":
    learn_features("../images/lines", "some empty folder", 100500)
