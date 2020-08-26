import json
import maya.cmds as cmds
from pixo_rigging.tools.Rigging.autoRig_tool.utils import curveShape


def save_controllers(json_path):
    dump_dict(get_controller_dict(), json_path)


def load_controllers(json_path):
    new_dict = load_dict(json_path)
    apply_dict_to_controllers(new_dict)


def replace_controllers(src, dst):
    src_shape = curveShape.CurveShape(src)
    dst_shape = curveShape.CurveShape(dst)

    dst_shape.set_shape(src_shape.get_shape_cmd())


def mirror_controllers():
    for shape in get_all_controllers():
        if "_L_" in shape:
            left = curveShape.CurveShape(shape)
            right = curveShape.CurveShape(shape.replace("_L_", "_R_"))

            right.set_shape(left.get_shape_cmd(mirror=True))


def reset_all_sub_controllers():
    for shape in get_all_controllers():
        if shape == "root_sub_ctrlShape":
            continue

        # add face exceptions

        if "_sub_ctrl" in shape:
            sub_shape = curveShape.CurveShape(shape)
            parent_shape = curveShape.CurveShape(shape.replace("_sub_", "_"))

            sub_shape.set_shape(parent_shape.get_shape_cmd(scale=0.8))

def reset_ctrl_position(ctrl):
    cvs = "%sShape.cv[*]"%ctrl

    ctrlPos = cmds.xform(ctrl, t=True, q=True, ws=True)
    cls, clsHdl = cmds.cluster(cvs)
    l = cmds.spaceLocator()
    cmds.matchTransform(l, clsHdl)
    cmds.xform(l, t=True, q=True, ws=True)
    clsPos = cmds.xform(l, t=True, q=True, ws=True)
    cmds.delete(cls, l)
    position = [x - y for x, y in zip(ctrlPos, clsPos)]
    cmds.xform(cvs, t=position, r=True, ws=True)


def assign_default_colors():
    color_dict = {"root": 6,
                  "global": 7,
                  "lefts": 18,
                  "rights": 13,
                  "centers": 17}

    for shape in get_all_controllers():
        if "_sub_ctrl" not in shape:
            ctrl = cmds.listRelatives(shape, p=True)[0]

            if ctrl == "root_ctrl":
                color = color_dict["root"]

            elif ctrl == "global_ctrl" or ctrl == "local_ctrl":
                color = color_dict["global"]

            elif "_L_" in ctrl:
                color = color_dict["lefts"]

            elif "_R_" in ctrl:
                color = color_dict["rights"]

            else:
                color = color_dict["centers"]

        cmds.setAttr("%s.overrideEnabled" % ctrl, True)
        cmds.setAttr("%s.overrideColor" % ctrl, color)


def get_all_controllers():
    result = list()
    for ctrl in cmds.ls("*_ctrl"):
        for shape in cmds.listRelatives(ctrl, type="nurbsCurve"):
            if "_sharedAttr" not in shape and cmds.getAttr("%s.intermediateObject" % shape) != 1:
                result.append(shape)
    result = list(set(result))
    return result


def get_controller_cmd(shape):
    controller_shape = curveShape.CurveShape(shape)
    return controller_shape.get_shape_cmd()


def get_controller_dict():
    controller_dict = dict()
    for shape in get_all_controllers():
        controller_dict[shape] = get_controller_cmd(shape)
    return controller_dict


def dump_dict(controller_dict, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(controller_dict, outfile)
    return


def load_dict(file_path):
    with open(file_path) as outfile:
        new_dict = json.load(outfile)
    return new_dict


def apply_dict_to_controllers(new_dict):
    for k, v in new_dict.iteritems():
        if not cmds.objExists(k):
            continue
        controller = curveShape.CurveShape(k)
        controller.set_shape(v)

    return


def toggle_all_subCtrl_vis():
    all_sub_ctrls = cmds.ls("*_sub_ctrl")
    all_sub_shapes = [cmds.listRelatives(subctrl, type="nurbsCurve")[0] for subctrl in all_sub_ctrls]

    is_all_subCtrl_hidden = False not in [cmds.getAttr("%s.v" % shape) == 0 for shape in all_sub_shapes]

    value = True if is_all_subCtrl_hidden else False

    all_parent_ctrls = [cmds.listRelatives(subctrl, p=True)[0] for subctrl in all_sub_ctrls]
    for ctrl in all_parent_ctrls:
        try:
            cmds.setAttr("%s.subCtrl"%ctrl, value)
        except Exception as e:
            cmds.warning(e)

    return
