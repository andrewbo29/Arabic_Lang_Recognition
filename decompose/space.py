__author__ = 'obus'
from exceptions import ValueError
import numpy as np
import xycuts
from util import writeGrayIm

_MAGIC_NUMBER_A = 2
_MAGIC_NUMBER_B = 0.75


# ----------------- wry spaces --------------------

def doSplit(line):
    """split given zone (seems to be a line of text) and returns
    list of words each one interpreted"""
    line = xycuts.cut_edges(line)
    central_ind = _central_ind(line)
    central_spaces = _find_central_spaces(line, central_ind)
    straight_spaces, other_spaces = _filter_straight_spaces(line, central_spaces)
    word_spaces, symbol_spaces = _filter_word_spaces(line, straight_spaces)
    wry_slices = _filter_wry_spaces(line, central_ind, other_spaces)
    return _makeWords(line, word_spaces, symbol_spaces, wry_slices)


def _find_central_spaces(line, central_ind):
    zeros = _find_zeros(line.im[central_ind, line.horizontal[0]:line.horizontal[1]])
    return [(z[0] + line.horizontal[0], z[1] + line.horizontal[0]) for z in zeros]


def _central_ind(zone):
    rsum = np.sum(zone.extract(), 1)
    maxInd = np.argmax(rsum)
    return maxInd + zone.vertical[0]


def _makeWords(line, word_spaces, symbols_spaces, wry_slices):
    """slow stupid and unreadable realization
    assume that symbol space could not start from left border or/and ends at right border"""
    _to_slice = lambda x: [x] * (line.vertical[1] - line.vertical[0])
    word_borders = _spaces_to_borders(line, word_spaces)
    symbols_ind = 0
    wry_ind = 0
    words = []
    for word_border in word_borders:
        symbols = []
        left_edge = _to_slice(word_border[0])
        while True:
            symbols_min, symbols_max = symbols_ind < len(symbols_spaces) and \
                (symbols_spaces[symbols_ind][0], symbols_spaces[symbols_ind][0]) or (-1, -1)
            wry_min, wry_max = wry_ind < len(wry_slices) and \
                (np.min(wry_slices[wry_ind]), np.max(wry_slices[wry_ind])) or (-1, -1)
            if wry_min == -1 and symbols_min == -1:
                right_edge = _to_slice(word_border[1])
                symbols.append(_edge_to_symbols(line, left_edge, right_edge))
                break
            if symbols_min != -1 and symbols_max < word_border[1] and \
                    (wry_min == -1 or symbols_min < wry_min):
                right_edge = _to_slice(symbols_spaces[symbols_ind][0])
                symbols.append(_edge_to_symbols(line, left_edge, right_edge))
                left_edge = _to_slice(symbols_spaces[symbols_ind][1])
                symbols_ind += 1
            elif wry_min != -1 and wry_max < word_border[1] and \
                    (symbols_min == -1 or wry_min < symbols_min):
                right_edge = wry_slices[wry_ind]
                symbols.append(_edge_to_symbols(line, left_edge, right_edge))
                left_edge = wry_slices[wry_ind]
                wry_ind += 1
            else:
                right_edge = _to_slice(word_border[1])
                symbols.append(_edge_to_symbols(line, left_edge, right_edge))
                break
        words.append(Word(symbols, line.im, word_border, line.vertical))
    return words


def _edge_to_symbols(zone, left_edge, right_edge):
    return Symbols(zone.im, zone.vertical, left_edge, right_edge)


def _filter_word_spaces(zone, straight_spaces):
    """find, which spaces separate words (rather than symbols) and return them"""
    lens = [s[1] - s[0] for s in straight_spaces]
    min_len = np.min(lens)
    max_len = np.max(lens)
    border = min_len + (max_len - min_len) * _MAGIC_NUMBER_B
    word_spaces = []
    symbols_spaces = []
    for space in straight_spaces:
        if space[0] == zone.horizontal[0] or space[1] == zone.horizontal[1]:
            word_spaces.append(space)
        elif space[1] - space[0] > border:
            word_spaces.append(space)
        else:
            symbols_spaces.append(space)
    return word_spaces, symbols_spaces


