import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def deleteIntermediateShapes():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        mayaUtils.deleteIntermediateShapes(sel)
        EdenLogger.info("Deleted Intermediate Shapes on {}".format(sel))
