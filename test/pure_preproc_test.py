from image_preprocessing.util import *
from image_preprocessing.pure_preproc import *
import template_recognition.pure_temp_rec as recognition
import shutil
from pure_temp_rec_test import *

PATH = "../images/text_input.bmp"
PATH_NORM = "../images/text_norm.bmp"
PATH_CENTRAL_LINE = "../images/text_central_line.bmp"

image = readGrayIm(PATH)
norm_image = normalizeImage(image)
writeGrayIm(PATH_NORM, norm_image)
writeGrayIm(PATH_CENTRAL_LINE, erodeImage(norm_image, STRUCT_SHAPE_CENTRAL_LNE))
splitDocumentLines(norm_image)

for ind in range(1, 7):
    src = "../images/lines/line_" + str(ind) + ".bmp"
    dst = "../images/results/line_" + str(ind) + ".bmp"
    shutil.copyfile(src, dst)
shutil.copyfile("../images/line_0.bmp", "../images/results/line_0.bmp")
shutil.copyfile("../images/line_0.bmp", "../images/lines/line_0.bmp")

recognition.makeOCR(getLines(), getTemplates(), getRectangleColours())
