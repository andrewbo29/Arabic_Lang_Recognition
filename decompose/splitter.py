__author__ = 'obus'
import numpy as np

import space


def intersects(space1, space2):
    return \
        (space1[0] < space2[0] < space1[1]) or \
        (space1[0] < space2[0] and space2[1] < space1[1]) or \
        (space2[0] < space1[0] < space2[1]) or \
        (space2[0] < space1[0] and space1[1] < space2[1])


class WordSpace(object):
    def __init__(self, line, word_space):
        self.line = line
        self.space = word_space
        self.straight_spaces = []

    def __contains__(self, item):
        return self.space[0] <= item[0] and item[1] <= self.space[1]

    def add_straight_space(self, straight_space):
        self.straight_spaces.append(straight_space)

    def check_wry_space(self, central_space):
        for straight in self.straight_spaces:
            if intersects(straight, central_space):
                raise BaseException("Illegal wry %s and straight %s spaces in word %s"
                                    % (central_space, straight, self.space))
        left_border = max((s[1] for s in self.straight_spaces if s[1] < central_space[0]))
        right_border = min((s[0] for s in self.straight_spaces if central_space[1] < s[0]))
        wry_space = self.find_wry_space(central_space, (left_border, right_border))

    def find_wry_space(self, central_space, borders):
        """find wry line which separates two symbols from in specified zone"""
        lower_slice = self._find_wry_space_down(central_space, borders)
        if lower_slice is None:
            return None
        upper_slice = self._find_wry_space_up(central_space)
        if upper_slice is None:
            return None
        slice = upper_slice
        slice.append(int(np.mean(central_space)))
        slice.extend(lower_slice)
        return slice

    def _find_wry_space_up(self, central_space, borders):
        """find wry line from central_ind to the upper border
         which separate two symbols"""
        spaces = [central_space]
        indexes = range(self.line.vertical[0], self.line.central_ind - 1)
        indexes.reverse()
        for ind in indexes:
            prev_space = spaces[-1]
            space = self._find_horizontal_line_space(ind, prev_space, borders)
            if space is None:
                return None
            spaces.append(space)
            if self.line.im[ind, int(np.mean(space))] != 0:
                """if there is non-zero pixel in center of 'space' then there is no 'why space'"""
                return None
            v_space = self._find_vertical_space(space, (self.line.vertical[0], ind + 1))
            if v_space is not None:
                return self._slice_up(zone, ind, spaces, v_space)
        raise Exception("There is no vertical space. Is it possible?")

    def _find_horizontal_line_space(self, v_ind, prev_space, borders):
        """find left and right border of horizontal space in given line (v_ind)
            if there is several of them"""
        zeros = space._find_zeros(self.line.im[v_ind, range(prev_space[0], prev_space[1])])

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
        while right < borders[1] and self.line.im[v_ind, right] == 0:
            right += 1
        left = zero[0] + prev_space[0]
        while left > borders[0] and self.line.im[v_ind, left] == 0:
            left -= 1
        if left < borders[0] or borders[1] < right:
            return None
        return left + 1, right

    def _slice_up(zone, ind, spaces, v_space):
        """slice zone by given spaces and vertical space from central_ind to up"""
        slice = [s[1] - 1 for s in spaces]
        slice.pop(0)
        v_ind = v_space[1] - 1
        for ind1 in range(zone.vertical[0], ind):
            slice.append(v_ind)
        slice.reverse()
        return slice

    def _slice(self, ind, spaces, v_space, v_from, v_to):
        """slice zone by given spaces and vertical space from central_ind to up"""
        slice = [s[1] - 1 for s in spaces]
        slice.pop(0)
        v_ind = v_space[1] - 1
        for ind1 in range(v_from, v_to):
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


class Splitter(object):
    def __init__(self, line):
        self.line = line

    def findWords(self):
        word_spaces, symbol_spaces, other_spaces = space.splitToSpaces(self.line)
        words = self.makeWords(word_spaces)
        # 1. object for each word space
        # 2. add symbols spaces to corresponding word space objects
        # 3. for all other spaces and corresponding word space object figure out, whether it is real space or not

    def makeWords(self, word_spaces):
        start = self.line.vertical[0]
        words = []
        for space in word_spaces:
            end = space[0]
            words.append(WordSpace(self.line, (start, end)))
            start = space[1]
        end = self.line.vertical[1]
        words.append(WordSpace(self.line, (start, end)))
        return words





