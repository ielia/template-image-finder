import cv2
import sys
from .algorithms import ALGORITHM_BF, ALGORITHM_FLANN


MATCHING_METHOD_BEST = 'best'
MATCHING_METHOD_KNN = 'KNN'
MATCHING_METHOD_RADIUS = 'radius-based'
NORMALIZATION_TYPE_L1 = 'NORM_L1'
NORMALIZATION_TYPE_L2 = 'NORM_L2'
NORMALIZATION_TYPE_HAMMING = 'NORM_HAMMING'
NORMALIZATION_TYPE_HAMMING2 = 'NORM_HAMMING2'

MATCHER_PARAM_SPECS = {
    ALGORITHM_BF: {
        'norm_type': {
            'type': str,
            'options': [NORMALIZATION_TYPE_L1, NORMALIZATION_TYPE_L2, NORMALIZATION_TYPE_HAMMING,
                        NORMALIZATION_TYPE_HAMMING2],
            'default': NORMALIZATION_TYPE_HAMMING,
        },
        'cross_check': {'type': bool, 'nullable': True, 'default': None},
    },
    ALGORITHM_FLANN: {
        'trees': {'type': int, 'min': 1, 'max': 1000, 'step': 1, 'default': 100},
        'checks': {'type': int, 'min': 1, 'max': 1000, 'step': 1, 'default': 500},
    },
}

MATCHING_METHOD_PARAM_SPECS = {
    MATCHING_METHOD_BEST: {
        # No parameters needed for this method.
    },
    MATCHING_METHOD_KNN: {
        'k': {'type': int, 'min': 1, 'max': 10, 'step': 1, 'default': 1},  # TODO: See what range it has.
        # 'compactResult': {'type': bool, 'nullable': True, 'default': None},  # Only used for masks.
    },
    MATCHING_METHOD_RADIUS: {
        # TODO: See what range this one has.
        'maxDistance': {'type': float, 'min': 0.0, 'max': 1.0, 'step': 0.01, 'default': 0.5},
        # 'compactResult': {'type': bool, 'nullable': True, 'default': None},  # Only used for masks.
    },
}

NORMALIZATION_TYPES = {
    NORMALIZATION_TYPE_L1: cv2.NORM_L1,
    NORMALIZATION_TYPE_L2: cv2.NORM_L2,
    NORMALIZATION_TYPE_HAMMING: cv2.NORM_HAMMING,
    NORMALIZATION_TYPE_HAMMING2: cv2.NORM_HAMMING2,
}


def create_bruteforce_matcher(norm_type: str = 'NORM_HAMMING', cross_check: bool = None, **kwargs):
    return cv2.BFMatcher(NORMALIZATION_TYPES[norm_type], crossCheck=cross_check)


def create_flann_matcher(trees: int = 100, checks: int = 500, **kwargs):
    index_params = dict(algorithm=cv2.DESCRIPTOR_MATCHER_FLANNBASED, trees=trees)
    search_params = dict(checks=checks)
    return cv2.FlannBasedMatcher(index_params, search_params)


def create_matcher(matcher: str, **kwargs):
    return MATCHERS[matcher](**kwargs)


def use_best_matching(matcher, base_kp, base_desc, query_kp, query_desc, **kwargs):
    return matcher.match(base_desc, query_desc)


def use_knn_matching(matcher, base_kp, base_desc, query_kp, query_desc, k: int, **kwargs):
    if len(query_kp) <= 1:
        print(f'Insufficient number of Query KPs: {query_kp}', file=sys.stderr)
    return matcher.knnMatch(base_desc, query_desc, k=k) if len(query_kp) > 1 else []


def use_radius_best_matching(matcher, base_kp, base_desc, query_kp, query_desc, maxDistance: float, **kwargs):
    return matcher.radiusMatch(base_desc, query_desc, maxDistance=maxDistance)


def use_matcher(matcher, matching_method, base_kp, base_desc, query_kp, query_desc, **kwargs):
    return MATCHER_USES[matching_method](matcher, base_kp, base_desc, query_kp, query_desc, **kwargs)


MATCHER_USES = {
    MATCHING_METHOD_BEST: use_best_matching,
    MATCHING_METHOD_KNN: use_knn_matching,
    MATCHING_METHOD_RADIUS: use_radius_best_matching,
}

MATCHERS = {
    ALGORITHM_BF: create_bruteforce_matcher,
    ALGORITHM_FLANN: create_flann_matcher,
}
