__author__ = 'obus'
import numpy as np
from shutil import rmtree
from os import mkdir

import space as sspace
from util import readGrayIm, writeGrayIm
import xycuts


def intersects(space1, space2):
    """
    check, whether two spaces intersects or not
    example: [0,5] and [4, 10] intersects, but [0,5] and [6,10] not.
    """
    return \
        (space1[0] < space2[0] < space1[1]) or \
        (space1[0] < space2[0] and space2[1] < space1[1]) or \
        (space2[0] < space1[0] < space2[1]) or \
        (space2[0] < space1[0] and space1[1] < space2[1])


class WordSpace(object):
    """
    object incapsulate part of image contain word
    consist of methods and objects involved in finding and extracting symbols (letters and letters sequences)
    for the part of image
    """

    def __init__(self, line, word_space):
        self.line = line
        self.space = word_space
        self.straight_spaces = []
        self.wry_slices = []

    def __contains__(self, item):
        """
        does this word contains such space or not
        """
        return self.space[0] <= item[0] and item[1] <= self.space[1]

    def add_straight_space(self, straight_space):
        self.straight_spaces.append(straight_space)

    def check_wry_space(self, central_space):
        for straight in self.straight_spaces:
            if intersects(straight, central_space):
                raise BaseException("Illegal wry %s and straight %s spaces in word %s"
                                    % (central_space, straight, self.space))
        left_border = self.left_border_for_wry_space(central_space)
        right_border = self.right_border_for_wry_space(central_space)
        if left_border > central_space[0] or right_border < central_space[1]:
            print "Central space: ", central_space, \
                ", left border: ", left_border, \
                ", right border: ", right_border
            return
        wry_slice = self.find_wry_slice(central_space, (left_border, right_border))
        if wry_slice is None:
            return False
        self.wry_slices.append(wry_slice)
        return True

    def left_border_for_wry_space(self, central_space):
        seq = [s[1] for s in self.straight_spaces if s[1] < central_space[0]]
        return seq and max(seq) or self.space[0]

    def right_border_for_wry_space(self, central_space):
        seq = [s[0] for s in self.straight_spaces if central_space[1] < s[0]]
        return seq and min(seq) or self.space[1]

    def toWord(self):
        """
        transform self to sspace.Word object (finally extract symbols images)
        """
        start_space_list = []
        for straight in self.straight_spaces:
            start_space_list.append((min(straight), straight))
        for wry in self.wry_slices:
            start_space_list.append((min(wry), wry))
        start_space_list.sort()
        _to_slice = lambda x: [x] * (self.line.vertical[1] - self.line.vertical[0])
        symbols = []
        left_edge = _to_slice(self.space[0])
        for start_space in start_space_list:
            print start_space[0]
            space = start_space[1]
            if len(space) == 2:
                # means space is straight
                right_edge = _to_slice(space[0])
                symbols.append(self._edge_to_symbols(left_edge, right_edge))
                left_edge = _to_slice(space[1])
            else:
                # otherwise space is wry
                right_edge = space
                symbols.append(self._edge_to_symbols(left_edge, right_edge))
                left_edge = space
        symbols.append(self._edge_to_symbols(left_edge, _to_slice(self.space[1])))
        return sspace.Word(symbols, self.line.im, horizontal=self.space, vertical=self.line.vertical)

    def _edge_to_symbols(self, left_edge, right_edge):
        return sspace.Symbols(self.line.im, self.line.vertical, left_edge, right_edge)

    def find_wry_slice(self, central_space, borders):
        """find wry line which separates two symbols from in specified zone"""
        lower_slice = self._find_wry_space_down(central_space, borders)
        if lower_slice is None:
            return None
        upper_slice = self._find_wry_space_up(central_space, borders)
        if upper_slice is None:
            return None
        space_slice_map = {}
        for item in upper_slice:
            space_slice_map[item[0]] = item[1]
            #space_slice.append(int(np.mean(central_space)))
        for item in lower_slice:
            space_slice_map[item[0]] = item[1]
        space_slice = space_slice_map.values()
        return space_slice

    def _find_wry_space_up(self, central_space, borders):
        """find wry line from central_ind to the upper border
         which separate two symbols"""
        indexes = range(self.line.vertical[0], self.line.central_ind)
        indexes.reverse()
        return self._find_wry_space_in_range(central_space, borders, indexes)

    def _find_wry_space_down(self, central_space, borders):
        """find wry line from central_ind to the lower border
         which separate two symbols"""
        indexes = range(self.line.central_ind + 1, self.line.vertical[1])
        return self._find_wry_space_in_range(central_space, borders, indexes)

    def _find_wry_space_in_range(self, central_space, borders, indexes_range):
        """find wry line from central_ind to the upper border
         which separate two symbols"""
        spaces = [(self.line.central_ind, central_space)]
        # indexes = range(self.line.vertical[0], self.line.central_ind - 1)
        # indexes.reverse()
        for ind in indexes_range:
            prev_space = spaces[-1]
            space = self._find_horizontal_line_space(ind, prev_space[1], borders)
            if space is None:
                return None
            spaces.append((ind, space))
            if sum(self.line.im[ind, space[0]:space[1]]) != 0:
                #  if there is non-zero pixel in center of 'space' then there is no 'why space'
                return None
            v_from, v_to = min(ind, indexes_range[-1]), max(ind, indexes_range[-1])
            v_space = self._find_vertical_space(space, (v_from, v_to))
            if v_space is not None:
                return self._slice(spaces, v_space, v_from, v_to)
        raise Exception("There is no vertical space. Is it possible?")

    def _find_horizontal_line_space(self, v_ind, prev_space, borders):
        """find left and right border of horizontal space in given line (v_ind)
            if there is several of them"""
        zeros = sspace._find_zeros(self.line.im[v_ind, range(prev_space[0], prev_space[1])])
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

    def _slice(self, spaces, v_space, v_from, v_to):
        """slice zone by given spaces and vertical space from central_ind to up"""
        space_slice = [(s[0], s[1][1] - 1) for s in spaces]
        # space_slice.pop(0)
        v_ind = v_space[1] - 1
        for ind1 in xrange(v_from, v_to + 1):
            space_slice.append((ind1, v_ind))
            # space_slice.reverse()
        return space_slice

    def _find_vertical_space(self, horizontal, vertical):
        """find vertical space borders in given zone"""
        sub_zone = self.line.absoluteZone(horizontal, vertical).extract()
        spaces = sspace._find_zeros(np.sum(sub_zone, 0))
        if spaces is None or len(spaces) == 0:
            return None
        space = spaces[-1]
        return space[0] + horizontal[0], space[1] + horizontal[0]


