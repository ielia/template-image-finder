import cv2
import numpy
import sys
from .detectors import create_detector
from .match_filters import filter_matches
from .matchers import MATCHING_METHOD_BEST, MATCHING_METHOD_KNN, MATCHING_METHOD_RADIUS, create_matcher, use_matcher
from image_filters.color_space import change_color_space_from_bgr
from timer import Timer
from utils import plot_empty_match, print_traceback


def plot(base_image, query_image, algorithm: str, color_space: str, detector: str, matching_method: str,
         match_filters_by: str, **kwargs):
    matches_image = None
    timer = Timer()
    timer.start()
    try:
        working_base_image, working_query_image = change_color_space_from_bgr(color_space, [base_image, query_image])
        timer.mark(f'Color space change BGR->{color_space}')
        detector_object = create_detector(detector, **kwargs)
        timer.mark(f'Detector {detector} creation')
        # TODO: second argument to detectAndCompute is the mask... might be worth trying later.
        base_kp, base_desc = detector_object.detectAndCompute(working_base_image, None)
        timer.mark('Base feature detection')
        query_kp, query_desc = detector_object.detectAndCompute(working_query_image, None)
        timer.mark('Query feature detection')
        matcher_object = create_matcher(algorithm, **kwargs)
        timer.mark(f'{algorithm} matcher creation')
        matches = use_matcher(matcher_object, matching_method, base_kp, base_desc, query_kp, query_desc, **kwargs)
        timer.mark(f'{algorithm} matching')
        filtered_matches = filter_matches(match_filters_by, matching_method, matches, **kwargs)
        timer.mark(f'Filter matches by {match_filters_by}')
        matches_image = plot_matches_and_outline(working_base_image, base_kp, working_query_image, query_kp,
                                                 filtered_matches, matching_method)
        timer.mark('Plotting')
    except:
        print_traceback(sys.exc_info())
        timer.mark('Exception handling')
        matches_image = plot_empty_match(base_image, query_image)
        timer.mark('Empty matches image creation')
    return {'duration': timer.stop(), 'image': matches_image}


def plot_knn_matches(base, base_kp, query, query_kp, matches: list[list[cv2.DMatch]]):
    return cv2.drawMatchesKnn(base, base_kp, query, query_kp, matches, None,
                              flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)


def plot_matches(base, base_kp, query, query_kp, matches: list[list[cv2.DMatch]]):
    return cv2.drawMatches(base, base_kp, query, query_kp, matches, None,
                           flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)


def plot_matches_and_outline(base, base_kp, query, query_kp, matches: list[list[cv2.DMatch]], match_shape: str):
    result_image = MATCH_PLOTTERS[match_shape](base, base_kp, query, query_kp, matches)
    try:
        src_pts = numpy.float32([query_kp[m[0].trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = numpy.float32([base_kp[m[0].queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        t_matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        qh, qw = query.shape[:2]
        pts = numpy.float32([[0, 0], [0, qh - 1], [qw - 1, qh - 1], [qw - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, t_matrix)
        result_image = cv2.polylines(result_image, [numpy.int32(dst)], True, (0, 0, 255), 3, cv2.LINE_AA)
    except:
        print_traceback(sys.exc_info())
    return result_image


MATCH_PLOTTERS = {
    MATCHING_METHOD_BEST: plot_matches,
    MATCHING_METHOD_KNN: plot_knn_matches,
    MATCHING_METHOD_RADIUS: plot_matches,
}
