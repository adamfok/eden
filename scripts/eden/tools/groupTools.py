import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def createOffsetGroups():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    grps = []
    for node in selection:
        grps.append(mayaUtils.createParentGroup(node, suffix="_offset"))
    cmds.select(grps)
    EdenLogger.debug("Offset Groups Created")
    return


def createCommonGroup():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    grp = mayaUtils.createCommonGroup(selection)
    cmds.select(grp)
    EdenLogger.debug("Common Group Created")
    return


def stackNodes():
    selection = cmds.ls(sl=True)
    if len(selection) < 2:
        EdenLogger.warning("Select 2 or more objects..")
        return

    mayaUtils.stackNodes(selection)
    EdenLogger.debug("Stack Nodes")