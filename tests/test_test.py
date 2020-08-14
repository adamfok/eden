import maya.cmds as mc

def test_cube():
    mc.file(new=True, force=True)
    cube = mc.polyCube(name="cube")[0]
    assert cube == "cube"

def test_afk_node():
    mc.loadPlugin('afk_nodes.mll')
    mc.createNode("afkToggleNode", name = "toggle")
    assert mc.objExists("toggle") == True