import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def createCenterLocator():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    loc = mayaUtils.createCenterLocator(selection)
    cmds.select(loc)
    EdenLogger.debug("Center Locator Created")
    return


def createComponentLocator():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    locs = mayaUtils.createComponentLocator(selection)
    cmds.select(locs)
    EdenLogger.debug("Component Locators Created")
    return
