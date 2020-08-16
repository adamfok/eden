import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


# TRANSFORM UTILS

def getCenterPosition(nodes):
    c = cmds.cluster(nodes)
    result = cmds.xform(c, ws=True, q=True, piv=True)[0:3]
    cmds.delete(c)
    return result


def createLocator(name="", pos=[0, 0, 0]):
    loc = cmds.spaceLocator(name=name)[0]
    cmds.xform(loc, ws=True, t=pos)
    return loc


def createCenterLocator(nodes, name=""):
    pos = getCenterPosition(nodes)
    loc = createLocator(name=name, pos=pos)

    return loc


def createComponentLocator(nodes):
    locs = []
    for component in cmds.ls(nodes, fl=True):
        loc = createCenterLocator(component)
        locs.append(loc)

    return locs


def hashRename(nodes, hashName, startNum=1):
    numCount = startNum

    for node in nodes:
        node = pm.PyNode(node)

        if "#" in hashName:
            hush = hashName[(hashName.find("#")):(hashName.find("#") + hashName.count("#"))]
            pad = str(numCount).zfill(hashName.count("#"))

            newName = hashName.replace(hush, pad)
            node.rename(newName)
            numCount = numCount + 1


def getCommonName(names):
    words = names[0].split("_")
    common_set = set(words)
    for name in names[1:]:
        compare_set = set(name.split("_"))
        common_set = common_set & compare_set

    common_words = [w for w in words if w in common_set]

    if common_words:
        result = "_".join(common_words)
    else:
        result = ""

    return result


def createCommonGroup(nodes):
    commonName = getCommonName(nodes)

    if commonName:
        grpName = "{0}_grp".format(commonName)
    else:
        grpName = "group"

    grp = cmds.group(empty=True, name=grpName)
    cmds.parent(nodes, grp)

    return grp


def createParentGroup(node, suffix):
    parent = cmds.listRelatives(node, p=True)

    name = "{}{}".format(node, suffix)
    grp = cmds.group(empty=True, name=name)

    cmds.matchTransform(grp, node)
    cmds.parent(node, grp)

    if parent:
        cmds.parent(grp, parent)

    return grp


def stackNodes(nodes):
    for i in range(len(nodes) - 1):
        cmds.parent(nodes[i + 1], nodes[i], a=True)
    return


# SKINNING UTILS

def setMoveJointMode(toggle):
    mel.eval("moveJointsMode {}".format(1 if toggle else 0))
    return


def copyVertexWeightToObject(vtx):
    mel.eval('artAttrSkinWeightCopy')
    cmds.select('%s.vtx[*]' % vtx.split(".vtx")[0])
    mel.eval('artAttrSkinWeightPaste')
    return


def getSkinCluster(mesh):
    return mel.eval('findRelatedSkinCluster("%s")' % mesh)


def getSkinJoints(mesh):
    skin = getSkinCluster(mesh)
    return cmds.skinCluster(skin, query=True, inf=True)


def copySkinCluster(src, dst, uv=False):
    joints = getSkinJoints(src)
    skin = cmds.skinCluster(joints, dst, tsb=True)
    if uv:
        cmds.copySkinWeights(src, dst, noMirror=True,
                             uvSpace=['map1', 'map1'],
                             surfaceAssociation='closestPoint',
                             influenceAssociation='oneToOne')
    else:
        cmds.copySkinWeights(src, dst, noMirror=True,
                             surfaceAssociation='closestPoint',
                             influenceAssociation='oneToOne')
    return skin


def rebind(mesh):
    skin = getSkinCluster(mesh)
    cmds.setAttr("{}.envelope".format(skin), 0)

    temp_geo = cmds.duplicate(mesh, name="temp_geo")[0]
    copySkinCluster(mesh, temp_geo, uv=True)

    cmds.delete(skin)

    new_skin = copySkinCluster(temp_geo, mesh)

    cmds.delete(temp_geo)

    return new_skin


def renameSkinCluster(mesh):
    skin = getSkinCluster(mesh)
    name = "{}_skinCluster".format(mesh)
    cmds.rename(skin, name)
    return name


# MESH UTILS
def deleteIntermediateShapes(mesh):
    shapes = cmds.listRelatives(mesh, s=True)
    for shape in shapes:
        if cmds.getAttr("{}.intermediateObject".format(shape)):
            cmds.delete(shape)
        else:
            cmds.rename(shape, "{}Shape".format(mesh))
    return


# JOINT UTILS
def lockJointOrient(joint):
    ro = cmds.xform(joint, ro=True, ws=True, q=True)

    jointOrient = "{}.jointOrient".format(joint)
    cmds.setAttr(jointOrient, 0, 0, 0)
    cmds.setAttr(jointOrient, lock=True)

    cmds.xform(joint, ro=ro, ws=True)
    return


def orientWorld(joint):
    cmds.joint(joint, e=True, oj="none", ch=False, zso=True)
    return


# ALIGN UTILS
def aimUpConstraint(target, base, up, upVector=[0, 1, 0], aimVector=[1, 0, 0]):
    aimConst = cmds.aimConstraint(target, base,
                                  worldUpType='object',
                                  worldUpObject=up,
                                  aimVector=aimVector,
                                  upVector=upVector)
    return aimConst
