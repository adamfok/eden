import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


def initializePlugin(plugin):
    vendor = "Chun Wai (Adam) Fok"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)

    from eden.custom_menu import setup as custom_menu_setup ; reload(custom_menu_setup)
    custom_menu_setup.install()

    pass


def uninitializePlugin(plugin):
    from eden.custom_menu import setup as custom_menu_setup
    custom_menu_setup.uninstall()

    pass