class Splitter(object):
    def __init__(self, line):
        self.line = line

    def find_word_spaces(self):
        word_spaces, symbol_spaces, other_spaces = sspace.splitToSpaces(self.line)
        words = self.makeWords(word_spaces)
        self.add_straight_spaces(words, symbol_spaces)
        self.add_wry_spaces(words, other_spaces)
        return words
        # 1. object for each word space
        # 2. add symbols spaces to corresponding word space objects
        # 3. for all other spaces and corresponding word space object figure out, whether it is real space or not

    def add_straight_spaces(self, words, symbol_spaces):
        for symbol_space in symbol_spaces:
            for word in words:
                if symbol_space in word:
                    word.add_straight_space(symbol_space)
                    break

    def add_wry_spaces(self, words, other_spaces):
        for wry_space_candidate in other_spaces:
            accepted_count = 0
            for word in words:
                if word.check_wry_space(wry_space_candidate):
                    accepted_count += 1
            print "Wry space accepted %s times" % accepted_count

    def makeWords(self, word_spaces):
        start = self.line.horizontal[0]
        words = []
        for space in word_spaces:
            end = space[0]
            words.append(WordSpace(self.line, (start, end)))
            start = space[1]
        end = self.line.horizontal[1]
        words.append(WordSpace(self.line, (start, end)))
        return words


im = readGrayIm("../images/line_0.bmp")
im[im < 0.3] = 0
zone = sspace.Zone(im)
zone = xycuts.cut_edges(zone)
central_ind = sspace._central_ind(zone)
line = sspace.Line(zone.im, central_ind, horizontal=zone.horizontal, vertical=zone.vertical)
word_spaces = Splitter(line).find_word_spaces()
word_id = 0
output = "../output/"
rmtree(output)
mkdir(output)
for word_space in word_spaces:
    word = word_space.toWord()
    writeGrayIm(output + "word_%s.bmp" % word_id, word.extract())
    symbol_id = 0
    mkdir(output + "word_%s" % word_id)
    for symbol in word.symbols:
        writeGrayIm(output + "word_%s/symbol_%s.bmp" % (word_id, symbol_id), symbol.extract())
        symbol_id += 1
    word_id += 1
