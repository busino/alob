WART_COLOR = 'yellow'
NOSE_TAIL_COLOR = 'blue'
EYE_COLOR = 'fuchsia'

POINT_TYPE_COLOR_DICT = {
    'wart': WART_COLOR,
    'nose': NOSE_TAIL_COLOR,
    'tail': NOSE_TAIL_COLOR,
    'left_eye': EYE_COLOR,
    'right_eye': EYE_COLOR
    }

def type2color(v):
    return POINT_TYPE_COLOR_DICT.get(v, 'gray')