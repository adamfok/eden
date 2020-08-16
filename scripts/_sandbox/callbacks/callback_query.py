from maya.api import _OpenMaya_py2 as om2

sel = om2.MGlobal.getActiveSelectionList()

mob = None
if sel.length():
    mob = sel.getDependNode(0)


def cb(msg, plug1, plug2, payload):
    print msg


if mob is not None:
    mfn_dep = om2.MFnDependencyNode(mob)
    plugTx = mfn_dep.findPlug("tx", False)
    for eachCB in om2.MMessage.nodeCallbacks(mob):
        print eachCB
        om2.MMessage.removeCallback(eachCB)

    om2.MNodeMessage.addAttributeChangedCallback(mob, cb)
