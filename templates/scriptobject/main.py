# -*- coding: utf-8 -*-
""" ScriptObject PythonPart

Copyright © __CURRENT_YEAR__ __PUBLISHER_NAME__
"""
from __future__ import annotations

from typing import Any, cast

import NemAll_Python_BaseElements       as BaseElements
import NemAll_Python_BasisElements      as BasisElements
import NemAll_Python_IFW_ElementAdapter as ElementAdapter
import NemAll_Python_Geometry           as Geometry
import NemAll_Python_AllplanSettings    as Settings

from BaseScriptObject import BaseScriptObject
from BaseScriptObject import BaseScriptObjectData

from CreateElementResult          import CreateElementResult
from BuildingElement              import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from TypeCollections.ModelEleList import ModelEleList
from PythonPartUtil               import PythonPartUtil
from PythonPartTransaction        import ConnectToElements

from ScriptObjectInteractors.OnCancelFunctionResult import OnCancelFunctionResult


class MyScriptObject(BaseScriptObject):
    """ Definition of the script object class
    """
    def __init__(self,
                 build_ele:          BuildingElement,
                 script_object_data: BaseScriptObjectData) -> None:
        """ Initialization

        Args:
            build_ele:          building element with the parameter properties
            script_object_data: script object data
        """
        super().__init__(script_object_data)

        self.build_ele = cast(BuildingElement, build_ele)
        self.is_modification_mode = self.execution_event != Settings.ExecutionEvent.eCreation


    def start_input(self) -> None:
        """ First input
        """
        self.script_object_interactor = None


    def execute(self) -> CreateElementResult:
        """ Execute the script

        Returns:
            created element result
        """
        return CreateElementResult()
