# ===========================================================================
# DOUBLE SKINCLUSTER
# ===========================================================================
def create_inverse_bind_group(jnt, mesh):
    skin = get_skinCluster(mesh)
    mtxDict = get_skinCluster_jointInfo(skin)

    name = "%s_invBind" % jnt.name()
    invGrp = pm.group(empty=True, name=name)
    pm.delete(pm.parentConstraint(jnt, invGrp, mo=False))
    # invGrp = add_parent_group(jnt, name=name)

    index = mtxDict[jnt.name()]
    pm.connectAttr("%s.worldInverseMatrix" % (invGrp.name()), "%s.bindPreMatrix[%d]" % (skin.name(), index), f=True)

    return invGrp