from . import blueprints
import maya.cmds as cmds
import pymel.core as pm


class PlanarGuidesBP(blueprints.Blueprints):

    def __init__(self, prefix, numGuides):
        super(PlanarGuidesBP, self).__init__(prefix)

        self.numGuides = numGuides if numGuides > 2 else 2
        self.aimVector = [1, 0, 0]
        self.upVector = [0, 0, 1]
        self.lock_axis = "y"

        self.up_color = 14
        self.startEnd_color = 13
        self.mid_color = 18

        self.initial_positions = [[0, 0, 0], [0, 5, 0], [10, 0, 0]]

    def build(self):
        blueprintsGrp = cmds.group(empty=True, parent=self.topBlueprints, name='{}_blueprints'.format(self.prefix))
        guidesGrp = cmds.group(empty=True, parent=blueprintsGrp, name='{}_guides'.format(self.prefix))
        displaysGrp = cmds.group(empty=True, parent=blueprintsGrp, name='{}_displays'.format(self.prefix))
        cmds.setAttr("%s.overrideEnabled" % displaysGrp, 1)
        cmds.setAttr("%s.overrideDisplayType" % displaysGrp, 2)

        start_guide = cmds.spaceLocator(name="{}_start_guide".format(self.prefix))[0]
        cmds.setAttr("%s.overrideEnabled" % start_guide, 1)
        cmds.setAttr("%s.overrideColor" % start_guide, self.startEnd_color)

        up_guide = cmds.spaceLocator(name="{}_up_guide".format(self.prefix))[0]
        cmds.setAttr("%s.overrideEnabled" % up_guide, 1)
        cmds.setAttr("%s.overrideColor" % up_guide, self.up_color)
        cmds.setAttr("{}.displayHandle".format(up_guide), 1)

        end_guide = cmds.spaceLocator(name="{}_end_guide".format(self.prefix))[0]
        cmds.setAttr("%s.overrideEnabled" % end_guide, 1)
        cmds.setAttr("%s.overrideColor" % end_guide, self.startEnd_color)

        cmds.parent([start_guide, end_guide, up_guide], guidesGrp)

        guides = [start_guide, end_guide]
        for i in range(self.numGuides - 2):  # skip start and end
            guide = cmds.spaceLocator(name="{}_{}_guide".format(self.prefix, (i + 1)))[0]
            guides.insert(-1, guide)
            cmds.setAttr("%s.overrideEnabled" % guide, 1)
            cmds.setAttr("%s.overrideColor" % guide, self.mid_color)

        for guide in guides:
            cmds.setAttr("{}.displayHandle".format(guide), 1)

        # planar rig
        cmds.aimConstraint(end_guide, start_guide, mo=False,
                           aimVector=self.aimVector,
                           upVector=self.upVector,
                           worldUpType='object',
                           worldUpObject=up_guide)

        up_buffer = cmds.group(up_guide, name="{}_const".format(up_guide))
        cmds.pointConstraint(start_guide, end_guide, up_buffer, mo=False)

        padding = 1
        for guide in guides[1:-1]:  # skip start and end
            weight = (1.0 / (self.numGuides - 1) * padding)
            padding += 1

            buffer = cmds.group(guide, name="{}_const".format(guide))
            ptConst = pm.pointConstraint(start_guide, end_guide, buffer, mo=False)  # pymel
            cmds.orientConstraint(start_guide, buffer, mo=False)
            ptConst.w0.set(1 - weight)
            ptConst.w1.set(weight)

            cmds.setAttr("%s.t%s" % (guide, self.lock_axis), 0)
            cmds.setAttr("%s.t%s" % (guide, self.lock_axis), lock=True)

            cmds.parent(buffer, guidesGrp)

        # Planar display
        planeSurface = cmds.nurbsPlane(w=1, lr=1, d=1, ch=0, name="{}_plane".format(self.prefix))[0]
        planeShape = cmds.listRelatives(planeSurface, type="nurbsSurface")[0]
        start_guide_shape = cmds.listRelatives(start_guide, type='locator')[0]
        end_guide_shape = cmds.listRelatives(end_guide, type='locator')[0]
        up_guide_shape = cmds.listRelatives(up_guide, type='locator')[0]
        cmds.parent(planeSurface, displaysGrp)

        cmds.connectAttr("{}.worldPosition[0]".format(start_guide_shape), "{}.controlPoints[0]".format(planeShape))
        cmds.connectAttr("{}.worldPosition[0]".format(end_guide_shape), "{}.controlPoints[1]".format(planeShape))
        cmds.connectAttr("{}.worldPosition[0]".format(up_guide_shape), "{}.controlPoints[2]".format(planeShape))
        cmds.connectAttr("{}.worldPosition[0]".format(up_guide_shape), "{}.controlPoints[3]".format(planeShape))

        # build joints display
        cmds.select(clear=True)
        joints = list()
        orients = list()
        for i in range(self.numGuides):
            joint = cmds.joint(radius=0.01, name='{}_joint_{}'.format(self.prefix, (i + 1)))
            joints.append(joint)

        for i in range(self.numGuides):
            orient = cmds.group(empty=True, name='{}_orient'.format(joints[i]))
            orients.append(orient)

            cmds.parentConstraint(orient, joints[i], mo=False)

        cmds.parent(orients, displaysGrp)
        cmds.parent(joints[0], displaysGrp)

        for i in range(self.numGuides):
            cmds.pointConstraint(guides[i], orients[i], mo=False)

            if i == self.numGuides - 1:
                cmds.orientConstraint(orients[i-1], orients[i], mo=False)
                continue

            aim_target = guides[i + 1]
            cmds.aimConstraint(aim_target, orients[i], mo=False,
                               aimVector=self.aimVector,
                               upVector=self.upVector,
                               worldUpType='objectRotation',
                               worldUpVector=self.upVector,
                               # mirror joint orient
                               worldUpObject=start_guide)

        # initial position
        for node, pos in zip([start_guide, up_guide, end_guide], self.initial_positions):
            cmds.setAttr("{}.t".format(node), pos[0], pos[1], pos[2])
