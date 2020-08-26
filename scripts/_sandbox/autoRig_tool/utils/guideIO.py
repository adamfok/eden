import json
import maya.cmds as cmds
import pymel.core as pm
from collections import OrderedDict


def save_positions(json_path):
    dump_dict(get_guide_dict(), json_path)


def load_positions(json_path):
    new_dict = load_dict(json_path)
    apply_dict_to_guide(new_dict)


def import_guides(guide_path):
    cmds.file(guide_path, i=True)


def create_guide_display():
    name = "guide_display"
    if cmds.objExists(name):
        cmds.delete(name)

    guide_display = cmds.group(empty=True, name=name)
    cmds.setAttr("%s.overrideEnabled" % guide_display, 1)
    cmds.setAttr("%s.overrideDisplayType" % guide_display, 2)

    for guide in get_all_guides()[1:]:  # skip first
        c = cmds.curve(d=1, p=[[0, 0, 0], [0, 0, 1]])
        c_shape = cmds.listRelatives(c, type="nurbsCurve")[0]
        c_shape = cmds.rename(c_shape, "%s_display" % guide)

        guide_shape = cmds.listRelatives(guide, type="locator")[0]

        parent_guide = cmds.listRelatives(guide, p=True)
        parent_guide_shape = cmds.listRelatives(parent_guide, type="locator")[0]

        cmds.connectAttr("%s.worldPosition[0]" % guide_shape, "%s.controlPoints[0]" % c_shape)
        cmds.connectAttr("%s.worldPosition[0]" % parent_guide_shape, "%s.controlPoints[1]" % c_shape)

        if "up" in guide:
            cmds.setAttr("%s.template" % c_shape, 1)

        cmds.parent(c_shape, guide_display, s=True, add=True, r=True)
        cmds.delete(c)


def create_joint_display():

    for guide in get_all_guides():
        if "up" in guide:
            continue

        pm.select(clear=True)
        j = cmds.joint(name=guide.replace("guide", "jointDisplay"))
        cmds.setAttr("%s.overrideEnabled" % j, 1)
        cmds.setAttr("%s.overrideDisplayType" % j, 2)
        cmds.parentConstraint(guide, j, mo=False)


        parent_guide = cmds.listRelatives(guide, p=True)[0]
        parent_joint = parent_guide.replace("guide", "jointDisplay")
        if cmds.objExists(parent_joint):
            pm.parent(j, parent_joint)


def get_guide_position(guide):
    loc = cmds.spaceLocator()

    cmds.matchTransform(loc, guide)
    position = cmds.xform(loc, q=True, ws=True, t=True)

    cmds.delete(loc)

    return position


def get_all_guides():
    all_guides = [cmds.listRelatives(loc, p=True)[0] for loc in
                  cmds.listRelatives("hip_01_guide", ad=True, type="locator")]

    return all_guides


def get_guide_dict():
    guide_dict = OrderedDict()

    for guide in get_all_guides():
        guide_dict[guide] = get_guide_position(guide)

    return guide_dict


