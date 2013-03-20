import util
import split_to_strings
import recognition
import shutil

image = util.readGrayIm(split_to_strings.PATH)
norm_image = split_to_strings.normalizeImage(image)
util.writeGrayIm(split_to_strings.PATH_NORM, norm_image)
util.writeGrayIm(split_to_strings.PATH_CENTRAL_LINE, split_to_strings.erodeImage(norm_image,
                                                                                 split_to_strings.STRUCT_SHAPE_CENTRAL_LNE))
split_to_strings.splitDocumentLines(norm_image)

for ind in range(1, 7):
    src = "../images/lines/line_" + str(ind) + ".bmp"
    dst = "../images/results/line_" + str(ind) + ".bmp"
    shutil.copyfile(src, dst)
shutil.copyfile("../images/line_0.bmp", "../images/results/line_0.bmp")
shutil.copyfile("../images/line_0.bmp", "../images/lines/line_0.bmp")

recognition.makeOCR()
