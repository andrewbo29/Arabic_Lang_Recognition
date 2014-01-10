# -*- coding: UTF-8 -*-
from PIL import Image, ImageFont, ImageDraw
import numpy
import math

from bidi.algorithm import get_display

import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper
import decompose.xycuts as xycuts
import decompose.util as util
from decompose.util import writeGrayIm
from decompose.util import readGrayIm
from decompose.util import remakeDir
from decompose.util import makeDir
from decompose.space import Zone
import decompose.space as space


# print len(arabic_reshaper.ARABIC_GLYPHS.items())
# for k, v in arabic_reshaper.ARABIC_GLYPHS.items():
#     s = u' '.join(v[0:(len(v) - 1)])
#     print s
SIZE = 60
FONT = ImageFont.truetype("/home/obus/Downloads/trado.ttf", SIZE)


def unicode_to_image(uni):
    """
    переводит unicode в картинку (ваш КО)
    """
    image = Image.new("L", (SIZE * len(uni), SIZE * 2), 255)
    d_usr = ImageDraw.Draw(image)
    d_usr.text((20, 20), uni, fill=0, font=FONT)
    image.save("test.bmp")
    zone = Zone(readGrayIm("test.bmp"))
    zone = xycuts.cut_edges(zone)
    return zone.extract()


def words_from_line(line):
    """
    вытаскивае слова из строки
    """
    word_spaces, symbols_spaces, other_spaces = space.splitToSpaces(line)
    words = space.makeWords(line, word_spaces, [], [])
    words = [xycuts.cut_edges(w) for w in words]
    return words


def makeDictionary():
    """
    создает массив из глифов - юникод и его возможные варианты картинок
    """
    glyphs = []
    for v in arabic_reshaper.ARABIC_GLYPHS_LIST:
        for uni in v[0:(len(v) - 1)]:
            glyphs.append(Glyph(uni, unicode_to_image(uni)))
    return glyphs


class Glyph:
    """
    глиф - юникодный символ и варианты картинок
    """
    def __init__(self, uni, im):
        self.uni = uni
        self.im = im


def recognize_word(glyph_dict, word):
    """
    распознает слово, возвращает юникод
    """
    unicode_glyphs = []
    offset = 0
    while (word.horizontal[1] - word.horizontal[0] - 1) > offset:
        uni, width = recognize_glyph(glyph_dict, word, offset)
        unicode_glyphs.append(uni)
        offset += width
    return arabic_reshaper.reshape(u''.join(unicode_glyphs))


def recognize_glyph(glyph_dict, word, glyph_offset):
    """
    распознает первый символ (с учетом оффсета) в слове
    """
    best_match_glyph_uni_width = None
    best_score = -1
    for glyph in glyph_dict:
        glyph_im = glyph.im
        width = glyph_im.shape[1]
        im = word.relativeZone((word.width() - min(glyph_offset + width, word.width()), word.width() - glyph_offset),
                               (0, word.height()))
        im = xycuts.cut_edges(im).extract()
        score = im_dist(glyph_im, im)
        if score > 0 and score > best_score:
            best_score = score
            best_match_glyph_uni_width = (glyph.uni, width)
    if best_score == -1:
        print "Failed to recognize first glyph of word"
        best_match_glyph_uni_width = (u'-', 20)
    else:
        print best_score
    return best_match_glyph_uni_width


def im_dist(im1, im2):
    """
    расстояние между двумя картинками
    """
    min_width = min(im1.shape[1], im2.shape[1])
    min_height = min(im1.shape[0], im2.shape[0])
    sub_im1 = im1[0:min_height, 0:min_width]
    sub_im2 = im2[0:min_height, 0:min_width]
    similar = math.sqrt(numpy.sum(sub_im1 * sub_im2))
    total = max(numpy.sum(im1), numpy.sum(im2))
    return similar / total


#создаем строку

DIR = remakeDir("workDir/")
DICTIONARY = makeDir(DIR + "dict/")
RESULTS = makeDir(DIR + "results/")

image = Image.new("L", (500, 100), 255)
d_usr = ImageDraw.Draw(image)
reshaped_text = arabic_reshaper.reshape(u'الله يكون معك')
bidi_text = get_display(reshaped_text)
d_usr = d_usr.text((20, 20), bidi_text, fill=0, font=FONT)
image.save(DIR + "input.bmp")
input_image = Zone(readGrayIm(DIR + "input.bmp"))


glyph_dict = makeDictionary()
for i, glyph in enumerate(glyph_dict):
    writeGrayIm(DICTIONARY + "glyph_%s.bmp" % i, glyph.im)

words = words_from_line(input_image)

for index, w in enumerate(words):
    # печатаем распознанное
    writeGrayIm(RESULTS + "word_%s.bmp" % index, w.extract())
    writeGrayIm(RESULTS + "word_rec_%s.bmp" % index,
                     unicode_to_image(get_display(arabic_reshaper.reshape(recognize_word(glyph_dict, w)))))



# writeGrayIm("t1.bmp", unicode_to_image(''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5'])))
# writeGrayIm("t2.bmp", unicode_to_image(arabic_reshaper.reshape(u''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5']))))
# writeGrayIm("t3.bmp", unicode_to_image(get_display(arabic_reshaper.reshape(u''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5'])))))

