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


def setAttrDv(attr, value):
    cmds.addAttr(attr, e=True, dv=value)


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


def lockAttr(attr):
    for fullAttr in listAttrs(attr):
        cmds.setAttr(fullAttr, lock=True)
        cmds.setAttr(fullAttr, channelBox=True)


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

    toggle = not (_hdl and _laxis)
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
    skin = cmds.skinCluster(joints, dst, tsb=True)[0]
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


def filterSelectionByComponent(componentType):
    componetTypes = ["face", "edge", "vertex"]

    if componentType not in componetTypes:
        print "Invalid Component Type : %s, expect (%s)" % (componetType, componetTypes)
        return

    selection = cmds.ls(sl=True, type='float3')  # this is obscure maya way to get only components
    if componentType == "face":
        result = cmds.polyListComponentConversion(selection, ff=True, tf=True)

    elif componentType == "edge":
        result = cmds.polyListComponentConversion(selection, fe=True, te=True)

    elif componentType == "vertex":
        result = cmds.polyListComponentConversion(selection, fv=True, tv=True)

    return result


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


def isDisplayController():
    return cmds.modelEditor(getCurrentPanel(), q=True, controllers=True)


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
    toggle = not (isDisplayCurve())
    cmds.modelEditor(getCurrentPanel(), edit=True, nurbsCurves=toggle)
    cmds.modelEditor(getCurrentPanel(), edit=True, cv=toggle)


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


def toggleDisplayController():
    toggle = not (isDisplayController())
    cmds.modelEditor(getCurrentPanel(), edit=True, nurbsCurves=toggle)
    cmds.modelEditor(getCurrentPanel(), edit=True, cv=toggle)
    cmds.modelEditor(getCurrentPanel(), edit=True, controllers=toggle)


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


# SKIN CLUSTER UTILS

def getSkinClusterJointInfo(skinCluster):
    """
    Returns:
        dict     [jointName(str) : jointIndex(int)]
    """
    result = dict()
    _connections = cmds.listConnections("{}.matrix".format(skinCluster), type="joint", c=True)
    names = _connections[1::2]
    indexs = [int(s[s.find("[") + 1: s.find("]")]) for s in _connections[0::2]]

    for name, index in zip(names, indexs):
        result[name] = index
    return result


def getWeightListFromJoint(skinCluster, joint):
    jointInfo = getSkinClusterJointInfo(skinCluster)
    jointIndex = jointInfo[joint]
    return cmds.getAttr("{}.wl[*].w[{}]".format(skinCluster, jointIndex))


def getVtxPositionList(mesh):
    positions = cmds.xform('%s.vtx[*]' % mesh, q=True, ws=True, t=True)
    return [positions[i:i + 3] for i in range(0, len(positions), 3)]


def applyWeightsByJoint(skinCluster, joint, weightList):
    jointInfo = getSkinClusterJointInfo(skinCluster)
    jointIndex = jointInfo[joint]

    for vtx, w in enumerate(weightList):
        if w == 0.0:
            continue
        pm.setAttr("{}.wl[{}].w[{}]".format(skinCluster, vtx, jointIndex), w)
    return


# DELTA MUSH TO SKIN CLUSTER CONVERTER
def convertVtxDeltaToWeights(mesh):
    joints = getSkinJoints(mesh)
    baseVtxPositions = [xyz[1] for xyz in getVtxPositionList(mesh)]  # y pos poly

    jointDeltaDict = dict()
    for jnt in joints:
        cmds.move(0, 1, 0, jnt, r=True, pcp=True)
        pm.refresh()
        targetVtxPositions = [xyz[1] for xyz in getVtxPositionList(mesh)]  # y pos only
        cmds.move(0, -1, 0, jnt, r=True, pcp=True)

        deltas = [target - base for base, target in zip(baseVtxPositions, targetVtxPositions)]
        jointDeltaDict[jnt] = deltas

    deleteHistory(mesh)
    deleteIntermediateShapes(mesh)
    skinCluster = cmds.skinCluster(joints, mesh, tsb=True)[0]
    cmds.skinCluster(skinCluster, e=True, normalizeWeights=2)  # post
    cmds.skinCluster(skinCluster, e=True, forceNormalizeWeights=True)

    for jnt, deltas in jointDeltaDict.iteritems():
        applyWeightsByJoint(skinCluster, jnt, deltas)
    #
    # cmds.skinCluster(skinCluster, e=True, normalizeWeights=1)  # interactive
    # cmds.skinCluster(skinCluster, e=True, forceNormalizeWeights=True)


