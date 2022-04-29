import threading
from tkinter import BooleanVar, BOTH, Checkbutton, DoubleVar, Entry, Frame, HORIZONTAL, IntVar, Label, LEFT, \
    OptionMenu, RIGHT, Scale, StringVar, Tk, X
from gui.components.VerticallyScrollableFrame import VerticallyScrollableFrame


ON_OFF_VARIABLE_NAME_SUFFIX = '_on/off'
PADDING_X = 10
PADDING_Y = 5


class FakeBooleanVar:
    def get(self):
        return True

    def trace_remove(self, *args):
        pass


class ControlsWindow:
    SETTING_WIDGET_CONSTRUCTORS = {
        bool: lambda self: self._build_bool_setting,
        float: lambda self: self._build_float_setting,
        int: lambda self: self._build_int_setting,
        str: lambda self: self._build_str_setting,
    }

    def __init__(self, quitting_ref, parameter_specs, initial_settings):
        self._algorithms = parameter_specs['algorithms']
        self._all_settings = initial_settings
        self._conditional_frames = []
        self._current_settings = {}
        self._last_algorithm = None
        self._last_process_duration = {}
        self._listeners = []
        self._main_frame = None
        # { alg: [ { modkey: { modval1: {}, ...} }, ...] }
        self._parameter_specs = parameter_specs['parameters']
        self._quitting_ref = quitting_ref
        self._variable = None
        self._window = None
        self._thread = threading.Thread(target=self._create)
        self._thread.start()

    def _add_conditional_settings(self, current_settings_raw, specs, conditional_frame):
        for spec_name, spec in specs.items():
            current_value = current_settings_raw[spec_name] \
                if spec_name in current_settings_raw else None
            self._current_settings[spec_name] = \
                ControlsWindow.SETTING_WIDGET_CONSTRUCTORS[specs[spec_name]['type']](self)(
                    conditional_frame, spec_name, specs[spec_name], current_value)
            value = self._current_settings[spec_name]['var'].get()
            on_off = self._current_settings[spec_name]['onoff_var'].get()
            if on_off:
                self._all_settings['current'][spec_name] = value
            elif spec_name in self._all_settings['current']:
                del self._all_settings['current'][spec_name]
        conditional_frame.pack(fill=X)

    def _broadcast_listeners(self):
        if len(self._listeners) > 0:
            current = self.current_settings()
            for listener in self._listeners:
                listener(**current)

    def _build_bool_setting(self, container, name, spec, current_value: bool):
        setting = BooleanVar(self._window, spec['default'] if current_value is None else current_value, name)
        return self._pack_controls(container, name, spec, setting, current_value,
                                   lambda frame: Checkbutton(frame, text=name, variable=setting))

    def _build_float_setting(self, container, name, spec, current_value: float):
        setting = DoubleVar(self._window, spec['default'] if current_value is None else current_value, name)
        return self._pack_controls(container, name, spec, setting, current_value,
                                   lambda frame: OptionMenu(frame, setting, *spec['options']) if 'options' in spec else
                                   Scale(frame, orient=HORIZONTAL, from_=spec['min'], resolution=spec['step'],
                                         to=spec['max'], variable=setting))

    def _build_int_setting(self, container, name, spec, current_value: int):
        setting = IntVar(self._window, spec['default'] if current_value is None else current_value, name)
        return self._pack_controls(container, name, spec, setting, current_value,
                                   lambda frame: OptionMenu(frame, setting, *spec['options']) if 'options' in spec else
                                   Scale(frame, orient=HORIZONTAL, from_=spec['min'], resolution=spec['step'],
                                         to=spec['max'], variable=setting))

    # noinspection PyMethodMayBeStatic
    def _build_nullable_check(self, name, spec, frame, current_value) -> tuple[object, str]:
        is_nullable = 'nullable' in spec and spec['nullable']
        if is_nullable:
            onoff_var = BooleanVar(self._window, current_value is not None, f'{name}{ON_OFF_VARIABLE_NAME_SUFFIX}')
            nullable_checkbox = Checkbutton(frame, text='(on/off)', variable=onoff_var)
            nullable_checkbox.pack(side=LEFT)
            onoff_cb_name = onoff_var.trace('w', self._on_change)
        else:
            # For some reason, on/off variables of non-nullable settings keep disappearing, so this is a patch:
            onoff_var = FakeBooleanVar()
            onoff_cb_name = None
        return onoff_var, onoff_cb_name

    def _build_str_setting(self, container, name, spec, current_value: str, callback=None):
        setting = StringVar(self._window, spec['default'] if current_value is None else current_value, name)
        return self._pack_controls(container, name, spec, setting, current_value,
                                   lambda frame: OptionMenu(frame, setting, *spec['options']) if 'options' in spec else
                                   Entry(frame, setting), callback)

    def _create(self):
        self._window = Tk()
        self._window.protocol('WM_DELETE_WINDOW', self._on_close_window)
        # self._window.geometry('300x300')
        self._last_process_duration['var'] = StringVar(self._window, 'Last process duration: 0.0',
                                                       'last_process_duration')
        self._last_process_duration['control'] = Label(self._window, anchor='w', justify=LEFT,
                                                       textvariable=self._last_process_duration['var'])
        self._last_process_duration['control'].pack(fill=X, padx=PADDING_X, pady=PADDING_Y)
        algorithm = self._all_settings['current']['algorithm']
        self._main_frame = VerticallyScrollableFrame(self._window)
        self._main_frame.pack(expand=True, fill=BOTH, pady=(0, PADDING_Y))
        self._algorithm = self._build_str_setting(self._main_frame.interior, 'algorithm', {'options': self._algorithms},
                                                  algorithm, self._on_change_algorithm)
        self._reread_settings()
        self._window.mainloop()

    # noinspection PyMethodMayBeStatic
    def _on_change(self, *args):
        name = args[0]
        if name.endswith(ON_OFF_VARIABLE_NAME_SUFFIX):
            name = name.removesuffix(ON_OFF_VARIABLE_NAME_SUFFIX)
        value = self._current_settings[name]['var'].get()
        on_off = self._current_settings[name]['onoff_var'].get()
        if on_off:
            self._all_settings['current'][name] = value
        elif name in self._all_settings['current']:
            del self._all_settings['current'][name]
        for condition_index, conditional in enumerate(self._conditional_frames):
            if name in conditional:
                self._reread_conditional_settings(condition_index, name, value if on_off else None)
        self._broadcast_listeners()

    def _on_change_algorithm(self, *args):
        self._reread_settings()

    def _on_close_window(self, *args):
        self._quitting_ref['quitting'] = True

    def _pack_controls(self, container, name, spec, setting, current_value, control_builder, callback=None):
        frame = Frame(container)
        (onoff_var, onoff_cb_name) = self._build_nullable_check(name, spec, frame, current_value)
        label = Label(frame, text=name + ':')
        control = control_builder(frame)
        var_cb_name = setting.trace('w', self._on_change if callback is None else callback)
        label.pack(side=LEFT)
        control.pack(expand=True, fill=X, side=RIGHT)
        frame.pack(fill=BOTH, padx=PADDING_X)
        return {'super_container': container, 'container': frame, 'control': control, 'var_cb_name': var_cb_name,
                'var': setting, 'onoff_cb_name': onoff_cb_name, 'onoff_var': onoff_var}

    def _remove_current_setting(self, var_name):
        if var_name in self._current_settings:
            setting = self._current_settings[var_name]
            # TODO: Make sure this will be enough to remove tkinter variables
            setting['var'].trace_remove('write', setting['var_cb_name'])
            setting['onoff_var'].trace_remove('write', setting['onoff_cb_name'])
            setting['container'].pack_forget()
            del setting['var']
            del setting['onoff_var']
            del self._current_settings[var_name]

    def _reread_conditional_settings(self, index, condition_name, value):
        algorithm = self._algorithm['var'].get()
        current_settings_raw = self._all_settings['all'][algorithm]
        all_conditional_specs = self._parameter_specs[algorithm][index]
        conditional_specs = all_conditional_specs[condition_name]
        for condition_value, specs in conditional_specs.items():
            for var_name in specs.keys():
                self._remove_current_setting(var_name)
        for condition_value, specs in conditional_specs.items():
            if condition_value == value:
                self._add_conditional_settings(current_settings_raw, specs,
                                               self._conditional_frames[index][condition_name])

    def _reread_settings(self):
        algorithm = self._algorithm['var'].get()
        disposable_current_settings = self._current_settings.copy()  # Cannot change a dictionary while iterating.
        for name in disposable_current_settings:
            self._remove_current_setting(name)
        for conditional in self._conditional_frames:
            for variable_name, conditional_frame in conditional.items():
                conditional_frame.pack_forget()
        self._conditional_frames = []
        # { alg: [ { modkey: { modval1: {}, ...} }, ...] }
        specs_list = self._parameter_specs[algorithm]
        current_settings_raw = self._all_settings['all'][algorithm]
        self._all_settings['current'] = current_settings_raw
        # [ { modkey: { modval1: {}, ...} }, ...]
        for spec_list_index, dependent_specs in enumerate(specs_list):
            if spec_list_index >= len(self._conditional_frames):
                self._conditional_frames.append({})
            for condition_name, conditional_specs in dependent_specs.items():  # This should contain only one condition
                conditional_specs = self._parameter_specs[algorithm][spec_list_index][condition_name]
                for condition_value, specs in conditional_specs.items():
                    if condition_name == '' or current_settings_raw[condition_name] == condition_value:
                        conditional_frame = Frame(self._main_frame.interior)
                        self._conditional_frames[spec_list_index][condition_name] = conditional_frame
                        self._add_conditional_settings(current_settings_raw, specs, conditional_frame)
        self._window.geometry()

    def add_change_listener(self, listener):
        self._listeners.append(listener)

    def current_settings(self):
        current = {'algorithm': self._algorithm['var'].get()}
        for name in self._current_settings:
            setting = self._current_settings[name]
            value = setting['var'].get()
            on_off = setting['onoff_var'].get()
            if on_off and value is not None:
                current[name] = value
        return current

    def destroy(self):
        self._window.quit()

    def record_last_duration(self, duration):
        if 'var' in self._last_process_duration:
            content = '\n'.join([f'Last {mark}: {duration[mark]} sec.' for mark in duration])
            self._last_process_duration['var'].set(content)
