from image_filters.color_space import COLOR_PARAM_SPECS
from .matcher import ALGORITHM, METHODS, plot


PARAMETER_SPECS = {
    'algorithms': [ALGORITHM],
    'parameters': [
        {'': {'all': COLOR_PARAM_SPECS}},
        {'': {'all': {
            'method': {
                'type': str,
                'options': list(METHODS.keys()),
                'default': 'TM_SQDIFF_NORMED',
            },
            'filter_by': {'type': str, 'options': ['number', 'ratio'], 'default': 'number'},
        }}},
        {'filter_by': {
            'number': {
                'n_matches': {'type': int, 'min': 1, 'max': 100, 'step': 1, 'default': 1},
            },
            'ratio': {
                'match_ratio_threshold': {'type': float, 'min': 0.01, 'max': 1.0, 'step': 0.01, 'default': 0.5},
            },
        }},
    ],
    'plot_functions': {
        ALGORITHM: plot,
    },
}
