import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def orientWorld():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        mayaUtils.orientWorld(sel)
        EdenLogger.info("Orient Joint to World : {}".format(sel))


def lockJointOrient():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        mayaUtils.lockJointOrient(sel)
        EdenLogger.info("Lock Joint Orient : {}".format(sel))