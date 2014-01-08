import numpy as np

_MAGIC_NUMBER_A = 2


def find_wry_space(zone, central_ind, central_space):
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
        if space is None:
            return None
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
        if space is None:
            return None
        spaces.append(space)
        if zone.im[ind, int(np.mean(space))] != 0:
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
    """find left and right border of horizontal space in given line (v_ind)
        if there is several of them"""
    zeros = _find_zeros(zone.im[v_ind, range(prev_space[0], prev_space[1])])
    if len(zeros) > 1:
        print("Expected 0 or 1 spaces at next line, but got %s" %
              [(z[0] + prev_space[0], z[1] + prev_space[0]) for z in zeros])
        max_length = 0
        zero = [0, 0]
        for z in zeros:
            if z[1] - z[0] > max_length:
                zero = z
    elif len(zeros) == 1:
        zero = zeros[0]
    else:
        return None
    right = zero[1] + prev_space[0]
    while right < zone.horizontal[1] and zone.im[v_ind, right] == 0:
        right += 1
    left = zero[0] + prev_space[0]
    while left >= zone.horizontal[0] and zone.im[v_ind, left] == 0:
        left -= 1
    return left + 1, right


def _find_zeros(a):
    """returns all sequences of zeros in given array"""
    zeros = []
    x = _find_zero(a, 0)
    while x is not None:
        zeros.append(x)
        if x[1] >= len(a):
            break
        x = _find_zero(a, x[1])
    return zeros


def _find_zero(a, s):
    """returns first sequence of zeros in given array from given index"""
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
        """extract image for the zone"""
        return self.im[self.vertical[0]:self.vertical[1], self.horizontal[0]:self.horizontal[1]]

    def absoluteZone(self, horizontal, vertical):
        """returns sub zone of the zone treating given indexes as absolute"""
        return Zone(self.im, horizontal, vertical)

    def relativeZone(self, horizontal, vertical):
        """returns sub zone of the zone treating given indexes as relative"""
        return Zone(self.im,
                    (self.horizontal[0] + horizontal[0], self.horizontal[1] + horizontal[1]),
                    (self.vertical[0] + vertical[0], self.vertical[1] + vertical[1]))
