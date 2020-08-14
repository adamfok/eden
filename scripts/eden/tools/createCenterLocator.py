import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils


def createCenterLocator(name=""):
    selection = cmds.ls(sl=True)
    assert selection, "Nothing Selected"

    pos = mayaUtils.getCenterPositionFromSelection(selection)
    loc = mayaUtils.createLocator(name=name, pos=pos)

    return loc
