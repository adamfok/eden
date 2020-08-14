import maya.cmds as cmds


def main(*args):
    from eden.utils.mayaUtils import createParentGroup

    selection = cmds.ls(sl=True)
    if not selection:
        print "Nothing Selected"
        return

    else:
        for node in selection:
            createParentGroup(node, suffix="_offset")
        return
