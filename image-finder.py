import argparse
import cv2
import glob
import os
import yaml
from gui.controls_window import ControlsWindow
from algorithms import PARAMETER_SPECS
from gui.plot_window import PlotWindow
from utils import filter_dict_keys, flat_map


KEY_BOTTOM_ARROW = 0x10000 * 0x28
KEY_ESC = 0x1B
KEY_F1 = 0x700000
KEY_F5 = 0x740000  # 0x700000 + 0x10000 * (5 - 1)
KEY_LEFT_ARROW = 0x10000 * 0x25
KEY_PG_DOWN = 0x10000 * 0x22
KEY_PG_UP = 0x10000 * 0x21
KEY_RIGHT_ARROW = 0x10000 * 0x27
KEY_SPACE = 0x20
KEY_UP_ARROW = 0x10000 * 0x26


def create_controls_window(base, query, query_index_ref, view_settings_ref, quitting_ref):
    controls_window = ControlsWindow(quitting_ref, PARAMETER_SPECS, view_settings_ref)
    return controls_window


def fill_param_blanks(parameter_specs, config_params):
    result = config_params.copy()
    for algorithm, conditionals in parameter_specs.items():
        for conditional in conditionals:
            for condition, params in conditional.items():
                for condition_value, specs in params.items():
                    if algorithm not in result:
                        if condition == '' or condition == 'algorithm':
                            result[algorithm] = fill_param_blanks_shallow(algorithm, specs, {})
                        else:
                            raise Exception(f'Invalid dependency in settings: "{algorithm}"."{condition}"')
                    elif condition == '' or condition == 'algorithm' or condition in result[algorithm]:
                        result[algorithm] = result[algorithm] | \
                                            fill_param_blanks_shallow(algorithm, specs, result[algorithm])
                    else:
                        raise Exception(f'Invalid dependency in settings: "{algorithm}"."{condition}"')
    return result


def fill_param_blanks_shallow(algorithm: str, conditional: dict, config_params: dict) -> dict:
    for key, spec in conditional.items():
        if key in config_params:
            if config_params[key] is None:
                if 'nullable' not in spec or not spec['nullable']:
                    raise Exception(f'Configuration value for "{algorithm}"."{key}" cannot be null/None.')
                del config_params[key]
            elif type(config_params[key]) != spec['type']:
                raise Exception(f'Configuration type for "{algorithm}"."{key}" has an invalid type.')
            elif 'options' in spec and config_params[key] not in spec['options']:
                raise Exception(f'Configuration value for "{algorithm}"."{key}" is invalid (not in available options).')
        elif spec['default'] is not None:
            config_params[key] = spec['default']
    if 'algorithm' in config_params and config_params['algorithm'] != algorithm:
        raise Exception(f'Configuration value for "{algorithm}"."algorithm" does not match key.')
    config_params['algorithm'] = algorithm
    return config_params


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--base', help='Base (canvas) image filename')
    ap.add_argument('-c', '--config', help='Configuration file', default='config.yaml')
    ap.add_argument('-q', '--query', nargs='+', help='Query image filename')
    ap.add_argument('-w', '--window-dimensions', help='Window dimensions ("{width}x{height}", e.g.: "800x600")')
    args = vars(ap.parse_args())
    with open(args['config'], 'r', encoding='utf-8') as f:
        data = yaml.load(f.read(), yaml.Loader)
        if not args['base']:
            assert 'base' in data, 'Need base filename either on command line or in config file.'
            args['base'] = data['base']
        base = args['base']
        assert base, 'Need base filename either on command line or in config file.'
        assert os.path.isfile(base) and os.access(base, os.R_OK), f'File {base} does not exist or is not readable.'
        if not args['query']:
            args['query'] = data['query']
        assert args['query'], 'Need query path list either on command line or in config file.'
        args['query'] = flat_map([glob.glob(query) for query in args['query']])
        assert 'parameters' in data, 'Must specify parameters.'
        args['parameters'] = data['parameters']
        args['algorithm'] = next(iter(data['parameters'].keys())) if len(data['parameters'].keys()) > 0 \
            else 'Match Template'
        if args['window_dimensions'] is not None:
            data['dimensions'] = [int(size) for size in args['window_dimensions'].split('x')]
        args['config_data'] = data
    return args


