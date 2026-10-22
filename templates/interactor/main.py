# -*- coding: utf-8 -*-
""" Interactor PythonPart

Copyright © __CURRENT_YEAR__ __PUBLISHER_NAME__
"""
from __future__ import annotations

from typing import Any, cast

import NemAll_Python_BaseElements       as BaseElements
import NemAll_Python_BasisElements      as BasisElements
import NemAll_Python_IFW_ElementAdapter as ElementAdapter
import NemAll_Python_Geometry           as Geometry
import NemAll_Python_IFW_Input          as Input
import NemAll_Python_Utility            as Utility

from BaseInteractor                   import BaseInteractor
from BaseInteractor                   import BaseInteractorData

from CreateElementResult              import CreateElementResult
from BuildingElement                  import BuildingElement
from BuildingElementListService       import BuildingElementListService
from BuildingElementPaletteService    import BuildingElementPaletteService
from BuildingElementComposite         import BuildingElementComposite
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementAttributeList     import BuildingElementAttributeList
from TypeCollections.ModelEleList     import ModelEleList
from StringTableService               import StringTableService
from ControlPropertiesUtil            import ControlPropertiesUtil
from PythonPartUtil                   import PythonPartUtil
from PythonPartTransaction            import PythonPartTransaction

from TypeCollections.ModificationElementList import ModificationElementList


class MyInteractor(BaseInteractor):
    """ Definition of the interactor class
    """
    def __init__(self,
                 interactor_data: BaseInteractorData) -> None:
        """ Initialization

        Args:
            interactor_data: interactor data
        """
        self.build_ele = cast(BuildingElement, interactor_data.build_ele_list[0])
        self.build_ele_list = interactor_data.build_ele_list
        self.control_props_list = interactor_data.control_props_list
        self.coord_input = interactor_data.coord_input
        self.document = self.coord_input.GetInputViewDocument()
        self.modification_ele_list = interactor_data.modify_uuid_list
        self.palette_service: BuildingElementPaletteService = None

        self.palette_service = BuildingElementPaletteService(
            build_ele_list=self.build_ele_list,
            build_ele_composite=interactor_data.build_ele_composite,
            build_ele_script=self.build_ele.script_name,
            build_ele_ctrl_props_list=self.control_props_list,
            picture_path=f"{self.build_ele.pyp_file_path}\\"
            )
        self.palette_service.show_palette(self.build_ele.pyp_file_name)


    def process_mouse_msg(self,
                          mouse_msg: int,
                          pnt:       Geometry.Point2D,
                          msg_info:  Input.AddMsgInfo) -> bool:
        """ Method called on each mouse movement, button click or release.

        Args:
            mouse_msg: the mouse message (e.g. 512 - mouse movement)
            pnt:       the input point in view coordinates
            msg_info:  additional message info

        Returns:
            True/False for success
        """
        return True


    def modify_element_property(self,
                                page:  int,
                                name:  str,
                                value: Any) -> None:
        """ Called after each property modification in the property palette

        Args:
            page:  index of the page, beginning with 0
            name:  name of the modified property
            value: new property value
        """
        update_palette = self.palette_service.modify_element_property(page, name, value)

        if update_palette:
            self.palette_service.update_palette(-1, False)

        self.palette_service.refresh_palette(self.build_ele_list, self.control_props_list)


    def on_control_event(self,
                         event_id: int) -> None:
        """ Called when an event is triggered by a palette control (ex. button)

        Args:
            event_id: id of the triggered event, defined in the tag `<EventId>`
        """


    def on_cancel_function(self) -> bool:
        """ Called when ESC key is pressed.

        Returns:
            True when the PythonPart framework should terminate the PythonPart, False otherwise
        """
        self.palette_service.close_palette()

        return True


    def on_cancel_by_menu_function(self) -> None:
        """ Handles the event of terminating the PythonPart by calling another function
        in Allplan UI

        Implement this method, when some actions must be introduced, before the PythonPart
        is eventually terminated.
        """
        self.palette_service.close_palette()


    def on_preview_draw(self) -> None:
        """ Called when an input in the dialog line is done (e.g. input of a coordinate)
        """


    def on_mouse_leave(self) -> None:
        """ Called when the mouse leaves the viewport window
        """


    def on_value_input_control_enter(self) -> bool:
        """ Called when enter key is pressed inside the value input control

        Returns:
            True/False for success
        """
        return True


    def execute_save_favorite(self,
                              file_name: str) -> None:
        """ Save the favorite data

        Args:
            file_name: name of the favorite file
        """
        BuildingElementListService.write_to_file(file_name, self.build_ele_list)


    def execute_load_favorite(self,
                              file_name: str) -> None:
        """ Load the favorite data

        Args:
            file_name: name of the favorite file
        """
        BuildingElementListService.read_from_file(file_name, self.build_ele_list)
        self.palette_service.update_palette(-1, True)


    def update_after_favorite_read(self) -> None:
        """ Update the data after a favorite read
        """
        self.palette_service.update_palette(-1, True)


    def reset_param_values(self,
                           _build_ele_list: list[BuildingElement]) -> None:
        """ Reset the parameter values

        Args:
            _build_ele_list: list with building elements
        """
        BuildingElementListService.reset_param_values(self.build_ele_list)

        self.palette_service.update_palette(-1, True)


    def __del__(self) -> None:
        """ Save the input values at the end of the user interaction
        """
        BuildingElementListService.write_to_default_favorite_file(self.build_ele_list)
