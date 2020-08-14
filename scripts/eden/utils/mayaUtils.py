import maya.cmds as cmds
import pymel.core as pm


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


def createParentGroup(node, suffix="_offset"):
    parent = cmds.listRelatives(node, p=True)

    name = "{}{}".format(node, suffix)
    grp = cmds.group(empty=True, name=name)

    cmds.matchTransform(grp, node)
    cmds.parent(node, grp)

    cmds.parent(grp, parent)

    return grp