def load_images(base_filename: str, query_filenames: list[str]):
    return [
        {'filename': base_filename, 'image': cv2.imread(base_filename, -1)},
        [{'filename': query_filename, 'image': cv2.imread(query_filename, -1)} for query_filename in query_filenames]
    ]


def main():
    args = get_args()
    base, query = load_images(args['base'], args['query'])
    query_index = {'query_index': 0}
    plot_window_args = filter_dict_keys(args['config_data'], ['center', 'dimensions', 'scale'])
    plot_window = PlotWindow(**plot_window_args)
    view_settings = {
        'all': fill_param_blanks(PARAMETER_SPECS['parameters'], args['parameters']),
    }
    view_settings['current'] = view_settings['all'][args['algorithm']]
    quitting_ref = {'quitting': False}
    controls_window = create_controls_window(base, query, query_index, view_settings, quitting_ref)
    run_plots(plot_window, controls_window, base, query, query_index, view_settings, quitting_ref)
    controls_window.destroy()


def plot(base_image, query_image, algorithm: str, **kwargs):
    return PARAMETER_SPECS['plot_functions'][algorithm](base_image, query_image, algorithm, **kwargs)


def run_plots(plot_window, controls_window, base, query, query_index_ref, settings_ref, quitting_ref):
    last_index = None
    last_params = None
    last_window_dimensions = None
    while plot_window.is_open() and not quitting_ref['quitting']:
        if last_params != settings_ref['current'] or last_index != query_index_ref['query_index']:
            last_index = query_index_ref['query_index']
            last_params = settings_ref['current'].copy()
            last_window_dimensions = plot_window.get_window_dimensions()
            a_query = query[last_index]
            plot_window.set_loading()
            print('<><><><><> PARAMS:', last_params)
            plotted = plot(base['image'], a_query['image'], **last_params)
            controls_window.record_last_duration(plotted['duration'])
            plot_window.set_plot_image(plotted['image'], f'{base["filename"]} <-- {a_query["filename"]}')
            plot_window.unset_loading()
        elif last_window_dimensions != plot_window.get_window_dimensions():
            last_window_dimensions = plot_window.get_window_dimensions()
            plot_window.redraw()
        key = cv2.waitKeyEx(1)  # TODO: There has to be a better and more performant way to detect resizes
        if key in [KEY_LEFT_ARROW, KEY_PG_UP, KEY_UP_ARROW]:
            query_index_ref['query_index'] = (query_index_ref['query_index'] - 1) % len(query)
        elif key in [KEY_BOTTOM_ARROW, KEY_PG_DOWN, KEY_RIGHT_ARROW, KEY_SPACE]:
            query_index_ref['query_index'] = (query_index_ref['query_index'] + 1) % len(query)
        elif key in [KEY_ESC, ord('Q'), ord('q')]:
            quitting_ref['quitting'] = True
        elif key in [KEY_F5, ord('R'), ord('r')]:
            last_index = None
            last_params = None
        elif key in [KEY_F1, ord('?'), ord('H'), ord('h')]:
            print('====================================================')
            print('HELP')
            print('----------------------------------------------------')
            print('previous/next image: Arrows, PgUp/Down, Space (next)')
            print('quit:                Esc, q/Q')
            print('re-process:          F5, r/R')
            print('this help message:   F1, h/H, ?')
            print('====================================================')
        elif key >= 0:
            print('invalid key pressed:', key, '. Press F1 for help.')
    controls_window.destroy()
    plot_window.destroy()


if __name__ == '__main__':
    main()
