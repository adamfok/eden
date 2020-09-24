import maya.cmds as cmds
import os
from eden.utils import jsonUtils


def isShape(nodeType):
    return nodeType in ["mesh", "nurbsSurface", "nurbsCurve", "locator", "follicle"]


def isDAG(nodeType):
    return nodeType in ["transform", "joint"]


def exportNodeDescription(node, filepath):
    data = dict()
    data['nodeName'] = node
    data['nodeType'] = getNodeType(node)
    data['parent'] = getParent(node)
    data['isShape'] = isShape(getNodeType(node))
    data['isDAG'] = isDAG(getNodeType(node))

    if isDAG(getNodeType(node)):
        data["attributes"] = appendDAGAttributesDescription(node)
    else:
        data["attributes"] = appendAttributesDescription(node)

    data["userdefined"] = appendUserDefinedAttributesDescription(node)

    jsonUtils.save_dict_to_json(filepath, data)
    print "exported node: %s" % filepath
    return


def appendDAGAttributesDescription(node):
    data = dict()
    matrix = cmds.xform(node, ws=True, q=True, m=True)
    data["xform"] = matrix

    attrs = ["visibility", "template"]
    for attr in attrs:
        data[attr] = cmds.getAttr("{}.{}".format(node, attr))
    return data


def appendUserDefinedAttributesDescription(node):
    data = dict()
    attrs = cmds.listAttr(node, ud=True)
    if attrs:
        for attr in attrs:
            data[attr] = dict()
            if cmds.attributeQuery(attr, node=node, message=True):
                data[attr]["message"] = cmds.attributeQuery(attr, node=node, message=True)
            else:
                data[attr]["value"] = cmds.getAttr("{}.{}".format(node, attr))
                data[attr]["type"] = cmds.getAttr("{}.{}".format(node, attr), type=True)
                data[attr]["enum"] = cmds.attributeQuery(attr, node=node, enum=True)
                data[attr]["keyable"] = cmds.attributeQuery(attr, node=node, keyable=True)
                data[attr]["hidden"] = cmds.attributeQuery(attr, node=node, hidden=True)

                if cmds.attributeQuery(attr, node=node, minExists=True):
                    data[attr]["min"] = cmds.attributeQuery(attr, node=node, min=True)
                if cmds.attributeQuery(attr, node=node, maxExists=True):
                    data[attr]["max"] = cmds.attributeQuery(attr, node=node, max=True)

                data[attr]["multi"] = cmds.attributeQuery(attr, node=node, multi=True)
                data[attr]["indexMatters"] = cmds.attributeQuery(attr, node=node, indexMatters=True)
                data[attr]["numberOfChildren"] = cmds.attributeQuery(attr, node=node, numberOfChildren=True)
                data[attr]["listChildren"] = cmds.attributeQuery(attr, node=node, listChildren=True)
                data[attr]["listParent"] = cmds.attributeQuery(attr, node=node, listParent=True)
                data[attr]["listEnum"] = cmds.attributeQuery(attr, node=node, listEnum=True)
                data[attr]["listEnum"] = cmds.attributeQuery(attr, node=node, listEnum=True)
                data[attr]["listDefault"] = cmds.attributeQuery(attr, node=node, listDefault=True)
                data[attr]["longName"] = cmds.attributeQuery(attr, node=node, longName=True)
                data[attr]["shortName"] = cmds.attributeQuery(attr, node=node, shortName=True)
                data[attr]["niceName"] = cmds.attributeQuery(attr, node=node, niceName=True)

    return data


def appendAttributesDescription(node):
    data = dict()
    attrs = cmds.listAttr(node, output=True)
    for attr in attrs:
        data[attr] = cmds.getAttr("{}.{}".format(node, attr))
    return data


def exportSceneDescription(nodes, dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

    for node in nodes:
        filepath = os.path.join(dirpath, "%s.json" % node)
        exportNodeDescription(node, filepath)

    return dirpath


def buildNodeFromDescription(data):
    nodeName = data["nodeName"]
    nodeType = data["nodeType"]
    node = cmds.createNode(nodeType, name=nodeName)
    print "build node %s" % nodeName
    return node


def buildShapeFromDescription(data):
    nodeName = data["nodeName"]
    nodeType = data["nodeType"]
    parent = data["parent"]
    node = cmds.createNode(nodeType, name=nodeName, parent=parent)
    print "build shape %s" % nodeName
    return node


def parentNodeFromDescription(data):
    nodeName = data["nodeName"]
    parent = data["parent"]
    if parent:
        cmds.parent(nodeName, parent)
        print "build parent %s" % nodeName
    return


def buildSceneFromDescription(dirpath):
    jsons = jsonUtils.list_json_files(dirpath)
    datas = jsonUtils.list_dicts_from_jsons(jsons)

    nodes = list()
    for data in [d for d in datas if d["isShape"] is False]:
        nodes.append(buildNodeFromDescription(data))

    for data in [d for d in datas if d["isShape"] is True]:
        nodes.append(buildShapeFromDescription(data))

    for data in [d for d in datas if d["isDAG"] is True]:
        parentNodeFromDescription(data)

    return nodes


def getNodeType(node):
    return cmds.nodeType(node)


def getParent(node):
    parent = cmds.listRelatives(node, p=True)
    return parent[0] if parent else None


if __name__ == "__main__":
    pass
    # nodes1 = cmds.ls(sl=True)
    # # dirpath1 = "D:/data/test_scene2"
    # # exportSceneDescription(nodes1, dirpath1)
    #
    # cmds.file(new=True, f=True)
    #
    # buildSceneFromDescription(dirpath1)
