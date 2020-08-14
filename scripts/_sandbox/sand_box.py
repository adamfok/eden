import eden.utils.mayaUtils as mayaUtils ; reload(mayaUtils)
import maya.cmds as cmds

nodes = cmds.ls(sl=True)
mayaUtils.createComponentLocator(nodes)