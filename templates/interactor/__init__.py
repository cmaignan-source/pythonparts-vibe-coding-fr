""" Entry point for __ASSET_NAME__ using Interactor PythonPart

Allplan discovers a PythonPart package through two mandatory module-level
functions defined here:

- ``check_allplan_version``  — version guard, called once on load.
- ``create_preview``         — create the library preview.
- ``create_interactor``      — factory that produces the interaction handler.

Everything else lives in the sub-modules:
- ``main.py`` — Allplan event handling

Copyright © __CURRENT_YEAR__ __PUBLISHER_NAME__
"""
from __future__ import annotations

import NemAll_Python_IFW_ElementAdapter as ElementAdapter

from BaseInteractor import BaseInteractor
from BaseInteractor import BaseInteractorData

from BuildingElement     import BuildingElement
from CreateElementResult import CreateElementResult

import Utils.LibraryBitmapPreview

from .main import MyInteractor


def check_allplan_version(_build_ele: BuildingElement,
                          version:    str) -> bool:
    """ Called when the PythonPart is started to check, if the current
    Allplan version is supported.

    Args:
        _build_ele: building element with the parameter properties
        version:    current Allplan version

    Returns:
        True if current Allplan version is supported and PythonPart script can be run, False otherwise
    """
    return float(version) >= 2026


def create_preview(build_ele:  BuildingElement,
                   _doc:       ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """ Create the library preview

    Args:
        build_ele:  building element with the parameter properties
        _doc:       document of the Allplan drawing files

    Returns:
        created element result
    """
    picture = f"{build_ele.pyp_file_path}\\{build_ele.pyp_file_name.split("\\")[-1].split(".")[0]}.png"
    return CreateElementResult(Utils.LibraryBitmapPreview.create_library_bitmap_preview(picture))


def create_interactor(interactor_data: BaseInteractorData) -> BaseInteractor:
    """ Function for the interactor creation, called when PythonPart is initialized.
    When called, the PythonPart framework performs the following steps:

    - reads the parameters and their values from the xxx.pyp file and stores them in the buld_ele_list
    - if tag `ReadLastInput` is set to True: read the parameter values from the last input,
        (stored in ...\\Usr\\_user_name_\\tmp\\_python_part_name.pyv) and assign them to the parameters
        in build_ele_list
    - if starting an input by Match from the context menu or double right click: read the parameter
        values from the attribute @611@ of the matched PythonPart and assign them to the parameters
        in build_ele_list
    - if in modification mode: read the parameter values from the attribute @611@ of the selected
        PythonPart and assign them to the parameters in build_ele_list

    Args:
        interactor_data: object with the data for the interactor creation

    Returns:
        Created interactor object
    """
    return MyInteractor(interactor_data)
