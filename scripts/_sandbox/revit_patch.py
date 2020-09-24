import pymel.core as pm


def main(*args):
    vtxs = pm.ls(sl=True, flatten=True)

    assert len(vtxs) == 4, "Please Select 4 vertices"

    nplane = pm.nurbsPlane(p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=1, u=1, v=1, ch=0, name="revit_patch_01")[0]
    cvs = [nplane.cv[0][0], nplane.cv[0][1], nplane.cv[1][0], nplane.cv[1][1]]

    mesh = pm.PyNode(vtxs[0].name().split(".vtx")[0]).getParent()

    for vtx, cv in zip(vtxs, cvs):
        pm.xform(cv, ws=True, t=vtx.getPosition())

    import maya.cmds as cmds
    import maya.mel as mel
    skinCluster = mel.eval('findRelatedSkinCluster("%s")' % (mesh))
    joints = cmds.skinCluster(skinCluster, query=True, inf=True)

    pm.skinCluster(joints, nplane, tsb=True)

    for vtx, cv in zip(vtxs, cvs):
        pm.select(vtx)
        pm.mel.eval("artAttrSkinWeightCopy")
        pm.select(cv)
        pm.mel.eval("artAttrSkinWeightPaste")

    # from pixo_rigging.lib.utils import utils_follicle
    # fol = utils_follicle.create_follicle(nplane, uPos=0.5, vPos=0.5)
    # pm.parent(jnt, fol.getParent(), r=True)

    loc = pm.spaceLocator(name="revit_patch_locator_01")
    pos = pm.createNode("pointOnSurfaceInfo")
    fbf = pm.createNode("fourByFourMatrix")
    vp = pm.createNode("vectorProduct")
    dm = pm.createNode("decomposeMatrix")

    pos.parameterU.set(0.5)
    pos.parameterV.set(0.5)
    vp.operation.set(2)

    nplane.worldSpace[0] >> pos.inputSurface

    pos.positionX >> fbf.in30
    pos.positionY >> fbf.in31
    pos.positionZ >> fbf.in32

    pos.normalizedNormalX >> fbf.in20
    pos.normalizedNormalY >> fbf.in21
    pos.normalizedNormalZ >> fbf.in22

    pos.normalizedTangentUX >> fbf.in00
    pos.normalizedTangentUY >> fbf.in01
    pos.normalizedTangentUZ >> fbf.in02

    pos.normalizedNormal >> vp.input1
    pos.normalizedTangentU >> vp.input2

    vp.outputX >> fbf.in10
    vp.outputY >> fbf.in11
    vp.outputZ >> fbf.in12

    fbf.output >> dm.inputMatrix

    dm.outputTranslate >> loc.translate
    dm.outputRotate >> loc.rotate
    dm.outputScale >> loc.scale

    return
