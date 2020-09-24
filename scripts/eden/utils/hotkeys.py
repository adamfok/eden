import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
import eden.maya_tools.tools.groupTools as groupTools
import eden.maya_tools.tools.hashRenamer as hashRenamer


def isCommandExists(commandName):
    return cmds.runTimeCommand(commandName, q=True, exists=True)


def setHotkey(key, name, category, command=None, alt=False, ctl=False, sht=False, release=False):
    # Create Runtime Command
    _category = "Custom Scripts.{}".format(category)
    if not isCommandExists(name):
        cmds.runTimeCommand(name, ann=name, category=_category, commandLanguage="python", command=command)
    elif command is not None:
        cmds.runTimeCommand(name, e=True, command=command)

    # NameCommand is required to connect hotkey with actual command lines
    nameCommand = "{}NameCommand".format(name)
    cmds.nameCommand(nameCommand, ann=nameCommand, command=name)

    # Create Hotkeys
    if release:
        cmds.hotkey(k=key, alt=alt, ctl=ctl, sht=sht, releaseName=nameCommand)
    else:
        cmds.hotkey(k=key, alt=alt, ctl=ctl, sht=sht, name=nameCommand)

    print "Added Hotkey : \t {} \t ({}{}{}{})".format(name,
                                                      ("Shift + " if sht else ""),
                                                      ("Ctrl + " if ctl else ""),
                                                      ("Alt + " if alt else ""),
                                                      key)


def createCmd(cmd):
    return "import eden.utils.hotkeys as hk ; hk.{}".format(cmd)


def install():
    _cat = "FileIO"
    setHotkey(key="F1", ctl=True, alt=True, name="export01", category=_cat, command=createCmd("exportCmd('TEMP_01')"))
    setHotkey(key="F2", ctl=True, alt=True, name="export02", category=_cat, command=createCmd("exportCmd('TEMP_02')"))
    setHotkey(key="F3", ctl=True, alt=True, name="export03", category=_cat, command=createCmd("exportCmd('TEMP_03')"))
    setHotkey(key="F4", ctl=True, alt=True, name="export04", category=_cat, command=createCmd("exportCmd('TEMP_04')"))
    setHotkey(key="F5", ctl=True, alt=True, name="import01", category=_cat, command=createCmd("importCmd('TEMP_01')"))
    setHotkey(key="F6", ctl=True, alt=True, name="import02", category=_cat, command=createCmd("importCmd('TEMP_02')"))
    setHotkey(key="F7", ctl=True, alt=True, name="import03", category=_cat, command=createCmd("importCmd('TEMP_03')"))
    setHotkey(key="F8", ctl=True, alt=True, name="import04", category=_cat, command=createCmd("importCmd('TEMP_04')"))
    setHotkey(key="F9", ctl=True, alt=True, name="ref01", category=_cat, command=createCmd("referenceCmd('TEMP_01')"))
    setHotkey(key="F10", ctl=True, alt=True, name="ref02", category=_cat, command=createCmd("referenceCmd('TEMP_01')"))
    setHotkey(key="F11", ctl=True, alt=True, name="ref03", category=_cat, command=createCmd("referenceCmd('TEMP_01')"))
    setHotkey(key="F12", ctl=True, alt=True, name="ref04", category=_cat, command=createCmd("referenceCmd('TEMP_01')"))

    _cat = "Attribute"
    setHotkey(key="w", alt=True, name="attrResetT", category=_cat, command=createCmd("resetTranslateCmd()"))
    setHotkey(key="e", alt=True, name="attrResetR", category=_cat, command=createCmd("resetRotateCmd()"))
    setHotkey(key="r", alt=True, name="attrResetS", category=_cat, command=createCmd("resetScaleCmd()"))
    setHotkey(key="q", alt=True, name="attrResetV", category=_cat, command=createCmd("resetTransformCmd()"))

    _cat = "ViewportDisplay"
    setHotkey(key="h", alt=True, name="toggleIsoSelect", category=_cat, command=createCmd("toggleIsoSelectCmd()"))
    setHotkey(key="`", alt=True, name="toggleShowAll", category=_cat, command=createCmd("toggleShowAllCmd()"))
    setHotkey(key="1", alt=True, name="toggleShowCurve", category=_cat, command=createCmd("toggleShowCurveCmd()"))
    setHotkey(key="2", alt=True, name="toggleShowSurface", category=_cat, command=createCmd("toggleShowSurfaceCmd()"))
    setHotkey(key="3", alt=True, name="toggleShowMesh", category=_cat, command=createCmd("toggleShowPolyCmd()"))
    setHotkey(key="4", alt=True, name="toggleShowController", category=_cat,
              command=createCmd("toggleShowControlCmd()"))
    setHotkey(key="5", alt=True, name="toggleShowJoint", category=_cat, command=createCmd("toggleShowJointCmd()"))
    setHotkey(key="6", alt=True, name="toggleShowHandle", category=_cat, command=createCmd("toggleShowHandleCmd()"))
    setHotkey(key="7", alt=True, name="toggleShowLocator", category=_cat, command=createCmd("toggleShowLocatorCmd()"))

    _cat = "Selection"
    setHotkey(key="`", name="SelectToggleMode", category=_cat)
    setHotkey(key="1", name="SelectVertexMask", category=_cat)
    setHotkey(key="2", name="SelectEdgeMask", category=_cat)
    setHotkey(key="3", name="SelectFacetMask", category=_cat)

    _cat = "ViewportDisplay"
    setHotkey(key="4", name="toggleShowWire", category=_cat, command=createCmd("toggleWireframeCmd()"))
    setHotkey(key="5", name="toggleShowJointXRay", category=_cat, command=createCmd("toggleJointXrayCmd()"))
    setHotkey(key="6", name="toggleShowTexture", category=_cat, command=createCmd("toggleShowTextureCmd()"))
    setHotkey(key="9", name="toggleSelectHighlight", category=_cat, command=createCmd("toggleSelectionHighlightCmd()"))
    setHotkey(key="0", name="toggleShowSmooth", category=_cat, command=createCmd("toggleShowSmoothCmd()"))

    _cat = "Selection"
    setHotkey(key="h", name="SelectHierarchy", category=_cat)

    setHotkey(key="1", ctl=True, name="ConvertSelectionToVertices", category=_cat)
    setHotkey(key="2", ctl=True, name="ConvertSelectionToEdges", category=_cat)
    setHotkey(key="3", ctl=True, name="ConvertSelectionToFaces", category=_cat)

    # _cat = "Tools"
    # setHotkey(key="q", ctl=True, alt=True, sht=True, name="ArtPaintSkinWeightsToolOptions", category=_cat)
    # setHotkey(key="w", ctl=True, alt=True, sht=True, name="SmoothBindSkinOptions", category=_cat)
    # setHotkey(key="e", ctl=True, alt=True, sht=True, name="CreateBlendShapeOptions", category=_cat)
    # setHotkey(key="r", ctl=True, alt=True, sht=True, name="ArtPaintBlendShapeWeightsToolOptions", category=_cat)

    _cat = "MarkingMenu"
    setHotkey(key="t", name="main_mm_press", category=_cat, command=createCmd("mmMainPressCmd()"))
    setHotkey(key="t", release=True, name="main_mm_release", category=_cat, command=createCmd("mmMainReleaseCmd()"))

    # _cat = "UI"
    # setHotkey(key="!", ctl=True, alt=True, name="NodeEditorWindow", category=_cat)
    # setHotkey(key="@", ctl=True, alt=True, name="ConnectionEditor", category=_cat)
    # setHotkey(key="$", ctl=True, alt=True, name="GraphEditor", category=_cat)
    # setHotkey(key="#", ctl=True, alt=True, name="ShapeEditor", category=_cat)
    # setHotkey(key="%", ctl=True, alt=True, name="ProfilerTool", category=_cat)

    _cat = "Transform"
    setHotkey(key="g", sht=True, name="Ungroup", category=_cat)
    setHotkey(key="g", ctl=True, name="CreateGroup", category=_cat, command=createCmd("createCommonGrpCmd()"))
    setHotkey(key="g", alt=True, name="HashRenamer", category=_cat, command=createCmd("hashRenameCmd()"))
    setHotkey(key="g", ctl=True, sht=True, name="ParentGroup", category=_cat, command=createCmd("createParentGrpCmd()"))

    setHotkey(key="a", alt=True, name="MatchTransform", category=_cat)
    setHotkey(key="d", name="ToggleHandles", category=_cat, command=createCmd("toggleHandlesCmd()"))


