import cv2
import numpy
import sys
from image_filters.color_space import change_color_space_from_bgr, COLOR_BW
from timer import Timer
from utils import plot_empty_match, print_traceback


ALGORITHM = 'Match Template'

METHODS = {
    'TM_CCOEFF': {'enum': cv2.TM_CCOEFF, 'mult': -1},
    'TM_CCOEFF_NORMED': {'enum': cv2.TM_CCOEFF_NORMED, 'mult': -1},
    'TM_CCORR': {'enum': cv2.TM_CCORR, 'mult': -1},
    'TM_CCORR_NORMED': {'enum': cv2.TM_CCORR_NORMED, 'mult': -1},
    'TM_SQDIFF': {'enum': cv2.TM_SQDIFF, 'mult': 1},
    'TM_SQDIFF_NORMED': {'enum': cv2.TM_SQDIFF_NORMED, 'mult': 1},
}


def generate_plot(base_image, query_image, color_space, matches):
    bh, bw = base_image.shape[:2]
    qh, qw = query_image.shape[:2]
    plot_image = numpy.zeros((max(bh, qh), bw + qw), numpy.uint8) \
        if color_space == COLOR_BW else numpy.zeros((max(bh, qh), bw + qw, 3), numpy.uint8)
    plot_image[0:bh, 0:bw] = base_image
    plot_image[0:qh, bw:bw + qw] = query_image
    if color_space == COLOR_BW:
        plot_image = cv2.cvtColor(plot_image, cv2.COLOR_GRAY2BGR)
    for match in matches:
        location = match[0]
        value = match[1]
        bottom_right = (location[0] + qw, location[1] + qh)
        cv2.rectangle(plot_image, location, bottom_right, (0, int(value), 255 - int(value)), 5)
    return plot_image


def plot(base_image, query_image, algorithm: str, color_space: str, method: str, filter_by: str = None,
         n_matches: int = None, match_ratio_threshold: float = None):
    sorted_matches = []
    top_results = []
    timer = Timer()
    timer.start()
    try:
        working_base_image, working_query_image = change_color_space_from_bgr(color_space, [base_image, query_image])
        timer.mark(f'Color space change ({color_space})')
        match_result = cv2.matchTemplate(working_base_image, working_query_image, METHODS[method]['enum'])
        timer.mark('Convolution')
        if filter_by == 'number' and n_matches == 1:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
            sorted_matches = [[min_loc, min_val], [max_loc, max_val]]
        else:
            bw = working_base_image.shape[1]
            zipped_matches = [[(i // bw, i % bw), value] for i, value in enumerate(numpy.array(match_result).flatten())]
            sorted_matches = sorted(zipped_matches, key=lambda match: match[1])
        timer.mark('Match sorting')
        if METHODS[method]['mult'] > 0:
            sorted_matches = [[match[0], 255 - match[1]] for match in sorted_matches]
        else:
            sorted_matches = sorted_matches[::-1]
        timer.mark('Match adjustment')
        if filter_by == 'ratio':
            lbound = 255 * match_ratio_threshold
            top_results = [match for match in sorted_matches if match[1] >= lbound]
        timer.mark('Match rating')
        if n_matches is not None and len(top_results) < n_matches:
            top_results = sorted_matches[:n_matches]
        timer.mark('Match selection')
        matches_image = generate_plot(working_base_image, working_query_image, color_space, top_results)
        timer.mark('Plotting')
    except:
        print_traceback(sys.exc_info())
        timer.mark('Exception handling')
        matches_image = plot_empty_match(base_image, query_image)
        timer.mark('Empty matches image creation')
    return {'duration': timer.stop(), 'image': matches_image}
