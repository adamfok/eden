import os

import maya.cmds as cmds
import maya.mel as mel
import xml.etree.ElementTree as ET


def bind_mesh(node, directory):
    name = "%s_skinCluster.xml" % node.split(":")[-1]
    xml = os.path.join(directory, name)
    if os.path.exists(xml):
        bind_mesh_from_xml(node, xml)
    return


def get_influence_from_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    result = [item.attrib["source"] for item in root.findall("weights")]

    return result


def bind_mesh_from_xml(node, xml_path):
    joints = get_influence_from_xml(xml_path)
    cmds.skinCluster(joints, node, tsb=True)
    rename_skinCluster(node)


def get_all_mesh():
    all_meshs = [cmds.listRelatives(m, p=True)[0] for m in cmds.ls(type="mesh") if get_skinCluster(m)]
    return all_meshs


def get_skinCluster(node):
    return mel.eval("findRelatedSkinCluster %s" % node)


def rename_skinCluster(node):
    name = "%s_skinCluster" % node.split(":")[-1]
    skin = get_skinCluster(node)
    cmds.rename(skin, name)
    return name


def export_skinCluster(node, path):
    name = rename_skinCluster(node)
    xml = "%s.xml" % name
    skin = get_skinCluster(node)

    cmds.deformerWeights(xml, export=True, deformer=skin, path=path, vc=True)
    return


def import_skinCluster(node, path):
    name = rename_skinCluster(node)
    xml = "%s.xml" % name
    skin = get_skinCluster(node)

    assert skin, "No Skin Found"
    assert os.path.exists(os.path.join(path, xml)), "%s Not Exists" % xml

    print "Importing Weight: %s from %s/%s" % (skin, path, xml)
    cmds.setAttr("%s.normalizeWeights" % skin, 0)
    cmds.skinPercent(skin, node, pruneWeights=100, normalize=False)
    cmds.deformerWeights(xml, im=True, method="barycentric", deformer=skin, path=path)
    cmds.skinCluster(skin, e=True, forceNormalizeWeights=True)
    cmds.setAttr("%s.normalizeWeights" % skin, 1)

if __name__ == "__main__":

    # for item in cmds.ls(sl=True):
    #     export_skinCluster(item, "H:/skintest")

    for item in cmds.ls(sl=True):
        import_skinCluster(item, "H:/skintest")