def exportCmd(filename):
    mayaUtils.tempFileExport(filename)


def importCmd(filename):
    mayaUtils.tempFileImport(filename)


def referenceCmd(filename):
    mayaUtils.tempFileReference(filename)


def resetTranslateCmd():
    [mayaUtils.resetAttr("{}.{}".format(node, "t")) for node in cmds.ls(sl=True)]


def resetRotateCmd():
    [mayaUtils.resetAttr("{}.{}".format(node, "r")) for node in cmds.ls(sl=True)]


def resetScaleCmd():
    [mayaUtils.resetAttr("{}.{}".format(node, "s")) for node in cmds.ls(sl=True)]


def resetTransformCmd():
    [mayaUtils.resetTransformAttr(node) for node in cmds.ls(sl=True)]


def toggleIsoSelectCmd():
    mayaUtils.toggleIsolateSelection()


def toggleShowAllCmd():
    mayaUtils.toggleDisplayAll()


def toggleShowPolyCmd():
    mayaUtils.toggleDisplayPolygon()


def toggleShowCurveCmd():
    mayaUtils.toggleDisplayCurve()


def toggleShowSurfaceCmd():
    mayaUtils.toggleDisplaySurface()


def toggleShowLocatorCmd():
    mayaUtils.toggleDisplayLocator()


def toggleShowJointCmd():
    mayaUtils.toggleDisplayJoint()


def toggleShowHandleCmd():
    mayaUtils.toggleDisplayHandle()


def toggleShowSmoothCmd():
    mayaUtils.toggleDisplaySmooth()


def toggleWireframeCmd():
    mayaUtils.toggleDisplayWireframe()


def toggleJointXrayCmd():
    mayaUtils.toggleDisplayJointXray()


def toggleShowTextureCmd():
    mayaUtils.toggleDisplayTexture()


def toggleSelectionHighlightCmd():
    mayaUtils.toggleSelectHighlight()


def toggleShowControlCmd():
    mayaUtils.toggleDisplayController()


def createCommonGrpCmd():
    groupTools.createCommonGroup()


def createParentGrpCmd():
    groupTools.parentGroupDialog()


def hashRenameCmd():
    hashRenamer.hashRenamer()


def toggleHandlesCmd():
    [mayaUtils.toggleHandles(node) for node in cmds.ls(sl=True)]


def mmMainPressCmd():
    # TODO
    print "Marking Menu Press"
    return


def mmMainReleaseCmd():
    # TODO
    print "Marking Menu Release"
    return
