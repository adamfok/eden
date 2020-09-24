import maya.cmds as cmds
import os
import eden.utils.mayaUtils as mayaUtils
import eden.utils.edenUtils as edenUtils
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


def flattenToWeights():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        mayaUtils.convertVtxDeltaToWeights(sel)
        EdenLogger.info("Flatten To SkinCluster : {}".format(sel))


def exportSkinXML():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    dirPath = cmds.fileDialog2(fileMode=2, dialogStyle=2, dir=edenUtils.DATA_PATH)

    if dirPath:
        nodes = cmds.ls(sl=True)
        mayaUtils.exportSkinXMLs(nodes, dirPath[0])


def importSkinXML():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    dirPath = cmds.fileDialog2(fileMode=2, dialogStyle=2, dir=edenUtils.DATA_PATH)

    if dirPath:
        nodes = cmds.ls(sl=True)
        mayaUtils.importSkinXMLs(nodes, dirPath[0])
    pass


def replaceSkinXML():
    selection = cmds.ls(sl=True)
    if not len(selection) == 1:
        EdenLogger.warning("Select One Object")
        return

    singleFilter = "XML (*.xml)"
    xmlPath = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, fileMode=1)

    if xmlPath:
        node = selection[0]

        if mayaUtils.isSkinned(node) is False:
            mayaUtils.bindSkinXML(node=node, xmlPath=xmlPath)

        mayaUtils.importSkinXML(node, xmlPath[0])