def dump_dict(guide_dict, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(guide_dict, outfile)


def load_dict(file_path):
    with open(file_path) as outfile:
        new_dict = json.load(outfile, object_pairs_hook=OrderedDict)

    return new_dict


def apply_dict_to_guide(new_dict):
    for k, v in new_dict.iteritems():
        if not cmds.objExists(k):
            continue
        cmds.xform(k, t=v, ws=True)
        locatorShape = cmds.listRelatives(k, type="locator")[0]
        cmds.setAttr("%s.localPosition" % locatorShape, 0, 0, 0)
    return


def mirror_guides():
    mGuides = []
    mirrorMatrix = pm.createNode("composeMatrix", name="guide_mirror_matrix")
    mirrorMatrix.inputScaleX.set(-1)

    for guide in pm.ls("*_L_*guide"):
        mGuideName = guide.name().replace("_L_", "_R_")

        if pm.objExists(mGuideName):
            mGuide = pm.PyNode(mGuideName)
        else:
            mGuide = pm.spaceLocator(name=mGuideName)

        mGuides.append(mGuide)

        dMat = pm.createNode("decomposeMatrix", name='%s_dm' % mGuide)
        mm = pm.createNode("multMatrix", name="%s_mm" % mGuide)

        guide.worldMatrix[0] >> mm.matrixIn[0]
        mirrorMatrix.outputMatrix >> mm.matrixIn[1]
        mGuide.parentInverseMatrix[0] >> mm.matrixIn[2]

        mm.matrixSum >> dMat.inputMatrix

        dMat.outputTranslate >> mGuide.t

        for uAttr in guide.listAttr(ud=True):
            pm.connectAttr("%s.%s" % (guide, uAttr.attrName()), "%s.%s" % (mGuide, uAttr.attrName()))


def unMirror_guides():
    guides = pm.ls("*_L_*guide")

    for guide in guides:
        mGuide = guide.name().replace("_L_", "_R_")

        pm.delete('%s_dm' % mGuide)
        # pm.delete("%s_mm" %mGuide)

        for uAttr in guide.listAttr(ud=True):
            pm.disconnectAttr("%s.%s" % (guide, uAttr.attrName()), "%s.%s" % (mGuide, uAttr.attrName()))


def get_prefix(node):
    splits = node.name().split("_")
    return "_".join(splits[:-2])


def get_end_guide(node):
    prefix = get_prefix(node)
    result = None
    for i in range(0, 10):
        name = "%s_%02d_guide" % (prefix, i)
        if pm.objExists(name):
            result = name

    return pm.PyNode(result)


def get_up_guide(node):
    prefix = get_prefix(node)
    return pm.PyNode("%s_up_guide" % prefix)

def get_start_guide(node):
    prefix = get_prefix(node)
    return pm.PyNode("%s_01_guide" % prefix)


def get_distance_between(p1, p2):
    db = pm.createNode("distanceBetween")
    p1.worldMatrix[0].connect(db.inMatrix1)
    p2.worldMatrix[0].connect(db.inMatrix2)

    result = db.distance.get()
    pm.delete(db)
    return result

def create_guide_plane(name):
    # PLANE
    plane = pm.nurbsPlane(ax=[0, 1, 0], w=1, lr=1, d=3, u=2, v=1, ch=0, name=name)[0]
    plane.overrideEnabled.set(1)
    plane.overrideDisplayType.set(2)

    plane.translateX.set(0.5)

    pm.makeIdentity(plane, apply=True, t=1, r=1, s=1, n=0, pn=1)
    plane.scalePivot.set(0, 0, 0)
    plane.rotatePivot.set(0, 0, 0)

    pm.makeIdentity(plane, apply=True, t=1, r=1, s=1, n=0, pn=1)

    return plane

def create_up_display(node):

    start = get_start_guide(node)
    end = get_end_guide(node)
    up = get_up_guide(node)

    plane = create_guide_plane(name="%s_plane"%up)

    width_db = pm.createNode("distanceBetween")
    start.worldMatrix[0].connect(width_db.inMatrix1)
    up.worldMatrix[0].connect(width_db.inMatrix2)

    length_db = pm.createNode("distanceBetween")
    start.worldMatrix[0].connect(length_db.inMatrix1)
    end.worldMatrix[0].connect(length_db.inMatrix2)

    width_db.distance.connect(plane.sy)
    width_db.distance.connect(plane.sz)
    length_db.distance.connect(plane.sx)

    pm.aimConstraint(end, plane, worldUpType='object', worldUpObject=up, aimVector=[1, 0, 0], upVector=[0, 0, 1], mo=False)
    pm.pointConstraint(start, plane, mo=False)

def delete_up_display(node):
    up = get_up_guide(node)
    plane = "%s_plane" % up
    if pm.objExists(plane):
        pm.delete(plane)


def pin_children(node):
    pass_nodes = ["foot_L_01_guide",
                  "foot_R_01_guide",
                  "arm_R_01_guide",
                  "hand_R_01_guide",
                  "thumb_R_01_guide",
                  "index_R_01_guide",
                  "middle_R_01_guide",
                  "ring_R_01_guide",
                  "pinky_R_01_guide",
                  "arm_L_01_guide",
                  "hand_L_01_guide",
                  "thumb_L_01_guide",
                  "index_L_01_guide",
                  "middle_L_01_guide",
                  "ring_L_01_guide",
                  "pinky_L_01_guide",
                  "head_01_guide"]

    children = node.listRelatives(type="transform")
    if not pm.objExists("pin"):
        pin = pm.group(empty=True, name="pin")
    else:
        pin = pm.PyNode("pin")

    for child in children:
        if child in pass_nodes:
            pin_children(child)
        else:
            pm.parentConstraint(pin, child, mo=True)


def delete_pin():
    if not pm.objExists("pin"):
        return

    for const in list(set(pm.listConnections("pin", type="constraint"))):
        pm.delete(const)

    pm.delete("pin")


def create_landmark_guide(name, position):
    loc = pm.spaceLocator(name=name)
    loc.t.set(position)
    loc.displayHandle.set(1)
    # pm.matchTransform(loc, "head_02_guide")
    annotate = pm.annotate(loc, text=name)
    pm.parent(annotate.getParent(), loc, r=True)
    annotate.displayArrow.set(0)
    annotate.getParent().overrideEnabled.set(1)
    annotate.getParent().overrideDisplayType.set(2)
    return loc


def create_landmark_guides():
    head_end = create_landmark_guide(name="head_end", position=pm.xform("head_02_guide", q=True, t=True, ws=True))
    neck = create_landmark_guide(name="neck", position=pm.xform("neck_01_guide", q=True, t=True, ws=True))
    crouch = create_landmark_guide(name="crouch", position=pm.xform("hip_02_guide", q=True, t=True, ws=True))
    leg = create_landmark_guide(name="leg", position=pm.xform("leg_L_01_guide", q=True, t=True, ws=True))
    foot = create_landmark_guide(name="foot", position=pm.xform("foot_L_01_guide", q=True, t=True, ws=True))
    foot_end = create_landmark_guide(name="foot_end", position=pm.xform("foot_L_03_guide", q=True, t=True, ws=True))
    shoulder = create_landmark_guide(name="shoulder", position=pm.xform("arm_L_01_guide", q=True, t=True, ws=True))
    hand = create_landmark_guide(name="hand", position=pm.xform("hand_L_01_guide", q=True, t=True, ws=True))
    thumb_end = create_landmark_guide(name="thumb_end", position=pm.xform("thumb_L_03_guide", q=True, t=True, ws=True))
    index_end = create_landmark_guide(name="index_end", position=pm.xform("index_L_04_guide", q=True, t=True, ws=True))
    middle_end = create_landmark_guide(name="middle_end",
                                       position=pm.xform("middle_L_04_guide", q=True, t=True, ws=True))
    ring_end = create_landmark_guide(name="ring_end", position=pm.xform("ring_L_04_guide", q=True, t=True, ws=True))
    pinky_end = create_landmark_guide(name="pinky_end", position=pm.xform("pinky_L_04_guide", q=True, t=True, ws=True))

    heads = [["head_02_guide"], ["head_01_guide", "neck_02_guide"], ["neck_01_guide"]]
    bodys = [["spine_04_guide"], ["spine_03_guide"], ["spine_02_guide"], ["spine_01_guide"], ["hip_01_guide"],
             ["hip_02_guide"]]
    clavs = [[], ["clav_L_01_guide"], ["clav_L_02_guide"]]
    arms = [["arm_L_01_guide"], ["arm_L_02_guide"], ["arm_L_03_guide", "hand_L_01_guide"]]
    thumbs = [[], ["thumbRoot_L_01_guide"], ["thumbRoot_L_02_guide", "thumb_L_01_guide"], ["thumb_L_02_guide"],
              ["thumb_L_03_guide"]]
    indexs = [[], ["indexRoot_L_01_guide"], ["indexRoot_L_02_guide", "index_L_01_guide"], ["index_L_02_guide"],
              ["index_L_03_guide"], ["index_L_04_guide"]]
    middles = [[], ["middleRoot_L_01_guide", "hand_L_02_guide"], ["middleRoot_L_02_guide", "middle_L_01_guide"],
               ["middle_L_02_guide"], ["middle_L_03_guide"], ["middle_L_04_guide"]]
    rings = [[], ["ringRoot_L_01_guide"], ["ringRoot_L_02_guide", "ring_L_01_guide"], ["ring_L_02_guide"],
             ["ring_L_03_guide"], ["ring_L_04_guide"]]
    pinkys = [[], ["pinkyRoot_L_01_guide"], ["pinkyRoot_L_02_guide", "pinky_L_01_guide"], ["pinky_L_02_guide"],
              ["pinky_L_03_guide"], ["pinky_L_04_guide"]]
    legs = [["leg_L_01_guide"], ["leg_L_02_guide"], ["leg_L_03_guide"]]
    foots = [["foot_L_01_guide"], ["foot_L_02_guide"], ["foot_L_03_guide"]]

    spread_locators(head_end, neck, heads)
    spread_locators(neck, crouch, bodys)
    spread_locators(leg, foot, legs)
    spread_locators(foot, foot_end, foots)
    spread_locators(neck, shoulder, clavs)
    spread_locators(shoulder, hand, arms)

    spread_locators(hand, thumb_end, thumbs)
    spread_locators(hand, index_end, indexs)
    spread_locators(hand, middle_end, middles)
    spread_locators(hand, ring_end, rings)
    spread_locators(hand, pinky_end, pinkys)

    pm.setAttr("hip_01_guide.v", 0)
    pm.setAttr("guide_display.v", 0)


def delete_landmark_guides():
    locs = ["head_end",
            "neck",
            "crouch",
            "leg",
            "foot",
            "foot_end",
            "shoulder",
            "hand",
            "thumb_end",
            "index_end",
            "middle_end",
            "ring_end",
            "pinky_end", ]

    for loc in locs:
        pm.delete(pm.listConnections(loc, type="constraint"))

    pm.delete(locs)

    pm.setAttr("hip_01_guide.v", 1)
    pm.setAttr("guide_display.v", 1)


def spread_locators(start, end, locs):
    for i in range(len(locs)):
        space = i * (1.0 / (len(locs) - 1))

        for loc in locs[i]:
            if loc:
                if i == 0: #start
                    pm.pointConstraint(start, loc, mo=False)
                elif i == len(locs) - 1: #end
                    pm.pointConstraint(end, loc, mo=False)
                else:
                    pm.pointConstraint(start, loc, mo=True, w=(1-space))
                    pm.pointConstraint(end, loc, mo=True, w=space)


    # for i in range(len(locs)):
    #     space = i * (1.0 / (len(locs) - 1))
    #
    #     for loc in locs[i]:
    #         if loc:
    #             const = pm.pointConstraint(start, end, loc, mo=True)
    #             const.w0.set(1 - space)
    #             const.w1.set(space)


if __name__ == "__main__":
    create_landmark_guides()

    # delete_landmark_guides()
