import maya.cmds as cmds
import eden.core.attribute as attribute


def test_attributes_io():
    cmds.file(new=True, force=True)

    cmds.group(empty=True, name="null1")
    cmds.group(empty=True, name="null2")

    cmds.addAttr("null1", ln="test_msg", at="message")
    cmds.addAttr("null1", ln="test_msg2", at="message", multi=True, im=True)
    cmds.addAttr("null1", ln="test_msg3", at="message", multi=True, im=False)

    cmds.addAttr("null1", ln="test_mtx", at="fltMatrix")
    cmds.addAttr("null1", ln="test_mtx2", at="fltMatrix", multi=True, im=True)
    cmds.addAttr("null1", ln="test_mtx3", at="fltMatrix", multi=True, im=False)

    cmds.addAttr("null1", ln="test_cmpd", at="compound", numberOfChildren=3)
    cmds.addAttr("null1", ln="test_cmpdA", at="float", parent="test_cmpd")
    cmds.addAttr("null1", ln="test_cmpdB", at="matrix", parent="test_cmpd")
    cmds.addAttr("null1", ln="test_cmpdC", at="bool", parent="test_cmpd")

    cmds.addAttr("null1", ln="test_flt", at="float", min=0, max=1, dv=0.5)
    cmds.addAttr("null1", ln="test_str", dt="string")

    cmds.addAttr("null1", ln="test_enum", at='enum', en="off:on:half")

    for attrname in cmds.listAttr("null1", ud=True):
        attr = attribute.Attribute("%s.%s"%("null1", attrname))
        # for k, v in attr.kwargs.iteritems():
        #     print "%s : %s"%(k,v)

        attribute.Attribute.create_attr(node="null2", **attr.kwargs)