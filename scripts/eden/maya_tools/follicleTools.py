import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def closestFollicle():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    loc = cmds.spaceLocator()[0]
    for sel in selection:
        mayaUtils.closestFollicle(inLocator=loc, node=sel)

    return


def createFollicleOnVert():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    verts = mayaUtils.filterSelectionByComponent(componentType="vertex")
    for vtx in verts:
        mayaUtils.createFollicleOnVert(vtx)


def revitObject():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    src = selection[-1]
    dsts = selection[:-1]

    for dst in dsts:
        mayaUtils.revitObject(inObj=dst, node=src)

    return
