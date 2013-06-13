__author__ = 'obus'
from bidi.algorithm import get_display

import simple_words_in_string_detection.arabic_reshaper as arabic_reshaper


reshaped_text = arabic_reshaper.reshape(u'اللغة العربية رائعة')
bidi_text = get_display(reshaped_text)
