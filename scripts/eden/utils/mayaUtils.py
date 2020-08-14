import maya.cmds as cmds


def getCenterPositionFromSelection(selection):
    c = cmds.cluster(selection)
    result = cmds.xform(c, ws=True, q=True, piv=True)[0:3]
    cmds.delete(c)
    return result


def createLocator(name="", pos=[0, 0, 0]):
    loc = cmds.spaceLocator(name=name)[0]
    cmds.xform(loc, ws=True, t=pos)
    return loc