def _spaces_to_borders(zone, spaces):
    borders = []
    if spaces[0][0] == zone.horizontal[0]:
        from_ind = 1
        prev_border = spaces[0][1]
    else:
        from_ind = 0
        prev_border = zone.horizontal[0]
    for ind in range(from_ind, len(spaces)):
        borders.append((prev_border, spaces[ind][0]))
        prev_border = spaces[ind][1]
    if prev_border != zone.horizontal[1]:
        borders.append((prev_border, zone.horizontal[1]))
    return borders


def _filter_wry_spaces(zone, central_ind, central_spaces):
    wry_spaces = []
    for space in central_spaces:
        wry_space = _find_wry_space(zone, central_ind, space)
        if wry_space is not None:
            wry_spaces.append(wry_space)
    return wry_spaces


def _filter_straight_spaces(zone, central_spaces):
    """split given spaces on straight and non-straight"""
    straight_spaces = []
    other_spaces = []
    for space in central_spaces:
        straight = _insure_space(zone, space)
        if straight is not None:
            straight_spaces.append(straight)
        else:
            other_spaces.append(space)
    return straight_spaces, other_spaces


def _insure_space(zone, zero):
    """insure whether given zero interval contain split line
    and if it is - return ??????"""
    a = np.sum(zone.im[zone.vertical[0]:zone.vertical[1], zero[0]:zero[1]], 0)
    tsp = _find_zeros(a)
    if len(tsp) > 1:
        print("Warning: %s inner-spaces found" % len(tsp))
    if len(tsp) != 0:
        return tsp[0][0] + zero[0], tsp[0][1] + zero[0]


# ----------------- wry spaces --------------------

def _find_wry_space(zone, central_ind, central_space):
    """find wry line which separates two symbols from in specified zone"""
    lower_slice = _find_wry_space_down(zone, central_ind, central_space)
    if lower_slice is None:
        return None
    upper_slice = _find_wry_space_up(zone, central_ind, central_space)
    if upper_slice is None:
        return None
    slice = upper_slice
    slice.append(int(np.mean(central_space)))
    slice.extend(lower_slice)
    return slice


def _find_wry_space_up(zone, central_ind, central_space):
    """find wry line from central_ind to the upper border
     which separate two symbols"""
    spaces = [central_space]
    indexes = range(zone.vertical[0], central_ind - 1)
    indexes.reverse()
    for ind in indexes:
        prev_space = spaces[-1]
        space = _find_horizontal_line_space(zone, ind, prev_space)
        spaces.append(space)
        if zone.im[ind, int(np.mean(space))] != 0:
            """if there is non-zero pixel in center of 'space' then there is no 'why space'"""
            return None
        v_space = _find_vertical_space(zone, (space[0] + 1, space[1]), (zone.vertical[0], ind + 1))
        if v_space is not None:
            return _slice_up(zone, ind, spaces, v_space)
    raise Exception("There is no vertical space. Is it possible?")


def _find_wry_space_down(zone, central_ind, central_space):
    """find wry line from central_ind to the lower border
     which separate two symbols"""
    spaces = [central_space]
    for ind in range(central_ind + 1, zone.vertical[1]):
        prev_space = spaces[-1]
        space = _find_horizontal_line_space(zone, ind, prev_space)
        spaces.append(space)
        if zone.im[ind, int(np.mean(space))] != 0:
            """if there is non-zero pixel in center of 'space' then there is no 'why space'"""
            return None
        v_space = _find_vertical_space(zone, (space[0] + 1, space[1]), (ind, zone.vertical[1]))
        if v_space is not None:
            return _slice_down(zone, ind, spaces, v_space)
    raise Exception("There is no vertical space. Is it possible?")


def _slice_down(zone, ind, spaces, v_space):
    """slice zone by given spaces and vertical space from central_ind to down"""
    slice = [s[1] - 1 for s in spaces]
    slice.pop(0)
    v_ind = v_space[1] - 1
    for ind1 in range(ind, zone.vertical[1]):
        slice.append(v_ind)
    return slice


def _slice_up(zone, ind, spaces, v_space):
    """slice zone by given spaces and vertical space from central_ind to up"""
    slice = [s[1] - 1 for s in spaces]
    slice.pop(0)
    v_ind = v_space[1] - 1
    for ind1 in range(zone.vertical[0], ind):
        slice.append(v_ind)
    slice.reverse()
    return slice


