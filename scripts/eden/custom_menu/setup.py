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

MENU_PATH = os.path.dirname(__file__)
EDEN_PATH = os.path.dirname(MENU_PATH)
SCRIPTS_PATH = os.path.dirname(EDEN_PATH)
MENU_NAME = "eden_menu"
MENU_LABEL = "Eden"

def install():
    EdenLogger.info("Install Eden Custom Menu...")

    # Create Menu
    gMainWindow = mel.eval('$temp1 = $gMainWindow')

    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)

    cmds.menu(MENU_NAME, parent=gMainWindow, label=MENU_LABEL, tearOff=True)

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
            _generate_button(file_path, parent)
    return


def _generate_button(path, parent):
    file_base = os.path.basename(path).split(".py")[0]
    label = file_base.title().replace("_", " ")

    mod_list = os.path.dirname(path).split(os.path.dirname(SCRIPTS_PATH))[-1].split('\\')[2:]
    mod_list.append(file_base)
    mod_path = ".".join(mod_list)

    try:
        mod = __import__(mod_path, (), (), [file_base])
        EdenLogger.debug("Created Button {}".format(label))
        cmds.menuItem(parent=parent, label=label, command=mod.main)

    except Exception as e:
        EdenLogger.warning('\t%s Failed : \n\t\t\t%s' % (label, e))
        pass


def uninstall():
    EdenLogger.info("Un-Install Eden Custom Menu...")

    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)

    return
