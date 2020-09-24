import maya.cmds as cmds
from eden.utils.mayaUtils import hashRename
from eden.utils.loggerUtils import EdenLogger


def hashRenamer():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected..")
        return

    result = cmds.promptDialog(
        title="Hash Renamer",
        message='Enter New Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text=selection[0])

    if result == 'OK':
        hashName = cmds.promptDialog(query=True, text=True)
        hashRename(selection, hashName, startNum=1)
