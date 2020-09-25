import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


def initializePlugin(plugin):
    vendor = "Chun Wai (Adam) Fok"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)

    import eden ; reload(eden)
    eden.install()


def uninitializePlugin(plugin):
    import eden
    eden.uninstall()
