import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


# DELETE UTILS
def deleteHistory(nodes):
    cmds.select(nodes)
    mel.eval("DeleteHistory")
    cmds.select(clear=True)


def deleteConstraints(nodes):
    cmds.select(nodes)
    mel.eval("DeleteConstraints")
    cmds.select(clear=True)


def deleteNonDeformerHistory(nodes):
    cmds.select(nodes)
    mel.eval("BakeNonDefHistory")
    cmds.select(clear=True)


def deleteIntermediateShapes(mesh):
    shapes = cmds.listRelatives(mesh, s=True)
    for shape in shapes:
        if cmds.getAttr("{}.intermediateObject".format(shape)):
            cmds.delete(shape)
        else:
            cmds.rename(shape, "{}Shape".format(mesh))
    return


# ATTRIBUTES UTILS

def listAttrs(attr):
    node, attrName = attr.split(".")
    if not cmds.attributeQuery(attrName, node=node, exists=True):
        return []

    return ["{}.{}".format(node, longName) for longName in cmds.listAttr("{}.{}".format(node, attrName))]


def listAttrsFromNodes(nodes, attrNames):
    result = list()
    for node in nodes:
        for attrName in attrNames:
            attr = "{}.{}".format(node, attrName)
            result += listAttrs(attr)
    return list(set(result))


def getAttrDv(attr):
    node, attrName = attr.split(".")
    defaultValues = cmds.attributeQuery(attrName, node=node, listDefault=True)
    return defaultValues[0] if len(defaultValues) == 1 else None


def resetAttr(attr):
    for fullAttr in listAttrs(attr):
        dv = getAttrDv(fullAttr)
        if dv is not None:
            cmds.setAttr(fullAttr, dv)


def showAttr(attr):
    for fullAttr in listAttrs(attr):
        cmds.setAttr(fullAttr, lock=False)
        cmds.setAttr(fullAttr, channelBox=True)
        cmds.setAttr(fullAttr, keyable=True)


def hideAttr(attr):
    for fullAttr in listAttrs(attr):
        cmds.setAttr(fullAttr, keyable=False)
        cmds.setAttr(fullAttr, lock=True)
        cmds.setAttr(fullAttr, channelBox=False)


def setAttrKeyable(attr, keyable):
    if keyable:
        [cmds.setAttr(fullAttr, keyable=True) for fullAttr in listAttrs(attr)]
    else:
        [cmds.setAttr(fullAttr, channelBox=True) for fullAttr in listAttrs(attr)]


def hideTransformAttr(node):
    for attr in "srt":
        hideAttr("{}.{}".format(node, attr))


def showTransformAttr(node):
    for attr in "srt":
        showAttr("{}.{}".format(node, attr))


def resetTransformAttr(node):
    for attr in "srt":
        resetAttr("{}.{}".format(node, attr))


def getSelectedMainAttributes():
    nodeNames = cmds.channelBox("mainChannelBox", q=True, mol=True)
    attrNames = cmds.channelBox("mainChannelBox", q=True, sma=True)
    return listAttrsFromNodes(nodeNames, attrNames)


def getSelectedInputAttributes():
    nodeNames = cmds.channelBox("mainChannelBox", q=True, hol=True)
    attrNames = cmds.channelBox("mainChannelBox", q=True, sha=True)
    return listAttrsFromNodes(nodeNames, attrNames)


def getSelectedShapesAttributes():
    nodeNames = cmds.channelBox("mainChannelBox", q=True, sol=True)
    attrNames = cmds.channelBox("mainChannelBox", q=True, ssa=True)
    return listAttrsFromNodes(nodeNames, attrNames)


def getSelectedAttributes():
    mainAttrs = getSelectedMainAttributes()
    inputAttrs = getSelectedInputAttributes()
    shapeAttrs = getSelectedShapesAttributes()
    return mainAttrs + inputAttrs + shapeAttrs


def freezeTransform(node, t=True, r=True, s=True):
    cmds.makeIdentity(node, apply=True, t=t, r=r, s=s)
    return node


# TRANSFORM UTILS
def toggleHandles(node):
    _hdl = cmds.getAttr("{}.displayHandle".format(node))
    _laxis = cmds.getAttr("{}.displayLocalAxis".format(node))

    toggle = not(_hdl and _laxis)
    cmds.setAttr("{}.displayHandle".format(node), toggle)
    cmds.setAttr("{}.displayLocalAxis".format(node), toggle)


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


# SELECTIONS UTILS
def selectByName(name):
    cmds.select(cmds.ls(name))


def filterSeletionByType(filterType):
    isShapeType = filterType in ['mesh', 'follicle', 'nurbsCurve', "nurbsSurface", "locator", "cluster"]

    if not isShapeType:
        result = cmds.ls(sl=True, type=filterType)
    else:
        shapes = [cmds.listRelatives(node)[0] for node in cmds.ls(sl=True)]
        result = [cmds.listRelatives(shape, p=True) for shape in cmds.ls(shapes, type=filterType)]

    cmds.select(result)


# DISPLAY UTILS
def getCurrentPanel():
    return cmds.getPanel(underPointer=True)


def isIsolateSelection():
    return cmds.isolateSelect(getCurrentPanel(), q=True, state=True)