# REVIT UTILS
def rebuildPolyToCurve(edges, spans=8, degree=3):
    curve, _ = cmds.polyToCurve(edges, form=2, degree=3, conformToSmoothMeshPreview=True)
    result, _ = cmds.rebuildCurve(curve, ch=True, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,
                                  s=spans, d=degree, tol=0.01)
    return result


def isCurveOpen(curve):
    curveShape = cmds.listRelatives(curve, type="nurbsCurve")[0]
    return cmds.getAttr("{}.form".format(curveShape)) == 0


def createPointOnCuveInfos(curve, pt):
    curveShape = cmds.listRelatives(curve, type="nurbsCurve")[0]

    p = 0.00
    p_inc = 1 / float(pt - 1) if isCurveOpen(curve) else 1 / float(pt)

    result = list()
    for i in range(pt):
        ptOnCurve = cmds.createNode("pointOnCurveInfo", name="{}_ptOnCurve_{}".format(curve, i))
        cmds.connectAttr("{}.worldSpace[0]".format(curveShape), "{}.inputCurve".format(ptOnCurve))
        cmds.setAttr("{}.parameter".format(ptOnCurve), p)
        p += p_inc

        result.append(ptOnCurve)

    return result


def createAvgPointOnCurveLocator(curve, pt):
    avg = cmds.createNode("plusMinusAverage", name="{}_avgPtOnCurve".format(curve))
    cmds.setAttr("{}.operation".format(avg), 3)  # average

    loc = cmds.spaceLocator(name="{}_avgLocator".format(curve))[0]
    cmds.connectAttr("{}.output3D".format(avg), "{}.translate".format(loc))

    ptOnCurves = createPointOnCuveInfos(curve, pt)
    for i, ptOnCurve in enumerate(ptOnCurves):
        cmds.connectAttr("{}.result.position".format(ptOnCurve), "{}.input3D[{}]".format(avg, i))

    return loc


def createAvgLocatorOnEdges(edges, pt, spans, degree):
    curve = rebuildPolyToCurve(edges, spans=spans, degree=degree)
    loc = createAvgPointOnCurveLocator(curve, pt=pt)

    return curve, loc


def createLocatorsOnCurve(curve, pt):
    result = list()

    ptOnCurves = createPointOnCuveInfos(curve=curve, pt=pt)
    for poc in ptOnCurves:
        loc = cmds.spaceLocator()[0]

        fbf = cmds.createNode("fourByFourMatrix")
        vp = cmds.createNode("vectorProduct")
        dm = cmds.createNode("decomposeMatrix")

        cmds.setAttr("{}.operation".format(vp), 2)

        cmds.connectAttr("{}.normalizedNormal".format(poc), "{}.input1".format(vp))
        cmds.connectAttr("{}.normalizedTangent".format(poc), "{}.input2".format(vp))

        # popluate 4x4 matrix
        cmds.connectAttr("{}.normalizedTangentX".format(poc), "{}.in00".format(fbf))
        cmds.connectAttr("{}.normalizedTangentY".format(poc), "{}.in01".format(fbf))
        cmds.connectAttr("{}.normalizedTangentZ".format(poc), "{}.in02".format(fbf))

        cmds.connectAttr("{}.outputX".format(vp), "{}.in10".format(fbf))
        cmds.connectAttr("{}.outputY".format(vp), "{}.in11".format(fbf))
        cmds.connectAttr("{}.outputZ".format(vp), "{}.in12".format(fbf))

        cmds.connectAttr("{}.normalizedNormalX".format(poc), "{}.in20".format(fbf))
        cmds.connectAttr("{}.normalizedNormalY".format(poc), "{}.in21".format(fbf))
        cmds.connectAttr("{}.normalizedNormalZ".format(poc), "{}.in22".format(fbf))

        cmds.connectAttr("{}.positionX".format(poc), "{}.in30".format(fbf))
        cmds.connectAttr("{}.positionY".format(poc), "{}.in31".format(fbf))
        cmds.connectAttr("{}.positionZ".format(poc), "{}.in32".format(fbf))

        # output
        cmds.connectAttr("{}.output".format(fbf), "{}.inputMatrix".format(dm))

        cmds.connectAttr("{}.outputTranslate".format(dm), "{}.translate".format(loc))
        cmds.connectAttr("{}.outputRotate".format(dm), "{}.rotate".format(loc))
        cmds.connectAttr("{}.outputScale".format(dm), "{}.scale".format(loc))

        result.append(loc)

    return result


def getUVfromVertex(vtx):
    return pm.PyNode(vtx).getUV()


def isMesh(node):
    return cmds.objectType(cmds.listRelatives(node)[0]) == "mesh"


