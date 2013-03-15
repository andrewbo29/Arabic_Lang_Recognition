# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import arabic_reshaper
import sys

THRESHOLD = 5
RESULT_PATH = 'result.doc'

def readImage(path):
    bim = cv2.imread(path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    im = abs(bim / 255 - 1)
    return im

def simpleCompareImages(image1, image2):
    val = np.mean(abs(image1 - image2))
    if val <= THRESHOLD:
        return True
    return False

def get_dictionary():
    arabicWords = [arabic_reshaper.reshape(u'وزارة'), arabic_reshaper.reshape(u'الشؤون'),
                   arabic_reshaper.reshape(u'الخارجيّة'), arabic_reshaper.reshape(u'شمس'),
                   arabic_reshaper.reshape(u'الله'), arabic_reshaper.reshape(u'نبي'),
                   arabic_reshaper.reshape(u'عام'), arabic_reshaper.reshape(u'مليون')]

    return arabicWords

def get_image_dictionary():
    arabicImagePaths = ["image_represent/word1.bmp", "image_represent/word2.bmp",
                        "image_represent/word3.bmp", "image_represent/word4.bmp",
                        "image_represent/word5.bmp", "image_represent/word6.bmp",
                        "image_represent/word7.bmp", "image_represent/word8.bmp"]

    return arabicImagePaths

def get_split_string(path):
    splitWords = ["image_represent/word1.bmp", "image_represent/word2.bmp",
                  "image_represent/word3.bmp"]

    return splitWords

def process(words, dictImages, dict):
    f = open(RESULT_PATH, 'w')
    resultStr = ''
    for i in range(0, len(words)):
        word = readImage(words[i])
        for j in range(0, len(dictImages)):
            wordDict = readImage(dictImages[j])
            if simpleCompareImages(word, wordDict):
                resultStr += dict[j] + ' '
    f.write(resultStr)
    f.close()
    print('Result: ' + resultStr)

reload(sys)
sys.setdefaultencoding('utf-8')

arabicWords = get_dictionary()
arabicImagePaths = get_image_dictionary()
words = get_split_string("input_image/input.bmp")
process(words, arabicImagePaths, arabicWords)