import cv2
from utils import filter_dict_keys


DETECTOR_ORB = 'ORB'
DETECTOR_SIFT = 'SIFT'

DETECTOR_PARAM_SPECS = {
    DETECTOR_ORB: {
        'nfeatures': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'scaleFactor': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'nlevels': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'edgeThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'firstLevel': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'WTA_K': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'scoreType': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'patchSize': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'fastThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
    },
    DETECTOR_SIFT: {
        'nfeatures': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'nOctaveLayers': {'type': int, 'nullable': True, 'min': 1, 'max': 100, 'step': 1, 'default': None},
        'contrastThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'edgeThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'sigma': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
    },
}

DETECTORS = {
    'ORB': cv2.ORB_create,
    'SIFT': cv2.SIFT_create,
    # 'SURF': cv2.SURF_create,  # TODO: Find SURF implementation.
}


def create_detector(detector: str, **kwargs):
    filtered_kwargs = filter_dict_keys(kwargs, DETECTOR_PARAM_SPECS[detector].keys())
    return DETECTORS[detector](**filtered_kwargs)
