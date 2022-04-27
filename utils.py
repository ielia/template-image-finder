from collections.abc import Iterable
import numpy
import sys
import traceback


def collect_level(dictionary: dict, level: int):
    acc = {}
    if level > 0:
        for subdict in [collect_level(dictionary[key], level - 1) for key in dictionary]:
            acc = dict(acc, **subdict)
    else:
        acc = dictionary
    return acc


def filter_dict_keys(dictionary: dict, keys: Iterable[str]):
    new_dict = {}
    for key in keys:
        if key in dictionary:
            new_dict[key] = dictionary[key]
    return new_dict


def flat_map(xs):
    ys = []
    for x in xs:
        ys.extend(x)
    return ys


def plot_empty_match(base_image, query_image):
    bh, bw = base_image.shape[:2]
    qh, qw = query_image.shape[:2]
    matches_image = numpy.zeros((max(bh, qh), bw + qw, 3), numpy.uint8)
    matches_image[0:bh, 0:bw] = base_image[0:bh, 0:bw]
    matches_image[0:qh, bw:bw + qw] = query_image[0:qh, 0:qw]
    return matches_image


def print_traceback(exc_info):
    exc_type, exc_value, exc_traceback = exc_info
    traceback.print_tb(exc_traceback, file=sys.stderr)
