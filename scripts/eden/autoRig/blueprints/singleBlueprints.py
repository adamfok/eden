from . import blueprints
import maya.cmds as cmds


class SingleBlueprints(blueprints.Blueprints):

    def __init__(self, prefix):
        super(SingleBlueprints, self).__init__(prefix)

    def build(self):
        blueprintsGrp = cmds.group(empty=True, parent=self.topBlueprints, name='{}_blueprints'.format(self.prefix))

        guide = cmds.spaceLocator(name="{}_guide".format(self.prefix))[0]
        cmds.setAttr("{}.displayHandle".format(guide), 1)

        cmds.parent(guide, blueprintsGrp)

        self.handles = [guide]
        self.guides = [guide]
