import cv2
import util
import numpy

PATH = "../images/text_input.bmp"
PATH_NORM = "../images/text_norm.bmp"
PATH_CENTRAL_LINE = "../images/text_central_line.bmp"

ANGLE_STEP = 5
ROW_BIAS = 10
COL_BIAS = 5

STRUCT_SHAPE_SPLITDOC = (4, 1)
STRUCT_SHAPE_CENTRAL_LNE = (7, 1)


def rotateImage(image, angle):
    image_center = tuple(numpy.array(image.shape) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    shape = (image.shape[1], image.shape[0])
    result = cv2.warpAffine(image, rot_mat, shape, flags=cv2.INTER_LINEAR)
    return result


def erodeImage(image, structElemShape):
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, structElemShape)
    result = cv2.erode(image, kernel)
    # util.writeGrayIm("smoothNoise.bmp", result)
    return result


def isVerticalRightLine(image):
    rightPixel = getRightPixel(image)

    if rightPixel == -1:
        return False

    rightRow = rightPixel[0]
    rightCol = rightPixel[1]
    for row in range(0, image.shape[0]):
        if not row == rightRow:
            if image[row, rightCol] == 1 or image[row, rightCol - COL_BIAS] == 1:
                if abs(rightRow - row) > ROW_BIAS:
                    return True

    return False


def getRightPixel(image):
    for col in range(image.shape[1] - 1, -1, -1):
        for row in range(0, image.shape[0]):
            if image[row, col] == 1:
                return row, col

    return -1, -1


def getRotateAngle(image):
    angle = 0
    newImage = image
    while not isVerticalRightLine(newImage):
        angle += ANGLE_STEP
        if angle >= 180:
            return 180
        newImage = rotateImage(image, angle)
        util.writeGrayIm("test_test.bmp", newImage)

    return angle


def normalizeImage(image):
    eroded = erodeImage(image, STRUCT_SHAPE_SPLITDOC)
    angle = getRotateAngle(eroded)
    result = rotateImage(image, angle)
    return result


def xy_cuts(m):
    out = []
    tosplit = [m]
    itt = 0
    for b in tosplit:
        ls = cuts(b, itt % 2)
        [out.append(v) for v in split(b, ls, itt % 2)]
    return out


rowsSum = lambda m: numpy.sum(m, 0)
colsSum = lambda m: numpy.sum(m, 1)


def cuts(m, d):
    ssum = d == 1 and rowsSum or colsSum
    s = ssum(m)
    ls = []
    if s[0] > 0:
        ls.append(0)
    for i in range(s.size - 1):
        if s[i] == 0 and s[i + 1] > 0:
            ls.append(i + 1)
        elif s[i] > 0 and s[i + 1] == 0:
            ls.append(i)
    if s[s.size - 1] > 0:
        ls.append(s.size - 1)
    return ls


def split(m, ls, d):
    if d == 0:
        return [m[ls[2 * i]: ls[2 * i + 1], :]for i in range(len(ls) / 2)]
    elif d == 1:
        return [m[:, ls[2 * i]: ls[2 * i + 1]]for i in range(len(ls) / 2)]


def splitDocumentLines(image):
    out = xy_cuts(image)
    for i in range(len(out)):
        fileLine = "../images/lines/line_" + str(i) + ".bmp"
        util.writeGrayIm(fileLine, out[i])


# image = util.readGrayIm(PATH)
# norm_image = normalizeImage(image)
# util.writeGrayIm(PATH_NORM, norm_image)
# util.writeGrayIm(PATH_CENTRAL_LINE, erodeImage(norm_image, STRUCT_SHAPE_CENTRAL_LNE))
# splitDocumentLines(norm_image)