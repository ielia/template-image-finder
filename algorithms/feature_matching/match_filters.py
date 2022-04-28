from .matchers import MATCHING_METHOD_BEST, MATCHING_METHOD_KNN, MATCHING_METHOD_RADIUS

# TODO: Improve performance of match filtering.

MATCH_FILTERING_TOP_N = 'top N'
MATCH_FILTERING_RATIO = 'ratio threshold'

MATCH_FILTERING_PARAM_SPECS = [
    {'': {'all': {
        'match_filters_by': {'type': str, 'options': [MATCH_FILTERING_RATIO, MATCH_FILTERING_TOP_N],
                             'default': MATCH_FILTERING_TOP_N},
    }}},
    {'match_filters_by': {
        MATCH_FILTERING_RATIO: {'match_ratio_threshold': {'type': float, 'min': 0.01, 'max': 1.00, 'step': 0.01,
                                                          'default': 0.5}},
        MATCH_FILTERING_TOP_N: {'n_matches': {'type': int, 'min': 1, 'max': 100, 'step': 1, 'default': 10}},
    }},
]


def filter_matches_by_lowe(all_matches, match_ratio_threshold: float, **kwargs):
    return [match for match in all_matches if match.distance < match_ratio_threshold]


def filter_in_top_n_matches(all_matches, n_matches: int, **kwargs):
    return sorted(all_matches, key=lambda m: m.distance)[:n_matches]


def filter_pairs_by_lowe(all_matches, match_ratio_threshold: float, **kwargs):
    return [pair for pair in all_matches if pair[0].distance < match_ratio_threshold * pair[1].distance]


def filter_in_top_n_pairs(all_matches, n_matches: int, **kwargs):
    return sorted(all_matches, key=lambda m: m[0].distance)[:n_matches]


def filter_matches(match_filters_by: str, matching_method: str, all_matches, **kwargs):
    return MATCH_FILTERS[match_filters_by][matching_method](all_matches, **kwargs)


MATCH_FILTERS = {
    MATCH_FILTERING_RATIO: {
        MATCHING_METHOD_BEST: filter_matches_by_lowe,
        MATCHING_METHOD_KNN: filter_pairs_by_lowe,
        MATCHING_METHOD_RADIUS: filter_matches_by_lowe,
    },
    MATCH_FILTERING_TOP_N: {
        MATCHING_METHOD_BEST: filter_in_top_n_matches,
        MATCHING_METHOD_KNN: filter_in_top_n_pairs,
        MATCHING_METHOD_RADIUS: filter_in_top_n_matches,
    },
}
