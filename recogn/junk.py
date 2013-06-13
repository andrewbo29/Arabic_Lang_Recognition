# coding=utf-8
__author__ = 'obus'

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from bidi.algorithm import get_display

import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper
import decompose.util
import decompose.xycuts
import decompose.space


# file = open("arabic-wordlist-1.5.txt", 'rb')
# file.readline()
# file.readline()
# file.readline()
# file.readline()
# file.readline()
# text = file.readline()[:-2]
# t = unicode(text, 'utf-8')
# i = Image.new("L", (60, 60))
# d = ImageDraw.Draw(i)
# f = ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", 20)
# d.text((10, 10), t, fill=255, font=f)
# i.save("/tmp/dummy.png", optimize=1)


def symbols_frequency_map(words_file):
    freq_map = {}
    for line in open(words_file, 'rb'):
        word = fix_arabic_text(line)
        for symbol in word:
            if symbol in freq_map:
                freq_map[symbol] += 1
            else:
                freq_map[symbol] = 1
    return freq_map


def fix_arabic_text(line):
    return get_display(arabic_reshaper.reshape(unicode(line[:-2], "utf-8")))


def _cut_edges(temp_parh, path):
    im = decompose.xycuts.cut_edges(
        decompose.space.Zone(
            decompose.util.readGrayIm(temp_parh)
        )
    ).extract()
    decompose.util.writeGrayIm(path, im)


temp_output = "temp.bmp"


def write_arabic_text(text, img_path):
    image = Image.new("L", (200, 200), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/home/obus/Downloads/trado.ttf", 60)
    draw.text((10, 10), text, fill=0, font=font)
    image.save(temp_output, optimize=1)
    _cut_edges(temp_output, img_path)


def split_to_symbols(word):
    write_arabic_text(word, temp_output)
    zone = decompose.xycuts.cut_edges(
        decompose.space.Zone(
            decompose.util.readGrayIm(temp_output)
        )
    )
    decompose.space.doSplit(zone)


if __name__ == '__main__':
    root = "/home/obus/study/candidate/arabic/code/"
    words_file = "/home/obus/study/candidate/arabic/Arabic-Wordlist-1.5/sample.txt"
    output = root + "output/symbols"
    words_output = root + "output/words"
    temp_output = output + "/temp.bmp"
    freq_map = symbols_frequency_map(words_file)
    print len(freq_map)
    # id = 0
    # for (symbol, freq) in sorted(freq_map.iteritems(), key=operator.itemgetter(1), reverse=True):
    #     write_arabic_text(symbol, temp_output)
    #     im = decompose.xycuts.cut_edges(
    #         decompose.space.Zone(
    #             decompose.util.readGrayIm(temp_output)
    #         )
    #     ).extract()
    #     decompose.util.writeGrayIm(output + "/%s_%s.bmp" % (id, freq), im)
    #     id += 1
    id = 0
    for line in open(words_file, 'rb'):
        id += 1
        if id % 10 != 9:
            continue
        word = fix_arabic_text(line)
        print len(word)
        write_arabic_text(word, words_output + "/%s.bmp" % id)
        if len(word) > 1:
            print split_to_symbols(word)




# reshaped_text = arabic_reshaper.reshape(u'اللغة العربية رائعة')
# bidi_text = get_display(reshaped_text)
# write_arabic_text(bidi_text, "word.bmp")
