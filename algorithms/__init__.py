from functools import reduce
from . import simple_convolution_matching, feature_matching

MODULES = [feature_matching, simple_convolution_matching]

ALL_VALID_SPEC_KEYS = ['default', 'max', 'min', 'nullable', 'options', 'step', 'type']
ALL_VALID_SPEC_TYPES = [bool, float, int, str]
NUMERICAL_SPEC_TYPES = [float, int]
OPTIONS_VALID_SPEC_KEYS = ['default', 'nullable', 'options', 'type']


def accumulate_parameter_specs(accumulator, parameter_specs):
    return {
        'algorithms': accumulator['algorithms'] + parameter_specs['algorithms'],
        # TODO: See if it would be worth cloning parameter specs so that settings would not be shared.
        'parameters': reduce(lambda acc, algorithm: {**acc, algorithm: parameter_specs['parameters']},
                             parameter_specs['algorithms'], accumulator['parameters']),
        'plot_functions': accumulator['plot_functions'] | parameter_specs['plot_functions'],
    }


# TODO: Break these up
def check_module_parameter_specs(module_name, parameter_specs):
    path = f'{module_name}.PARAMETER_SPECS'
    if sorted(parameter_specs.keys()) != ['algorithms', 'parameters', 'plot_functions']:
        raise Exception(f'There are unexpected keys in {path} object:', sorted(parameter_specs.keys()))
    algorithms = sorted(parameter_specs['algorithms'])
    if algorithms != sorted(parameter_specs['plot_functions'].keys()):
        raise Exception('There is a difference between the declared algorithms and the ones collected from '
                        f'{path}["plot_functions"].')
    collector = {'algorithm': {'type': str, 'options': algorithms}}
    path = f'{path}["parameters"]'
    for index, conditional in enumerate(parameter_specs['parameters']):
        if len(conditional.keys()) != 1:
            raise Exception(f'Invalid conditional parameters format at {path}[{index}]. '
                            'Multiple variables not allowed.')
        for condition_var, conditional_params in conditional.items():
            check_parameter_specs_conditional_branches(f'{path}[{index}]', condition_var, conditional_params, collector)


def check_parameter_specs_conditional_branch(path, condition_var, condition_value, params, collector):
    for key, spec in params.items():
        if key in collector and collector[key]['path'] != path:
            raise Exception(f'Parameter {path}["{condition_var}"]["{condition_value}"]["{key}"] is an overlap '
                            'of an earlier declaration.')
        check_spec(f'{path}["{condition_var}"]["{condition_value}"]["{key}"]', spec)
        collector[key] = spec.copy()
        collector[key]['path'] = path


def check_parameter_specs_conditional_branches(path, condition_var, conditional_params, collector):
    if condition_var in collector:
        for condition_value, params in conditional_params.items():
            if condition_value is None:
                if not collector['nullable']:
                    raise Exception(f'Parameter {path}["{condition_var}"] condition variable is not nullable.')
            if type(condition_value) != collector[condition_var]['type']:
                raise Exception(f'Parameter {path}["{condition_var}"] condition value "{condition_value}" has a '
                                'different type to the one that was declared.')
            if 'max' in collector[condition_var] and (condition_value < collector[condition_var]['min'] or
                                                      condition_value > collector[condition_var]['max']):
                raise Exception(f'Parameter {path}["{condition_var}"] condition value "{condition_value}" is outside '
                                'the declared range.')
            check_parameter_specs_conditional_branch(path, condition_var, condition_value, params, collector)
    elif condition_var == '':
        if len(conditional_params.keys()) != 1:
            raise Exception(f'Unconditional section {path} has multiple branches.')
        for condition_value, params in conditional_params.items():
            check_parameter_specs_conditional_branch(path, condition_var, condition_value, params, collector)
    else:
        raise Exception(f'Conditional section {path} reference previously undeclared parameter "{condition_var}".')


def check_spec(prefix: str, spec: dict):
    spec_keys = spec.keys()
    if any([spec_key not in ALL_VALID_SPEC_KEYS for spec_key in spec_keys]):
        raise Exception(f'There are invalid spec keys in {prefix}.')
    if 'type' not in spec:
        raise Exception(f'Spec {prefix} needs "type".')
    spec_type = spec['type']
    if spec_type not in ALL_VALID_SPEC_TYPES:
        raise Exception(f'Spec {prefix} type is not valid: "{spec_type}".')
    if 'default' not in spec:
        raise Exception(f'Spec {prefix} does not contain a default value.')
    spec_default = spec['default']
    if spec_default is None and ('nullable' not in spec or not spec['nullable']):
        raise Exception(f'Non-nullable spec {prefix} default value cannot be null.')
    if spec_default is not None and type(spec_default) != spec_type:
        raise Exception(f'Spec {prefix} default value is of a different type to the one declared.')
    if 'options' in spec:
        if any([spec_key not in OPTIONS_VALID_SPEC_KEYS for spec_key in spec_keys]):
            raise Exception(f'Spec {prefix}, containing options, has invalid keys.')
        if spec_default is not None and spec['default'] not in spec['options']:
            raise Exception(f'Spec {prefix} default value not in its declared options.')
    if (('max' in spec and 'min' not in spec)
            or ('max' not in spec and 'min' in spec)
            or ('step' in spec and ('max' not in spec or 'min' not in spec))
            or ('max' in spec and spec_type not in NUMERICAL_SPEC_TYPES)):
        raise Exception(f'Numerical spec {prefix} is invalid.')
    if (('max' in spec and type(spec['max']) != spec_type)
            or ('min' in spec and type(spec['min']) != spec_type)
            or ('step' in spec and type(spec['step']) != spec_type)):
        raise Exception(f'Numerical spec {prefix} configuration data types are invalid.')
    if 'max' in spec and spec_default is not None and (spec['min'] > spec_default or spec['max'] < spec_default):
        raise Exception(f'Spec {prefix} default value out of range.')


for algorithmic_module in MODULES:
    check_module_parameter_specs(algorithmic_module.__name__, algorithmic_module.PARAMETER_SPECS)

PARAMETER_SPECS = reduce(lambda acc, module: accumulate_parameter_specs(acc, module.PARAMETER_SPECS), MODULES,
                         {'algorithms': [], 'parameters': {}, 'plot_functions': {}})

# DEBUGGING:
# import json
# def json_default(obj):
#     if type(obj) in [type, type(lambda x: x)]:
#         return str(obj)
#     raise Exception(f'Non-serializable object found: {type(obj)}')
# print('PARAMETER_SPECS:', json.dumps(PARAMETER_SPECS, sort_keys=False, indent=4, default=json_default))
