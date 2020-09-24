import maya.cmds as cmds
import maya.mel as mel
import os

from eden.utils.loggerUtils import EdenLogger

# PATHS
EDEN_PATH = os.path.dirname(__file__)
SCRIPTS_PATH = os.path.dirname(EDEN_PATH)
DATA_PATH = os.path.abspath(os.path.join(SCRIPTS_PATH, "..", "data"))

# MENU
MENU_NAME = "eden_menu"
MENU_LABEL = "Eden"
MENU_PATHS = [os.path.join(r, "menu") for r, d, f in os.walk(EDEN_PATH) if "menu" in d]

# RELOAD MODULES
RELOAD_DIRS = [os.path.join(EDEN_PATH, "core"),
               os.path.join(EDEN_PATH, "utils"),
               os.path.join(EDEN_PATH, "maya_tools")]


def getModPath(filepath):
    module_name = os.path.basename(filepath).split(".py")[0]
    _module_path = os.path.dirname(filepath).split(os.path.dirname(SCRIPTS_PATH))[-1].split('\\')[2:]
    module_path = ".".join(_module_path)
    return module_path, module_name


def reloadModules(*args):
    for reload_dir in RELOAD_DIRS:
        for root, dirs, files in os.walk(reload_dir):
            for f in files:
                if not f.startswith("_") and f.endswith(".py"):
                    path = os.path.join(root, f)

                    module_path, module_name = getModPath(path)

                    try:
                        mod = __import__("%s.%s" % (module_path, module_name), (), (), [module_name])
                        reload(mod)

                        print ("Reload {}".format(mod))

                    except Exception as e:
                        print ('Reload Failed %s : \n\t\t\t%s' % (module_name, e))
                        pass


def install():
    EdenLogger.info("Install Eden Custom Menu...")

    # Create Menu
    gMainWindow = mel.eval('$temp1 = $gMainWindow')

    if cmds.menu(MENU_NAME, exists=True):
        cmds.deleteUI(MENU_NAME)

    cmds.menu(MENU_NAME, parent=gMainWindow, label=MENU_LABEL, tearOff=True)
    cmds.menuItem(parent=MENU_NAME, label="RELOAD", command=reloadModules)

    # Generate Label Dividers
    for menu_path in MENU_PATHS:
        first_level_directories = [os.path.join(menu_path, f) for f in os.listdir(menu_path)]
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
    module_path, module_name = getModPath(file_path)
    command += "from {} import {}\n".format(module_path, module_name)
    command += "{}.main()".format(module_name)
    return command