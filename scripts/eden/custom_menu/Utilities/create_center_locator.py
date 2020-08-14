import maya.cmds as cmds


def main(*args):
    from eden.utils.mayaUtils import createCenterLocator

    selection = cmds.ls(sl=True)
    if not selection:
        print "Nothing Selected"
        return

    else:
        createCenterLocator(selection)
        return