# -*- coding: UTF-8 -*-
from PIL import Image, ImageFont, ImageDraw
import numpy
import math

from bidi.algorithm import get_display

import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper
import decompose.xycuts as xycuts
import decompose.util as util
from decompose.space import Zone
import decompose.space as space


print arabic_reshaper.DEFINED_CHARACTERS_ORGINAL_ALF
print arabic_reshaper.DEFINED_CHARACTERS_ORGINAL_ALF_UPPER_MDD
print arabic_reshaper.DEFINED_CHARACTERS_ORGINAL_ALF_LOWER_HAMAZA
print arabic_reshaper.DEFINED_CHARACTERS_ORGINAL_ALF_UPPER_HAMAZA
for k, v in arabic_reshaper.ARABIC_GLYPHS.items():
    s = u' '.join(v[0:(len(v) - 1)])
    print s

FONT = ImageFont.truetype("/home/obus/Downloads/trado.ttf", 60)


def unicode_to_image(uni):
    """
    переводит unicode в картинку (ваш КО)
    """
    image = Image.new("L", (100, 100), 255)#,ARABSWELL_1.TTF, resources/Ubuntu-R.ttf", 25)
    d_usr = ImageDraw.Draw(image)
    # reshaped_text = arabic_reshaper.reshape(u'اللغة العربية رائعة')
    #bidi_text = get_display(reshaped_text)
    d_usr = d_usr.text((20, 20), uni, fill=0, font=FONT)
    image.save("test.bmp")
    zone = Zone(util.readGrayIm("test.bmp"))
    zone = xycuts.cut_edges(zone)
    return zone.extract()


def words_from_line(line):
    """
    вытаскивае слова из строки
    """
    word_spaces, symbols_spaces, other_spaces = space.splitToSpaces(line)
    words = space.makeWords(line, word_spaces, [], [])
    return words


def makeDictionary():
    """
    создает массив из глифов - юникод и его возможные варианты картинок
    """
    glyphs = []
    for k, v in arabic_reshaper.ARABIC_GLYPHS.items():
        uni = k
        im_arr = [unicode_to_image(i) for i in v[0:(len(v) - 1)]]
        glyphs.append(Glyph(uni, im_arr))
    return glyphs


class Glyph:
    """
    глфи - юникодный символ и варианты картинок
    """

    def __init__(self, uni, im_array):
        self.uni = uni
        self.im_array = im_array


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
        for glyph_im in glyph.im_array:
            width = glyph_im.shape[1]
            im = word.relativeZone((glyph_offset, min(glyph_offset + width, word.horizontal[1] - word.horizontal[0])),
                                   (word.vertical[0], word.vertical[1] - word.vertical[0]))
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


# создаем строку

image = Image.new("L", (500, 100), 255)#,ARABSWELL_1.TTF, resources/Ubuntu-R.ttf", 25)
d_usr = ImageDraw.Draw(image)
reshaped_text = arabic_reshaper.reshape(u'سفن فييبترةزكحخ')
bidi_text = get_display(reshaped_text)
d_usr = d_usr.text((20, 20), bidi_text, fill=0, font=FONT)
image.save("input.bmp")
input_image = Zone(util.readGrayIm("input.bmp"))

glyph_dict = makeDictionary()
words = words_from_line(input_image)
for w in words:
    # печатаем распознанное
    print recognize_word(glyph_dict, w)


