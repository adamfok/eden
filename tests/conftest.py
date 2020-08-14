import atexit
import maya.standalone

maya.standalone.initialize(name="python")
atexit.register(maya.standalone.uninitialize)