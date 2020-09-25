import maya.cmds as cmds

TOP_BLUEPRINTS = "blueprints"


class Blueprints(object):

    @classmethod
    def getTopBlueprints(cls):
        if not cmds.objExists(TOP_BLUEPRINTS):
            result = cmds.group(empty=True, name=TOP_BLUEPRINTS)
        else:
            result = TOP_BLUEPRINTS
        return result

    def __init__(self, prefix):
        self.topBlueprints = self.getTopBlueprints()
        self.prefix = prefix
        self.guides = list()

    def build(self):
        return

    # TODO:
    # def remove(self):
    #     return
    #
    # def rebuild(self, settings):
    #     self.remove()
    #     self.build()
    #     self.applySettings(settings)
    #
    # def applySeittings(self, settings):
    #     return