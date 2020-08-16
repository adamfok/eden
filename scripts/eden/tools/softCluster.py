import maya.OpenMaya as om
import maya.cmds as cmds
from eden.utils.loggerUtils import EdenLogger
import string


def softCluster():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    # Strip selection of any attributes
    sel = string.split(selection[0], '.')

    richSel = om.MRichSelection()
    om.MGlobal.getRichSelection(richSel)

    richSelList = om.MSelectionList()
    richSel.getSelection(richSelList)

    path = om.MDagPath()
    component = om.MObject()
    richSelList.getDagPath(0, path, component)

    componentFn = om.MFnSingleIndexedComponent(component)

    cluster = cmds.cluster(rel=True)
    clusterSet = cmds.listConnections(cluster, type="objectSet")

    cmds.select(selection[0], r=True)
    for i in range(0, componentFn.elementCount()):
        weight = componentFn.weight(i)
        v = componentFn.element(i)
        w = weight.influence()
        # print "The selection weight of vertex %d is %f." % (v, w)
        vtx = (sel[0] + '.vtx[%d]') % v
        cmds.sets(vtx, add=clusterSet[0])
        cmds.percent(cluster[0], vtx, v=w)

    cmds.select(cluster)
    return cluster
