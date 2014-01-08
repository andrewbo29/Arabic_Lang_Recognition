from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bidi.algorithm import get_display
import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper


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


def write_arabic_text(text, img_path):
    image = Image.new("L", (200, 200), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/home/obus/Downloads/trado.ttf", 60)
    draw.text((10, 10), text, fill=0, font=font)
    image.save(img_path, optimize=1)


def fix_arabic_text(line):
    unicod = arabic_reshaper.reshape(unicode(line[:-2], "utf-8"))
    return get_display(unicod)


if __name__ == '__main__':
    root = "/home/obus/study/candidate/arabic/code/"
    words_file = "/home/obus/study/candidate/arabic/Arabic-Wordlist-1.5/arabic-wordlist-1.5.txt"
    output = root + "output/symbols"
    words_output = root + "output/words"
    temp_output = output + "/temp.bmp"
    LIMIT = 10000
    freq_map = symbols_frequency_map(words_file)
    print len(freq_map)
    id = 0
    for line in open(words_file, 'rb'):
        id += 1
        print(id)
        word = fix_arabic_text(line)
        write_arabic_text(word, words_output + "/%s.bmp" % id)
        if id > LIMIT:
            pass



