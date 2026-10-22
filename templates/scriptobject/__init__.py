""" Entry point for __ASSET_NAME__ using ScriptObject PythonPart

Allplan discovers a PythonPart package through two mandatory module-level
functions defined here:

- ``check_allplan_version``  — version guard, called once on load.
- ``create_script_object``   — factory that produces the interaction handler.

Everything else lives in the sub-modules:
- ``main.py`` — Allplan event handling

Copyright © __CURRENT_YEAR__ __PUBLISHER_NAME__
"""
from __future__ import annotations

from BaseScriptObject import BaseScriptObject
from BaseScriptObject import BaseScriptObjectData

from BuildingElement  import BuildingElement

from .main import MyScriptObject


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


def create_script_object(build_ele:          BuildingElement,
                         script_object_data: BaseScriptObjectData) -> BaseScriptObject:
    """ Creation of the script object

    Args:
        build_ele:          building element with the parameter properties
        script_object_data: script object data

    Returns:
        created script object
    """
    return MyScriptObject(build_ele, script_object_data)
