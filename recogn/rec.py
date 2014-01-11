# -*- coding: UTF-8 -*-
import math

from PIL import Image, ImageDraw
import numpy
from scipy.stats import pearsonr

import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper
import decompose.xycuts as xycuts
from decompose.util import readGrayIm
from decompose.space import Zone
import decompose.space as space


SIZE = 60
FONT = None
MAX_OVERLAP = 0.3
MAX_SAME_OVERLAP = 0.2
THRESHOLD = 0.75


def dependencies_for_myprogram():


def unicode_to_image(uni):
    """
    переводит unicode в картинку (ваш КО)
    """
    image = Image.new("L", (int(SIZE * len(uni) * 2), SIZE * 3), 255)
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
    word_spaces = [ws for ws in word_spaces if ws[1] - ws[0] > SIZE / 10]
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
    for l in arabic_reshaper.LAM_ALEF_GLYPHS:
        for uni in l:
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


class Hit(object):
    def __init__(self, glyph, place, score):
        self.glyph = glyph
        self.place = place
        self.score = score

    def __cmp__(self, other):
        assert isinstance(other, Hit)
        return cmp(self.score, other.score)

    def __str__(self):
        return "%s : %s" % (self.place, self.score)


def intersection(space1, space2):
    if space1[0] <= space2[0] <= space1[1]:
        return min(space1[1], space2[1]) - space2[0]
    if space2[0] <= space1[0] <= space2[1]:
        return min(space1[1], space2[1]) - space1[0]
    return 0


def recognize_word_brute(glyph_dict, word):
    """
    распознает слово, возвращает юникод
    """
    glyphs_hits = []
    for glyph in glyph_dict:
        hits = find_glyph_hits_in_word_brute(glyph, word)
        if hits:
            glyphs_hits.append((glyph, hits))
    all_hits = []
    for glyph_hits in glyphs_hits:
        all_hits.extend(filter_overlapped_hits_for_same_glyph(glyph_hits[1]))
    all_ranked_hits = sorted(all_hits, reverse=True)
    non_overlapped_hits = filter_overlapped_hits(all_ranked_hits)
    non_overlapped_hits = sorted(non_overlapped_hits,
                                 cmp=lambda a, b: cmp(a.place[0], b.place[0]), reverse=True)
    return u''.join([hit.glyph.uni for hit in non_overlapped_hits])


def filter_overlapped_hits_for_same_glyph(hits):
    non_overlapped_hits = []
    for hit in hits:
        if not any([is_overlapped(no_hit.place, hit.place, MAX_SAME_OVERLAP) for no_hit in non_overlapped_hits]):
            non_overlapped_hits.append(hit)
    return non_overlapped_hits


def is_overlapped(place_a, place_b, max_overlap):
    overlap = float(intersection(place_a, place_b))
    overlap_rate = overlap / min(place_a[1] - place_a[0], place_b[1] - place_b[0])
    return overlap_rate > max_overlap


def filter_overlapped_hits(hits):
    for hit in hits:
        hit.score = hit.score * math.log(hit.place[1] - hit.place[0])
    hits = sorted(hits, reverse=True)
    non_overlapped_hits = []
    for hit in hits:
        if not any([is_overlapped(no_hit.place, hit.place, MAX_OVERLAP) for no_hit in non_overlapped_hits]):
            non_overlapped_hits.append(hit)
    return non_overlapped_hits


def find_glyph_hits_in_word_brute(glyph, word):
    # """
    # ищет вхождения глифа в слово
    # """
    glyph_width = glyph.im.shape[1]
    hits = []
    if word.width() < glyph_width:
        if glyph_width - word.width() == 1:
            glyph = Glyph(glyph.uni, glyph.im[:, 1:glyph_width])
            glyph_width -= 1
        elif glyph_width - word.width() == 2:
            glyph = Glyph(glyph.uni, glyph.im[:, 1:(glyph_width - 1)])
            glyph_width -= 2
        else:
            return []
    for right in range(word.width(), glyph_width - 1, -1):
        if sum(sum(word.relativeZone((right - 1, right)).extract())) == 0:
            continue
        left = right - glyph_width
        place = (left, right)
        im_zone = xycuts.cut_edges(word.relativeZone(horizontal=place))
        if im_zone.width() < 3 or im_zone.height() < 5:
            # print "WARN: too small image"
            continue
        dist = im_dist3(im_zone.extract(), glyph.im)
        if dist > THRESHOLD:
            # print dist
            hits.append(Hit(glyph, place, dist))
    return sorted(hits, reverse=True)


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
        # else:
    #     print best_score
    return best_match_glyph_uni_width


def im_dist(im1, im2):
    return im_dist1(im1, im2)


def im_dist1(im1, im2):
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


def im_dist2(im1, im2):
    """
    расстояние между двумя картинками
    """
    min_width = min(im1.shape[1], im2.shape[1])
    min_height = min(im1.shape[0], im2.shape[0])
    sub_im1 = im1[0:min_height, 0:min_width]
    sub_im2 = im2[0:min_height, 0:min_width]
    similar = numpy.sum(abs(sub_im1 - sub_im2))
    return similar / min_width / min_height


def im_dist3(im1, im2):
    """
    расстояние между двумя картинками
    """
    min_width = min(im1.shape[1], im2.shape[1])
    min_height = min(im1.shape[0], im2.shape[0])
    sub_im_array1 = im1[0:min_height, 0:min_width].flatten()
    sub_im_array2 = im2[0:min_height, 0:min_width].flatten()
    return pearsonr(sub_im_array1, sub_im_array2)[0]


#создаем строку

# DIR = remakeDir("workDir/")
# DICTIONARY = makeDir(DIR + "dict/")
# RESULTS = makeDir(DIR + "results/")
#
# image = Image.new("L", (500, 100), 255)
# d_usr = ImageDraw.Draw(image)
# # reshaped_text = arabic_reshaper.reshape(u'لا إله إلا الله')
# # reshaped_text = arabic_reshaper.reshape(u'الله يكون معك')
# reshaped_text = arabic_reshaper.reshape(u'لا إله إلا الله وأن محمدا رسول الله')
# bidi_text = get_display(reshaped_text)
# d_usr = d_usr.text((20, 20), bidi_text, fill=0, font=FONT)
# image.save(DIR + "input.bmp")
# input_image = Zone(readGrayIm(DIR + "input.bmp"))
#
#
# glyph_dict = makeDictionary()
# for i, glyph in enumerate(glyph_dict):
#     writeGrayIm(DICTIONARY + "glyph_%s.bmp" % i, glyph.im)
#
# words = words_from_line(input_image)
#
# for index, w in enumerate(words):
#     # печатаем распознанное
#     writeGrayIm(RESULTS + "%s_word.bmp" % index, w.extract())
#     writeGrayIm(RESULTS + "%s_word_rec.bmp" % index,
#                      unicode_to_image(get_display(arabic_reshaper.reshape(recognize_word_brute(glyph_dict, w)))))



# writeGrayIm("t1.bmp", unicode_to_image(''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5'])))
# writeGrayIm("t2.bmp", unicode_to_image(arabic_reshaper.reshape(u''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5']))))
# writeGrayIm("t3.bmp", unicode_to_image(get_display(arabic_reshaper.reshape(u''.join([u'\u3BA6', u'\uFEF6', u'\uFEF5'])))))

