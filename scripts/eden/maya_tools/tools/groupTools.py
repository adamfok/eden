import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def createCommonGroup():
    selection = cmds.ls(sl=True)
    if not selection:
        grp = cmds.group(empty=True, name="null1")
    else:
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


def parentGroupDialog():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected..")
        return

    result = cmds.promptDialog(
        title="Parent Groups",
        message='Enter Suffix:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text="_offset")

    if result == 'OK':
        suffix = cmds.promptDialog(query=True, text=True)
        for node in selection:
            mayaUtils.createParentGroup(node, suffix=suffix)
