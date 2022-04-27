import cv2


COLOR_BGR = 'BGR'
COLOR_BW = 'BW'

COLOR_PARAM_SPECS = {
    'color_space': {'type': str, 'options': [COLOR_BGR, COLOR_BW], 'default': COLOR_BGR},
}


def change_color_space_from_bgr(color_space: str, images: list) -> list:
    return images if color_space == COLOR_BGR else [cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) for image in images]
