__author__ = 'obus'
import numpy as np
import space as sp

_sum_horizontal = lambda m: np.sum(m, 0)
_sum_vertical = lambda m: np.sum(m, 1)


def cut_leftright(zone):
    """cut off left and right spaces"""
    hsum = _sum_horizontal(zone.extract())
    left_offset = 0
    while hsum[left_offset] == 0:
        left_offset += 1
    right_offset = len(hsum)
    while hsum[right_offset - 1] == 0:
        right_offset -= 1
    return sp.Zone(zone.im,
                horizontal=(zone.horizontal[0] + left_offset, zone.horizontal[0] + right_offset),
                vertical=zone.vertical)


def cut_topdown(zone):
    """cut off top and down spaces"""
    vsum = _sum_vertical(zone.extract())
    top_offset = 0
    while vsum[top_offset] == 0:
        top_offset += 1
    down_offset = len(vsum)
    while vsum[down_offset - 1] == 0:
        down_offset -= 1
    return sp.Zone(zone.im,
                horizontal=zone.horizontal,
                vertical=(zone.vertical[0] + top_offset, zone.vertical[0] + down_offset))


def cut_edges(zone):
    return cut_topdown(cut_leftright(zone))
