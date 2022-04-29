import cv2
from utils import filter_dict_keys


DETECTOR_BRIEF = 'BRIEF'
DETECTOR_ORB = 'ORB'
DETECTOR_SIFT = 'SIFT'

DETECTOR_PARAM_SPECS = {
    DETECTOR_BRIEF: {
        'maxSize': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'responseThreshold': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'lineThresholdProjected': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'lineThresholdBinarized': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'suppressNonmaxSize': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'bytes': {'type': int, 'nullable': True, 'min': 0, 'max': 100, 'step': 1, 'default': None},
        'use_orientation': {'type': bool, 'nullable': True, 'default': None},
    },
    DETECTOR_ORB: {
        'nfeatures': {'type': int, 'nullable': True, 'min': 0, 'max': 1000, 'step': 1, 'default': None},
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
        'nfeatures': {'type': int, 'nullable': True, 'min': 0, 'max': 1000, 'step': 1, 'default': None},
        'nOctaveLayers': {'type': int, 'nullable': True, 'min': 1, 'max': 100, 'step': 1, 'default': None},
        'contrastThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'edgeThreshold': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
        'sigma': {'type': float, 'nullable': True, 'min': 0.0, 'max': 100.0, 'step': 1.0, 'default': None},
    },
}


# noinspection PyPep8Naming
class BRIEFDetector:
    # maxSize=45, responseThreshold=30, lineThresholdProjected=10, lineThresholdBinarized=8, suppressNonmaxSize=5
    # bytes=32, use_orientation=false
    def __init__(self, maxSize: int = None, responseThreshold: int = None, lineThresholdProjected: int = None,
                 lineThresholdBinarized: int = None, suppressNonmaxSize: int = None, bytes: int = None,
                 use_orientation: bool = None):
        # Initiate STAR detector
        self._star = cv2.xfeatures2d.StarDetector_create(maxSize=maxSize, responseThreshold=responseThreshold,
                                                         lineThresholdProjected=lineThresholdProjected,
                                                         lineThresholdBinarized=lineThresholdBinarized,
                                                         suppressNonmaxSize=suppressNonmaxSize)
        # Initiate BRIEF extractor
        self._brief = cv2.xfeatures2d.BriefDescriptorExtractor_create(bytes=bytes, use_orientation=use_orientation)

    def detectAndCompute(self, image, mask=None):
        # find the keypoints with STAR
        kp = self._star.detect(image, mask)
        # compute the descriptors with BRIEF
        return self._brief.compute(image, kp)


DETECTORS = {
    'BRIEF': BRIEFDetector,
    'ORB': cv2.ORB_create,
    'SIFT': cv2.SIFT_create,
    # 'SURF': cv2.SURF_create,  # TODO: Find SURF implementation.
}


def create_detector(detector: str, **kwargs):
    filtered_kwargs = filter_dict_keys(kwargs, DETECTOR_PARAM_SPECS[detector].keys())
    return DETECTORS[detector](**filtered_kwargs)