def isNurbs(node):
    return cmds.objectType(cmds.listRelatives(node)[0]) == "nurbsSurface"


def createFollicle(node, u=0.0, v=0.0):
    shape = cmds.listRelatives(node)[0]

    name = "{}_follicle_1".format(node)
    follicle = cmds.createNode('follicle', name=name)
    follicleXform = cmds.listRelatives(follicle, p=True)[0]

    if isNurbs(node):
        cmds.connectAttr("{}.local".format(shape), "{}.inputSurface".format(follicle))

    if isMesh(node):
        cmds.connectAttr("{}.outMesh".format(shape), "{}.inputMesh".format(follicle))

    cmds.connectAttr("{}.worldMatrix[0]".format(node), "{}.inputWorldMatrix".format(follicle))
    cmds.connectAttr("{}.outRotate".format(follicle), "{}.rotate".format(follicleXform))
    cmds.connectAttr("{}.outTranslate".format(follicle), "{}.translate".format(follicleXform))

    cmds.setAttr("{}.parameterU".format(follicle), u)
    cmds.setAttr("{}.parameterV".format(follicle), v)

    setAttrKeyable("{}.translate".format(follicleXform), False)
    setAttrKeyable("{}.rotate".format(follicleXform), False)

    return follicleXform


def createFollicleOnVert(vtx):
    node = vtx.split(".vtx")[0]
    u, v = getUVfromVertex(vtx)
    return createFollicle(node=node, u=u, v=v)


def createClosestPointOnNode(node):
    shape = cmds.listRelatives(node)[0]

    if isNurbs(node):
        closePointNode = cmds.createNode('closestPointOnSurface')
        cmds.connectAttr("{}.worldSpace[0]".format(shape), "{}.inputSurface".format(closePointNode))

    elif isMesh(node):
        closePointNode = cmds.createNode('closestPointOnMesh')
        cmds.connectAttr("{}.outMesh".format(shape), "{}.inMesh".format(closePointNode))

    return closePointNode


def getClosestPointUV(inPosition, node):
    p0, p1, p2 = inPosition
    closetPointNode = createClosestPointOnNode(node)
    cmds.setAttr("{}.inPosition".format(closetPointNode), p0, p1, p2)

    u = cmds.getAttr("{}.parameterU".format(closetPointNode))
    v = cmds.getAttr("{}.parameterV".format(closetPointNode))

    cmds.delete(closetPointNode)
    return u, v


def getClosestPoint(inPosition, node):
    p0, p1, p2 = inPosition
    closetPointNode = createClosestPointOnNode(node)
    cmds.setAttr("{}.inPosition".format(closetPointNode), p0, p1, p2)

    outPosition = cmds.getAttr("{}.position".format(closetPointNode))
    cmds.delete(closetPointNode)
    return outPosition


def getClosestFace(inPosition, node):
    if not isMesh(node):
        print "{} Is Not Mesh Type".format(node)

    p0, p1, p2 = inPosition
    closetPointNode = createClosestPointOnNode(node)
    cmds.setAttr("{}.inPosition".format(closetPointNode), p0, p1, p2)

    closestFaceIndex = cmds.getAttr("{}.closestFaceIndex".format(closetPointNode))
    cmds.delete(closetPointNode)
    return closestFaceIndex


def getClosestVertex(inPosition, node):
    if not isMesh(node):
        print "{} Is Not Mesh Type".format(node)

    p0, p1, p2 = inPosition
    closetPointNode = createClosestPointOnNode(node)
    cmds.setAttr("{}.inPosition".format(closetPointNode), p0, p1, p2)

    closestVertexIndex = cmds.getAttr("{}.closestVertexIndex".format(closetPointNode))
    cmds.delete(closetPointNode)
    return closestVertexIndex


def closestFollicle(inLocator, node):
    locatorShape = cmds.listRelatives(inLocator, type="locator")[0]

    closetPointNode = createClosestPointOnNode(node)
    cmds.connectAttr("{}.worldPosition[0]".format(locatorShape), "{}.inPosition".format(closetPointNode))

    follicle = createFollicle(node, u=0.0, v=0.0)
    follicleShape = cmds.listRelatives(follicle)[0]
    cmds.connectAttr("{}.parameterU".format(closetPointNode), "{}.parameterU".format(follicleShape))
    cmds.connectAttr("{}.parameterV".format(closetPointNode), "{}.parameterV".format(follicleShape))
    return


def revitObject(inObj, node):
    position = cmds.xform(inObj, q=True, t=True, ws=True)
    u, v = getClosestPointUV(position, node)
    follicle = createFollicle(node, u=u, v=v)
    cmds.parentConstraint(follicle, inObj, mo=True)
    return