def _find_vertical_space(zone, horizontal, vertical):
    """find vertical space borders in given zone"""
    sub_zone = zone.absoluteZone(horizontal, vertical).extract()
    spaces = _find_zeros(np.sum(sub_zone, 0))
    if spaces is None or len(spaces) == 0:
        return None
    space = spaces[-1]
    return space[0] + horizontal[0], space[1] + horizontal[0]


def _break_out(space, prev_space):
    left = space[0]
    right = space[1]
    prev_left = prev_space[0]
    prev_right = prev_space[1]
    if (right - left) / (prev_right - prev_left) > _MAGIC_NUMBER_A:
        left_break = abs(left - prev_left) > abs(right - prev_right)
        if left_break:
            return -1
        else:
            return +1
    return 0


def _find_horizontal_line_space(zone, v_ind, prev_space):
    """find left and right border of horizontal space in given line (v_ind)"""
    h_ind = int(np.mean(prev_space))
    right = h_ind + 1
    while right < zone.horizontal[1] and zone.im[v_ind, right] == 0:
        right += 1
    left = h_ind - 1
    while left >= zone.horizontal[0] and zone.im[v_ind, left] == 0:
        left -= 1
    return left, right


def _find_zeros(a):
    zeros = []
    x = _find_zero(a, 0)
    while x is not None:
        zeros.append(x)
        if x[1] >= len(a):
            break
        x = _find_zero(a, x[1])
    return zeros


def _find_zero(a, s):
    while s < len(a) and a[s] != 0:
        s += 1
    if s < len(a):
        start = s
        while s < len(a) and a[s] == 0:
            s += 1
        return start, s
    return None

class Zone:
    """Zone of image"""
    def __init__(self, im, horizontal=None, vertical=None):
        if horizontal is None:
            horizontal = (0, im.shape[1])
        if vertical is None:
            vertical = (0, im.shape[0])
        if horizontal[0] < 0 or vertical[0] < 0 or horizontal[1] > im.shape[1] or vertical[1] > im.shape[0]:
            raise ValueError("Horizontal %s, vertical %s." % (horizontal, vertical))
        self.im = im
        self.horizontal = horizontal
        self.vertical = vertical

    def extract(self):
        return self.im[self.vertical[0]:self.vertical[1], self.horizontal[0]:self.horizontal[1]]

    def absoluteZone(self, horizontal, vertical):
            return Zone(self.im, horizontal, vertical)

    def relativeZone(self, horizontal, vertical):
        return Zone(self.im,
                    (self.horizontal[0] + horizontal[0], self.horizontal[1] + horizontal[1]),
                    (self.vertical[0] + vertical[0], self.vertical[1] + vertical[1]))


class Word(Zone):
    """Word on image"""
    def __init__(self, symbols, im, horizontal=None, vertical=None):
        Zone.__init__(self, im, horizontal, vertical)
        self.symbols = symbols


class Symbols(Zone):
    """One or few connected symbols.
    This implementation is awful. Hope, it would be rewritten"""
    def __init__(self, im, vertical, left_edge, right_edge):
        """horizontal_left and horizontal_right"""
        if len(left_edge) != len(right_edge) or len(left_edge) != vertical[1] - vertical[0]:
            raise ValueError("Wrong unequal left_edge, right_edge lengths and vertical range")
        if min(left_edge) >= max(right_edge):
            raise ValueError("Minimum of left edge %s >= maximum of right edge %s"
                             % (min(left_edge), max(right_edge)))
        for ind in range(len(left_edge)):
            if left_edge[ind] >= right_edge[ind]:
                raise ValueError("Left edge >= right edge at index %s: %s, %s"
                                 % (ind, left_edge[ind], right_edge[ind]))
        self.im = im
        self.vertical = vertical
        self.left_edge = left_edge
        self.right_edge = right_edge

    def extract(self):
        min_edge = min(self.left_edge)
        max_edge = max(self.right_edge)
        om = np.zeros(shape=(self.vertical[1] - self.vertical[0], max_edge - min_edge))
        for ind in range(self.vertical[0], self.vertical[1]):
            rel_ind = ind - self.vertical[0]
            om[rel_ind, (self.left_edge[rel_ind] - min_edge):(self.right_edge[rel_ind] - min_edge)] = \
                self.im[ind, self.left_edge[rel_ind]:self.right_edge[rel_ind]]
        return om

    def relativeZone(self, horizontal, vertical):
        raise AttributeError("Not implemented yet")




