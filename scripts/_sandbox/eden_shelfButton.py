import maya.cmds as cmds

plugin_name = "eden.py"

if cmds.pluginInfo(plugin_name, q=True, loaded=True):
    cmds.unloadPlugin(plugin_name)

cmds.loadPlugin(plugin_name)