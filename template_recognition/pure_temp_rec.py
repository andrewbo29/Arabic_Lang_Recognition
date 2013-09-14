import cv2
import numpy


THRESHOLD = 0.075


def simpleCompareImages(image1, image2):
    val = numpy.mean(abs(image1 - image2))
    if val <= THRESHOLD:
        return True
    return False


def templateRecognition(line, templ, resultPath, colour):
    height = templ.shape[0]
    width = templ.shape[1]
    newImage = cv2.imread(resultPath, cv2.CV_LOAD_IMAGE_COLOR)

    beginCol = line.shape[1] - 1
    endCol = beginCol - width + 1
    while endCol >= 0:
        image = line[:, range(endCol, beginCol + 1)]
        if simpleCompareImages(image, templ):
            cv2.rectangle(newImage, (endCol, 0), (beginCol, height - 1), colour, thickness=2)
        beginCol -= 1
        endCol -= 1
    cv2.imwrite(resultPath, newImage)


def makeOCR(lines, templates, colours):
    for index in range(0, len(lines)):
        for i in range(0, len(templates)):
            resultPath = "../images/results/line_" + str(index) + ".bmp"
            templateRecognition(lines[index], templates[i], resultPath, colours[i])
