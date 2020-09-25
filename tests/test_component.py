from eden.autoRig.components import component;
import maya.cmds as cmds

reload(component)


def test_create_container():
    cmds.file(new=True, force=True)

    c1 = component.Container("test_container")
    assert c1.container == "test_container"


def test_create_components():
    cmds.file(new=True, force=True)

    c2 = component.Component("test_component")
    assert c2.moduleID == "component.Component"

    c3 = component.Component.initialize("test_component")
    assert c3.module == "component.Component"


def test_create_rig_components():
    cmds.file(new=True, force=True)

    c4 = component.RigComponent("test_rig_component")
    assert c4.module == "component.RigComponent"

    c5 = component.Component.initialize("test_rig_component")
    c5.setPrefix("test_c5")
    assert c5.module == "component.RigComponent"

    g1 = cmds.group(empty=True, name="%s_test_null_1" % c5.prefix)
    g2 = cmds.group(empty=True, name="%s_test_null_2" % c5.prefix)

    c5.addNodes([g1, g2])

    assert g1 == "test_c5_test_null_1"


def test_get_published_name():
    cmds.file(new=True, force=True)

    con1 = component.RigComponent("test_component")
    con1.setPrefix("omg_cn")

    node1 = cmds.spaceLocator(name="%s_loc" % con1.prefix)[0]
    node2 = cmds.spaceLocator(name="%s_loc2" % con1.prefix)[0]

    con1.addNodes([node1, node2])

    con1.publishNode(node1, "locator_1")
    con1.publishNode(node2, "locator_2")

    assert con1.getPublishedNode("locator_1") == "omg_cn_loc"


def test_publish_attribute():
    cmds.file(new=True, force=True)

    con1 = component.RigComponent("test_component", prefix='test')

    node1 = cmds.spaceLocator(name="%s_loc" % con1.prefix)[0]
    con1.addNodes(node1)

    con1.publishAttribute("{}.tx".format(node1), "pub_tx")
    cmds.setAttr("{}.pub_tx".format(con1.container), 100)

    assert cmds.getAttr("{}.tx".format(node1)) == 100


def test_reinvoke_component_connections():
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

    cmds.setAttr("%s.tx" % n4, 100)
    assert cmds.getAttr("%s.tx" % n3) == 100
