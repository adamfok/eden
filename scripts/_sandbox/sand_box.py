import eden.utils.mayaUtils as mayaUtils ; reload(mayaUtils)
import eden.tools.follicleTools as follicleTools ; reload(follicleTools)
import maya.cmds as cmds

verts = mayaUtils.filterSelectionByComponent(componentType="vertex")
print verts
for vtx in verts:
    print vtx
    mayaUtils.createFollicleOnVert(vtx)