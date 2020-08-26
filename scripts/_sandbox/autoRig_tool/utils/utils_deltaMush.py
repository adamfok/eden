import pymel.core as pm
import maya.cmds as cmds


def get_skinCluster(mesh):
    skinCluster = pm.mel.eval('findRelatedSkinCluster("%s")' % (mesh))
    result = pm.PyNode(skinCluster)

    return result


def get_skinCluster_joints(skinCluster):
    return [y for x, y in skinCluster.matrix.listConnections(type='joint', c=True)]


def get_skinCluster_jointIndex(skinCluster):
    return [x.index() for x, y in skinCluster.matrix.listConnections(type='joint', c=True)]


def get_skinCluster_jointInfo(skinCluster):
    """
    return {jointName : jointIndex}
    """
    result = {}
    for x, y in skinCluster.matrix.listConnections(type='joint', c=True):
        result[y] = x.index()

    return result


def bind_like(src, dst):
    skin = get_skinCluster(src)
    joints = get_skinCluster_joints(skin)
    pm.skinCluster(joints, dst, tsb=True)
    pm.copySkinWeights(src, dst, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='oneToOne')


def get_joint_weightMap(mesh, joint):
    result = []
    skin = get_skinCluster(mesh)
    jointInfo = get_skinCluster_jointInfo(skin)

    jointIndex = jointInfo[joint]

    for vertex in xrange(mesh.numVertices()):
        weight = pm.getAttr("%s.wl[%d].w[%d]" % (skin, vertex, jointIndex))
        result.append(weight)

    return result


def get_position_map(mesh):
    posList = cmds.xform('%s.vtx[*]' % mesh, q=True, ws=True, t=True)
    result = posList[1::3]

    return result


def apply_weightMap(mesh, joint, weightMap):
    skin = get_skinCluster(mesh)
    jointInfo = get_skinCluster_jointInfo(skin)

    jointIndex = jointInfo[joint]

    for vertex in xrange(mesh.numVertices()):
        weight = weightMap[vertex]
        if weight != 0.0:
            pm.setAttr("%s.wl[%s].w[%s]" % (skin, vertex, jointIndex), weight)

    return


def multiply_map(srcMap, dstMap):
    map = [dst * src for src, dst in zip(srcMap, dstMap)]
    return map


def delta_map(baseMap, dstMap):
    map = [dst - base for base, dst in zip(baseMap, dstMap)]
    return map


def transfer_deltaMush_to_weight(srcGeo, dstGeo):
    srcSkin = get_skinCluster(srcGeo)
    baseMap = get_position_map(srcGeo)

    joints = get_skinCluster_joints(srcSkin)

    for jnt in joints:
        pm.xform(jnt, t=[0, 1, 0], ws=True, r=True)
        pm.refresh()
        dstMap = get_position_map(srcGeo)
        pm.xform(jnt, t=[0, -1, 0], ws=True, r=True)

        deltaMap = delta_map(baseMap, dstMap)
        apply_weightMap(dstGeo, jnt, deltaMap)


def convert_deltaMush_to_weight(geo):
    skinGeo = pm.duplicate(geo, name='deltaSkin_geo_temp')[0]

    bind_like(geo, skinGeo)
    skinGeoSC = get_skinCluster(skinGeo)

    pm.skinCluster(skinGeoSC, e=True, normalizeWeights=2)  # post
    pm.skinCluster(skinGeoSC, e=True, forceNormalizeWeights=True)

    transfer_deltaMush_to_weight(geo, skinGeo)

    pm.select(geo)
    pm.mel.eval('DeleteHistory')

    bind_like(skinGeo, geo)

    pm.delete(skinGeo)
