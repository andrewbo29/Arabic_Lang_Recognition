from template_recognition.util import *
from template_recognition.pure_temp_rec import *


def getRectangleColours():
    colours = [(255, 255, 0, 0), (48, 213, 200, 0), (48, 213, 200, 0), (123, 63, 0, 0),
               (0, 0, 255, 0), (255, 0, 0, 0), (0, 255, 0, 0), (58, 117, 196, 0),
               (215, 125, 49, 0), (255, 71, 202, 0), (139, 0, 255, 0), (139, 0, 255, 0)]
    return colours


def getTemplates():
    templates = []
    for i in range(1, 13):
        path = "../images/train_data/" + str(i) + ".bmp"
        templates.append(readGrayIm(path))
    return templates


def getLines():
    lines = []
    for i in range(0, 7):
        lines.append(readGrayIm("../images/lines/line_" + str(i) + ".bmp"))
    return lines


makeOCR(getLines(), getTemplates(), getRectangleColours())
