import maya.cmds as cmds
from pixo_rigging.lib.modules.BipedModule import BipedModule;

reload(BipedModule)

# BUILD AUTORIG
def build_autoRig(name):

    # cmds.file(new=True, f=True)
    unit = cmds.currentUnit(q=True)
    cmds.currentUnit(linear='cm')
    bp = BipedModule.BipedModule(assetName=name, size=1)
    bp.build_guide()
    bp.build_rig()

    cmds.currentUnit(linear=unit)
    print "AutoRig Build Completed"

    return bp
