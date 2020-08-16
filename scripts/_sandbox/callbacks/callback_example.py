import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


callback_ids = []

def on_new_scene(client_data):
    print("New scene opened")

def on_time_changed(client_data):
    print("Time changed: {0}".format(oma.MAnimControl.currentTime().asUnits(om.MTime.uiUnit())))

def on_selection_changed(client_data):
    print("Selection changed")

def before_import(client_data):
    print("Import pre-processing")

def after_import(client_data):
    print("Import post-processing")

def on_viewport_camera_changed(model_panel, *args):
    print("Camera changed in model panel: {0}".format(model_panel))

def on_playing_back_state_changed(is_playing, client_data):
    print("Playing state changed: {0}".format(is_playing))

def on_timer_fired(elapsed_time, previous_execution_time, client_data):
    print("Timer fired")


def initializePlugin(plugin):
    global callback_ids

    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)

    callback_ids.append(om.MEventMessage.addEventCallback("NewSceneOpened", on_new_scene))
    # callback_ids.append(om.MEventMessage.addEventCallback("timeChanged", on_time_changed))
    callback_ids.append(om.MEventMessage.addEventCallback("SelectionChanged", on_selection_changed))

    callback_ids.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeImport, before_import))
    callback_ids.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImport, after_import))

    callback_ids.append(omui.MUiMessage.addCameraChangedCallback("modelPanel4", on_viewport_camera_changed))

    callback_ids.append(om.MConditionMessage.addConditionCallback("playingBack", on_playing_back_state_changed))

    callback_ids.append(om.MTimerMessage.addTimerCallback(2.5, on_timer_fired))


def uninitializePlugin(plugin):

    global callback_ids

    om.MMessage.removeCallbacks(callback_ids)
    callback_ids = []



if __name__ == "__main__":
    """
    For Development Only

    Specialized code that can be executed through the script editor to speed up the development process.

    For example: scene cleanup, reloading the plugin, loading a test scene
    """

    # Any code required before unloading the plug-in (e.g. creating a new scene)


    # Reload the plugin
    plugin_name = "callback_example.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))


    # Any setup code to help speed up testing (e.g. loading a test scene)
