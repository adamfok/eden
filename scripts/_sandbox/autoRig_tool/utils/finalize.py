import pymel.core as pm
# ==============================================================================
# FINALIZE RIG
# ==============================================================================
# def lock_autoRig(toggle=True):
#     if toggle:
#         print "\nLocking Auto Rig... "
#     else:
#         print "\nUnlocking Auto Rig..."
#     lock_group_visibility(toggle)
#     set_ihi_attr(toggle)
#
#     if toggle:
#         reset_display_override()
#         delete_on_publish_set()


# def lock_group_visibility(toggle):
#     print "Lock Group Visibility...",
#     nodes = ['rig_grp', 'shared_attribute']
#     for node in nodes:
#         try:
#             if toggle:
#                 pm.setAttr('%s.v' % node, not toggle)
#                 pm.setAttr('%s.v' % node, lock=toggle)
#             else:
#                 pm.setAttr('%s.v' % node, lock=toggle)
#                 pm.setAttr('%s.v' % node, not toggle)
#
#         except Exception as e:
#             print e
#     print "Complete"


def setup_debug_mode():
    master = pm.ls("*_master")[0]
    if not master.hasAttr("debug"):
        master.addAttr("debug", at="bool")

    if pm.objExists('ihi_off_set'):
        pm.select('ihi_off_set')

        for obj in pm.selected():
            if master not in obj.ihi.listConnections():
                master.debug.connect(obj.ihi)


def reset_display_override():
    for child in pm.listRelatives('hi_geo_grp', ad=True):
        child.overrideEnabled.set(0)


def delete_on_publish_set():
    if not pm.objExists('delete_on_publish'):
        pm.sets(empty=True, name='delete_on_publish')

        pm.sets('delete_on_publish', fe='extra_grp')


def add_doublePreision():
    for mesh in pm.ls(type='mesh'):
        if not mesh.hasAttr("doublePrecisionWorldMesh"):
            pm.addAttr(mesh, ln="doublePrecisionWorldMesh", sn="dpw", at="bool", dv=True)
            pm.dgdirty(a=True)
    return True


def hide_sub_ctrls():
    for node in pm.ls("*_ctrl"):
        if node.hasAttr("subCtrl"):
            node.subCtrl.set(0)
    return True


def hide_rig_grp():
    pm.setAttr("rig_grp.v", 0)
    return True


def delete_all_ctrl_keys():
    pm.cutKey(pm.ls("*_ctrl"))
    return True


def reset_ctrl_attributes():
    for ctrl in pm.ls("*_ctrl"):
        try:
            ctrl.t.set([0, 0, 0])
        except:
            pass

        try:
            ctrl.r.set([0, 0, 0])
        except:
            pass

        try:
            ctrl.tFollow.set(0)
        except:
            pass

    return True


def reset_sharedAttr_settings():
    for name in ["arm_L_attr_ctrl",
                 "arm_R_attr_ctrl",
                 "leg_L_attr_ctrl",
                 "leg_R_attr_ctrl"]:
        node = pm.PyNode(name)
        node.stretch_toggle.set(0)
        node.ikfk.set(1)

    pm.setAttr("global_ctrl.globalScale", 1)
    return True


def lock_and_hide_channels():
    for node in pm.ls("*_ctrl"):
        for attr in [node.s, node.v]:
            set_lock_and_hide_attr(attr)

    for node in pm.ls("*_pv_ctrl"):
        set_lock_and_hide_attr(node.r)
        pm.setAttr(node.rotateOrder, channelBox=False)

    # for node in ["eye_ctrl", "eye_lf_ctrl", "eye_rt_ctrl", "head_lookAt_ctrl"]:
    #     node = pm.PyNode(node)
    #     set_lock_and_hide_attr(node.r)
    #     pm.setAttr(node.rotateOrder, channelBox=False)

    return True


def reset_space_switchs():
    for ctrl in pm.ls("*_ctrl"):
        try:
            ctrl.rFollow.set("default")
        except:
            pass

    for node in ["arm_R_pv_ctrl", "arm_L_pv_ctrl", "leg_R_pv_ctrl", "leg_L_pv_ctrl", "head_lookAt_ctrl"]:
        node = pm.PyNode(node)
        node.tFollow.set("local")

    for ctrl in pm.ls("*_ik_ctrl"):
        ctrl.tFollow.set("local")

    return True


def reset_layers():
    geo_layers = pm.ls("*geo_layer")
    if geo_layers:
        geo_layers[0].displayType.set(2)

    ctrl_layers = pm.ls("*ctrl_layer")
    if ctrl_layers:
        ctrl_layers[0].displayType.set(0)

    pm.delete(pm.ls(type="animLayer"))
    return True


def set_lock_and_hide_attr(attr, toggle=True):
    if not attr.isCompound():
        if toggle:
            attr.showInChannelBox(False)
            attr.setKeyable(False)
            attr.lock()
        else:
            attr.unlock()
            attr.showInChannelBox(True)
            attr.setKeyable(True)

    else:
        for attr in attr.getChildren():
            set_lock_and_hide_attr(attr, toggle)
