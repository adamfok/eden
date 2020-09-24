import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def deleteKeys():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        cmds.cutKey(sel)
        EdenLogger.info("Deleted All Keys on {}".format(sel))
