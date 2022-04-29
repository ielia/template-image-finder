from .algorithms import ALGORITHM_BF, ALGORITHM_FLANN
from .detectors import DETECTOR_BRIEF, DETECTOR_ORB, DETECTOR_SIFT, DETECTOR_PARAM_SPECS
from .match_filters import MATCH_FILTERING_PARAM_SPECS
from .matchers import MATCHING_METHOD_BEST, MATCHING_METHOD_KNN, MATCHING_METHOD_RADIUS, MATCHER_PARAM_SPECS, \
    MATCHING_METHOD_PARAM_SPECS
from .plotting import plot
from image_filters.color_space import COLOR_PARAM_SPECS


ALGORITHM_PARAMS = {
    ALGORITHM_BF: {
        'detector': {'type': str, 'options': [DETECTOR_BRIEF, DETECTOR_ORB, DETECTOR_SIFT], 'default': DETECTOR_ORB},
        'matching_method': {'type': str, 'options': [MATCHING_METHOD_BEST, MATCHING_METHOD_KNN, MATCHING_METHOD_RADIUS],
                            'default': MATCHING_METHOD_BEST},
    },
    ALGORITHM_FLANN: {
        'detector': {'type': str, 'options': [DETECTOR_BRIEF, DETECTOR_ORB, DETECTOR_SIFT], 'default': DETECTOR_SIFT},
        'matching_method': {'type': str, 'options': [MATCHING_METHOD_BEST, MATCHING_METHOD_KNN, MATCHING_METHOD_RADIUS],
                            'default': MATCHING_METHOD_KNN},
    },
}

PARAMETER_SPECS = {
    'algorithms': [ALGORITHM_BF, ALGORITHM_FLANN],
    'parameters': [
        {'': {'all': COLOR_PARAM_SPECS}},
        {'algorithm': ALGORITHM_PARAMS},
        {'detector': DETECTOR_PARAM_SPECS},
        {'algorithm': MATCHER_PARAM_SPECS},
        {'matching_method': MATCHING_METHOD_PARAM_SPECS},
        *MATCH_FILTERING_PARAM_SPECS,
    ],
    'plot_functions': {
        ALGORITHM_BF: plot,
        ALGORITHM_FLANN: plot,
    },
}
