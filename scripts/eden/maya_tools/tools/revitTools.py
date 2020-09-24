import maya.cmds as cmds
import eden.utils.mayaUtils as mayaUtils
from eden.utils.loggerUtils import EdenLogger


def avgLocatorOnEdges():
    edges = mayaUtils.filterSelectionByComponent(componentType="edge")

    if not edges:
        EdenLogger.warning("No Edges Selected..")
        return

    curve, loc = mayaUtils.createAvgLocatorOnEdges(edges, pt=8, spans=8, degree=3)

    cmds.setAttr("{}.template".format(curve), 1)
    cmds.select(loc)

    return


def locatorsOnCurve():
    result = cmds.promptDialog(
        title='Create Locators On Curves',
        message='How many locators:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        style='integer',
        text=5)

    if result == 'OK':
        selection = cmds.ls(sl=True)
        if not selection:
            EdenLogger.warning("Nothing Selected.. ")
            return

        num = int(cmds.promptDialog(query=True, text=True))
        for sel in selection:
            if not mayaUtils.isCurveTransform(sel):
                EdenLogger.warning("%s Is Not Curve Type" % sel)
                mayaUtils.createLocatorsOnCurve(curve=sel, pt=num)


def locatorPerCV():
    selection = cmds.ls(sl=True)
    if not selection:
        EdenLogger.warning("Nothing Selected.. ")
        return

    for sel in selection:
        if mayaUtils.isCurveTransform(sel):
            EdenLogger.warning("%s Is Not Curve Type" % sel)
            mayaUtils.locatorPerCV(sel)
