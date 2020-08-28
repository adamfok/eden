import maya.cmds as cmds
from eden.maya_tools import skinTools
from eden.utils import mayaUtils
reload(mayaUtils)

node = cmds.ls(sl=True)[0]
mayaUtils.curveCVLocator(node)