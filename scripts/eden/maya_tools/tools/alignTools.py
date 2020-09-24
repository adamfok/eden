import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def aimUpConstraint():
    selection = cmds.ls(sl=True)
    if not len(selection) == 3:
        EdenLogger.warning("Select 3 Objects (Target, Base, Up)")
        return

    target, base, up = selection
    mayaUtils.aimUpConstraint(target, base, up, upVector=[0, 1, 0], aimVector=[1, 0, 0])
    EdenLogger.info("Created Aim Up Constraint")