def isDisplayAll():
    return isDisplayCurve() and isDisplayPolygon() and isDisplayJoint() and isDisplaySurface()


def isDisplayCurve():
    return cmds.modelEditor(getCurrentPanel(), q=True, nurbsCurves=True)


def isDisplaySurface():
    return cmds.modelEditor(getCurrentPanel(), q=True, nurbsSurfaces=True)


def isDisplayPolygon():
    return cmds.modelEditor(getCurrentPanel(), q=True, polymeshes=True)


def isDisplayLocator():
    return cmds.modelEditor(getCurrentPanel(), q=True, locators=True)


def isDisplayDeformer():
    return cmds.modelEditor(getCurrentPanel(), q=True, deformers=True)


def isDisplayJoint():
    return cmds.modelEditor(getCurrentPanel(), q=True, joints=True)


def isDisplayHandle():
    return cmds.modelEditor(getCurrentPanel(), q=True, handles=True)


def isDisplayJointXRay():
    return cmds.modelEditor(getCurrentPanel(), q=True, jointXray=True)


def isDisplayTexture():
    return cmds.modelEditor(getCurrentPanel(), q=True, displayTextures=True)


def isDisplaySelectionHighlight():
    return cmds.modelEditor(getCurrentPanel(), q=True, selectionHiliteDisplay=True)


def toggleIsolateSelection():
    currentPanel = getCurrentPanel()
    toggle = not (isIsolateSelection())

    cmds.isolateSelect(currentPanel, state=toggle)

    if isIsolateSelection():
        cmds.isolateSelect(currentPanel, removeSelected=True)
    else:
        cmds.isolateSelect(currentPanel, addSelected=True)


def toggleDisplayAll():
    toggle = not (isDisplayCurve() and isDisplayPolygon() and isDisplayJoint() and isDisplaySurface())
    cmds.modelEditor(getCurrentPanel(), edit=True, allObjects=toggle)


def toggleDisplayCurve():
    cmds.modelEditor(getCurrentPanel(), edit=True, nurbsCurves=not (isDisplayCurve()))
    cmds.modelEditor(getCurrentPanel(), edit=True, cv=not (isDisplayCurve()))


def toggleDisplaySurface():
    cmds.modelEditor(getCurrentPanel(), edit=True, nurbsSurfaces=not (isDisplaySurface()))


def toggleDisplayPolygon():
    cmds.modelEditor(getCurrentPanel(), edit=True, polymeshes=not (isDisplayPolygon()))


def toggleDisplayLocator():
    cmds.modelEditor(getCurrentPanel(), edit=True, locators=not (isDisplayLocator()))


def toggleDisplayJoint():
    cmds.modelEditor(getCurrentPanel(), edit=True, joints=not (isDisplayJoint()))


def toggleDisplayDeformer():
    cmds.modelEditor(getCurrentPanel(), edit=True, deformers=not (isDisplayDeformer()))


def toggleDisplayJointXray():
    cmds.modelEditor(getCurrentPanel(), edit=True, jointXray=not (isDisplayJointXRay()))


def toggleDisplayTexture():
    cmds.modelEditor(getCurrentPanel(), edit=True, displayTextures=not (isDisplayTexture()))


def toggleDisplayHandle():
    cmds.modelEditor(getCurrentPanel(), edit=True, handles=not (isDisplayHandle()))


def toggleSelectHighlight():
    cmds.modelEditor(getCurrentPanel(), edit=True, selectionHiliteDisplay=not (isDisplaySelectionHighlight()))


def toggleDisplayWireframe():
    currentPanel = getCurrentPanel()

    if not cmds.modelEditor(currentPanel, q=True, displayAppearance=True) == "smoothShaded":
        cmds.modelEditor(currentPanel, edit=True, displayAppearance='smoothShaded')

    elif cmds.modelEditor(currentPanel, q=True, wireframeOnShaded=True):
        cmds.modelEditor(currentPanel, edit=True, wireframeOnShaded=False)
        cmds.modelEditor(currentPanel, edit=True, displayAppearance='wireframe')

    else:
        cmds.modelEditor(currentPanel, edit=True, wireframeOnShaded=True)


def isDisplaySmooth():
    return 3 in cmds.displaySmoothness(q=True, polygonObject=True)


def toggleDisplaySmooth():
    smoothness = 1 if isDisplaySmooth() else 3
    cmds.displaySmoothness(polygonObject=smoothness)


# FILES IO UTILS

def tempFileExport(fileName):
    path = "C:/TEMP/%s.ma" % fileName
    cmds.file(path, es=True, f=True, type='mayaAscii')
    print "file exported : %s" % path,
    return


def tempFileImport(fileName):
    path = "C:/TEMP/%s.ma" % fileName
    cmds.file(path, i=True, type="mayaAscii", ignoreVersion=True, mergeNamespacesOnClash=False, rpr=fileName, pr=True)
    print "file imported : %s" % path,
    return


def tempFileReference(fileName):
    path = "C:/TEMP/%s.ma" % fileName
    cmds.file(path, r=True, type="mayaAscii", ignoreVersion=True, mergeNamespacesOnClash=False, rpr=fileName, pr=True)
    print "file referenced : %s" % path,
    return
