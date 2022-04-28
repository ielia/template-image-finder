# Template Image Finder


## Getting started
To create a virtual environment and install dependencies
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```


## Execution
Example executions:
```powershell
.\image-finder.py
.\image-finder.py -b base.jpg -q template*.jpg -w 800,600
```


## Algorithmic Modules
Image search algorithms will be contained in modules with their corresponding files in a subdirectory.
These modules need to comply with specifications in order to function with the GUI.

### PARAMETER_SPECS Module Constant
`PARAMETER_SPECS` module constant format for new algorithms:
```python
{
    'algorithms': [ ALGORITHM1, ... ],
    'parameters': [
        { 'condition_variable': {
            'condition_value1': { 'param_a1': { 'type': TYPE_PARAM_A1, 'options': [...], 'default': DEFAULT_PARAM_A1 } },
            'condition_value2': { 'param_b1': { 'type': {int|float}, 'min': ..., 'max': ..., 'step': ..., 'default': ... } },
            'condition_value3': { 'param_b1': { 'type': ..., 'nullable': {True|False}, 'default': ..., ... } },
            ...
        } },
        ...
    ],
    'plot_functions': { ALGORITHM1: plot_function1, ... }
}
```
Each element in `parameters` will represent a section in the controls GUI. Each `condition_variable` needs to be either `''` (meaning "always visible"), `'algorithm'` or a parameter contained in a previous section.

Parameters must not overlap, i.e., a parameter of the same name cannot be found in two different sections of the same algorithm.
A parameter can show up in a single section in more than one conditional branch, though.

Parameter specs must have one of `bool`, `float`, `int` or `str` as type.
They need also have a default value, even if it is `None`.

These module `PARAMETER_SPECS` will later be condensed into a single `PARAMETER_SPECS` structure for all algorithms in the repository.


### Plot Functions
Plot functions must have the following signature:
```python
def plot(base_image, query_image, algorithm: str, **kwargs)
```
Those `kwargs` can (and should) be expanded in the signature to capture high-level parameters.
Parameters from expanded `kwargs` must be declared in the corresponding `PARAMETER_SPECS` constant of the same module.


## TODO
* Fix algorithms.
* Improve matching of scarcely featured query images.
* Improve readability of code.
* Fix zoom-in center calculations.
* Find more GUI listeners to improve performance and UX.


## Reading material
* https://docs.opencv.org/3.4/d5/d6f/tutorial_feature_flann_matcher.html
* https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html
* https://medium.com/@vad710/cv-for-busy-developers-detecting-objects-35081faf1b3d
