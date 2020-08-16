import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def setMoveJointMode(toggle=True):
    mayaUtils.setMoveJointMode(toggle)
    EdenLogger.info("Move Joint Mode : {}".format(toggle))
    return


def copyVertexWeightToObject():
    selection = cmds.ls(sl=True, fl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    vtx = selection[0]
    if ".vtx" not in vtx:
        EdenLogger.warning("No Vertex Selected..")
        return

    shape = vtx.split(".vtx")[0]
    mayaUtils.copyVertexWeightToObject(vtx)
    cmds.select(shape)

    EdenLogger.info("Copy Weight to Object ---> {}".format(shape))
    return


def selectSkinJoints():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    result = []
    for sel in selection:
        result.extend(mayaUtils.getSkinJoints(sel))

    cmds.select(result)
    EdenLogger.info("Select Skin Joints")
    return


def copySkinWeights():
    selection = cmds.ls(sl=True)
    if len(selection) < 2:
        EdenLogger.warning("Select 2 or more objects.. (targets , source)")
        return

    src = selection[-1]
    dsts = selection[:-1]

    for dst in dsts:
        cmds.copySkinWeights(src, dst, noMirror=True,
                             surfaceAssociation='closestPoint',
                             influenceAssociation='oneToOne')
        EdenLogger.info("Copied Weights from {} to {}".format(src, dst))

    return


def copySkinCluster():
    selection = cmds.ls(sl=True)
    if len(selection) < 2:
        EdenLogger.warning("Select 2 or more objects.. (targets , source)")
        return

    src = selection[-1]
    dsts = selection[:-1]

    for dst in dsts:
        mayaUtils.copySkinCluster(src, dst)
        EdenLogger.info("Copied SkinCluster from {} to {}".format(src, dst))


def rebind():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        mayaUtils.rebind(sel)
        EdenLogger.info("Rebind {}".format(sel))


def renameSkinCluster():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        name = mayaUtils.renameSkinCluster(sel)
        EdenLogger.info("Renamed {}'s SkinCluster to {}".format(sel, name))
