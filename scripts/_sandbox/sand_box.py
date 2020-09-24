import maya.cmds as cmds
from eden.core.components import component

reload(component)

cmds.file(new=True, force=True)

con1 = component.RigComponent("test_component", prefix='test2')
con1.setPrefix("tst3")

node1 = cmds.spaceLocator(name="%s_loc" % con1.prefix)[0]
con1.addNodes(node1)

con1.add_in_attribute(at="float", publishName="in_loc_1_tx")
cmds.connectAttr("%s.in_loc_1_tx" % con1.inputs, "%s.tx" % node1)

con2 = component.RigComponent("test2_component")
con2.setPrefix("test2")

node2 = cmds.spaceLocator(name="%s_loc" % con2.prefix)[0]
con2.addNodes(node2)

con2.add_out_attribute(at="float", publishName="out_loc_1_tx")
cmds.connectAttr("%s.tx" % node2, "%s.out_loc_1_tx" % con2.outputs)


cmds.connectAttr("{}.out_loc_1_tx".format(con2.container), "{}.in_loc_1_tx".format(con1.container))

con1.clear_component()
con2.clear_component()


c3 = component.Component.initialize("test_component")
c3.setPrefix("test3")
n3 = cmds.spaceLocator(name="%s_loc" % c3.prefix)[0]
c3.addNodes(n3)

cmds.connectAttr("%s.in_loc_1_tx" % c3.inputs, "%s.tx" % n3)


c4 = component.Component.initialize("test2_component")
c4.setPrefix("test4")
n4 = cmds.spaceLocator(name="%s_loc" % c4.prefix)[0]
c4.addNodes(n4)

cmds.connectAttr("%s.tx" % n4, "%s.out_loc_1_tx" % c4.outputs)