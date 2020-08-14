if __name__ == "__main__":
    plugin_name = "eden.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    """
    plugin_name = "eden.py"
    
    if cmds.pluginInfo(plugin_name, q=True, loaded=True):
        cmds.unloadPlugin(plugin_name)
        
    cmds.loadPlugin(plugin_name)
    """