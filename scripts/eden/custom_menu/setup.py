"""
Author : Adam Chun Wai Fok
Date : Aug 2020

Description : 
    Custom Menu using os.listdir()
    
Note : 
    Script will walk through the custom menu path,
    dynamically create label divider on first level
    dynamically create sub-menu when folder found.
    dynamically create menuItem for each .py file, running .main() function of each file

"""
import maya.cmds as cmds
import maya.mel as mel
import os

from eden.utils.loggerUtils import EdenLogger
from eden.utils import edenUtils

MENU_PATH = os.path.dirname(__file__)
EDEN_PATH = edenUtils.EDEN_PATH
SCRIPTS_PATH = edenUtils.SCRIPTS_PATH
MENU_NAME = "eden_menu"
MENU_LABEL = "Eden"


def install():
    EdenLogger.info("Install Eden Custom Menu...")

    # Create Menu
    gMainWindow = mel.eval('$temp1 = $gMainWindow')

    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)

    cmds.menu(MENU_NAME, parent=gMainWindow, label=MENU_LABEL, tearOff=True)
    cmds.menuItem(parent=MENU_NAME, label="RELOAD", command=edenUtils.reloadModules)

    # Generate Label Dividers
    first_level_directories = [os.path.join(MENU_PATH, f) for f in os.listdir(MENU_PATH)]
    for first_level_dir in [d for d in first_level_directories if os.path.isdir(d)]:
        dir_name = os.path.basename(first_level_dir)
        cmds.menuItem(parent=MENU_NAME, divider=True, dividerLabel=dir_name.title())

        # Generate Sub-Menus & Buttons
        _generate_menu_items(first_level_dir, MENU_NAME)

    return


def _generate_menu_items(path, parent):
    for d in os.listdir(path):
        dir_path = os.path.join(path, d)
        if os.path.isdir(dir_path):
            new_parent = cmds.menuItem(parent=parent, subMenu=True, label=d.title())
            _generate_menu_items(dir_path, new_parent)

    for f in os.listdir(path):
        if f.endswith('.py') and not f.startswith("_"):
            file_path = os.path.join(path, f)
            command = _generate_command(file_path)
            label = f.split(".py")[0].title().replace("_", " ")
            cmds.menuItem(parent=parent, label=label, command=command)
    return


def uninstall():
    EdenLogger.info("Un-Install Eden Custom Menu...")

    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)

    return


def _generate_command(file_path):
    command = ""
    module_path, module_name = edenUtils.getModPath(file_path)
    command += "from {} import {}\n".format(module_path, module_name)
    command += "{}.main()".format(module_name)
    return command
