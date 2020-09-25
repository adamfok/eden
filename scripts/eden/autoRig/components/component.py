import maya.cmds as cmds
import os
import importlib
import eden

COMPONENTS_PATH = os.path.dirname(__file__)
COMPONENTS_PACKAGE_PATH = ".".join(COMPONENTS_PATH.split(eden.SCRIPTS_PATH + "\\")[-1].split("\\"))
# eden.autoRig.components


class Container(object):
    """
    wrapper class fro maya container
    """

    def __init__(self, name):
        self.isNew = cmds.objExists(name) is False
        self.container = cmds.container(name=name) if self.isNew else name

    def addNodes(self, nodes):
        """
        add maya nodes to container, includes relatives transform and shapes

        Args:
            nodes: list of nodes to add

        Returns: None

        """

        cmds.container(self.container, e=True, addNode=nodes, ish=True, it=True)

    def createNode(self, nodeType, name, parent=None):
        """
        create maya node , then added to container

        Args:
            nodeType: type of node to create
            name: name of the node without prefix
            parent: parent name

        Returns: created node

        """
        node = cmds.createNode(nodeType, name="{}{}".format(self.prefix, name), parent=parent)
        self.addNodes(nodes=node)

        return node

    def listNodes(self):
        """

        Returns: list of members in container

        """

        return cmds.container(self.container, query=True, nodeList=True) or []

    def removeNodes(self, nodes):
        """
        remove nodes from container

        Args:
            nodes: node name

        Returns: None

        """

        cmds.container(self.container, edit=True, removeNode=nodes)

    def publishAttribute(self, attribute, publishName):
        """

        Args:
            attribute: attribute to bind (node.attr)
            publishName: publish name

        Returns:

        """
        cmds.container(self.container, edit=True, publishName=publishName)
        cmds.container(self.container, edit=True, bindAttr=[attribute, publishName])

    def unPublishAttribute(self, attribute):
        """
        unbind and unpublish attribute

        Args:
            attribute: attribute (node.attr)

        Returns:

        """
        cmds.container(self.container, edit=True, unbindAndUnpublish=attribute)

    def setBlackBox(self, value):
        """

        Args:
            value: blackbox boolean

        Returns:

        """
        cmds.setAttr("{}.blackBox".format(self.container), value)

    def publishNode(self, node, publishName):
        """
        publish node so it not hidden when black box

        Args:
            node: node name
            publishName: publish name

        Returns:

        """

        cmds.containerPublish(self.container, publishNode=[publishName, ""])
        cmds.containerPublish(self.container, bindNode=[publishName, node])

    def getPublishedNode(self, publishName):
        """
        get node name by published name

        Args:
            publishName: publish name

        Returns:

        """
        connections = cmds.containerPublish(self.container, q=True, bindNode=True)
        node_dict = {connections[i]: connections[i + 1] for i in range(0, len(connections), 2)}
        if publishName in node_dict:
            return node_dict[publishName]
        else:
            cmds.warning("Invalid Published Name")


class Component(Container):
    """
    the base class for all components
    """
    moduleID = "component.Component"

    @classmethod
    def initialize(cls, name):
        moduleID = cmds.getAttr("%s.module" % name)
        module_splits = moduleID.split(".")
        package = ".".join([COMPONENTS_PACKAGE_PATH] + module_splits[:-1])
        module = importlib.import_module(package)
        class_name = module_splits[-1]
        class_ = getattr(module, class_name)
        # print "Initialized %s(%s) :  %s" % (class_name, name, module)
        return class_(name)

    def __init__(self, name):
        super(Component, self).__init__(name)

        if self.isNew:
            self._addComponentAttributes()

    def _addComponentAttributes(self):
        cmds.addAttr(self.container, ln="module", dt="string")
        cmds.setAttr("{}.module".format(self.container), self.moduleID, type="string")
        cmds.setAttr("{}.module".format(self.container), lock=True)

    @property
    def module(self):
        return cmds.getAttr("{}.module".format(self.container))


class RigComponent(Component):
    """
    the base class for rig components
    """
    moduleID = "component.RigComponent"

    def __init__(self, name, prefix=None):
        super(RigComponent, self).__init__(name)

        if self.isNew:
            self._initializeAttributes()
            self._create_inputs()
            self._create_outputs()

        if prefix:
            self.setPrefix(prefix)

    def _initializeAttributes(self):
        cmds.addAttr(self.container, ln="prefix", dt="string")

    @property
    def prefix(self):
        """
        get prefix attribute from container
        """
        return cmds.getAttr("{}.prefix".format(self.container)) or ""

    @property
    def inputs(self):
        # inputss = cmds.listConnections("{}.inputs".format(self.container))
        # return inputss[0] if inputss else None
        return "{}_inputs".format(self.prefix) if self.prefix else "inputs"

    @property
    def outputs(self):
        # outputss = cmds.listConnections("{}.outputs".format(self.container))
        # return outputss[0] if outputss else None
        return "{}_outputs".format(self.prefix) if self.prefix else "outputs"

    @property
    def configs(self):
        return "{}_configs".format(self.prefix) if self.prefix else "configs"

    def setPrefix(self, prefix):
        """
        set prefix attribute in container
        """
        self.removePrefix()
        cmds.setAttr("{}.prefix".format(self.container), prefix, type="string")
        self.addPrefix()

    def removePrefix(self):
        """
        Remove prefix to all nodes in container
        """
        for node in self.listNodes():
            if self.prefix in node:
                cmds.rename(node, node.replace(self.prefix + "_", ""), ignoreShape=True)
        return

    def addPrefix(self):
        """
        Add prefix to all nodes in container
        """
        for node in self.listNodes():
            if self.prefix not in node:
                cmds.rename(node, "{}_{}".format(self.prefix, node), ignoreShape=True)
        return

    def _create_inputs(self):
        """
        create inputs node for publish attributes,
        purpose is to keep the component to component connections when delete or rebuild rig

        Returns: inputs node

        """

        node = cmds.createNode("network", name="inputs")
        # cmds.connectAttr("{}.message".format(node), "{}.inputs".format(self.container))
        self.addNodes(node)
        return node

    def _create_outputs(self):
        """
        create outputs node for publish attributes
        purpose is to keep the component to component connections when delete or rebuild rig

        Returns: outputs node

        """
        node = cmds.createNode("network", name="outputs")
        # cmds.connectAttr("{}.message".format(node), "{}.outputs".format(self.container))
        self.addNodes(node)
        return node

    def add_in_attribute(self, publishName, **kwargs):
        cmds.addAttr(self.inputs, ln=publishName, **kwargs)
        self.publishAttribute("{}.{}".format(self.inputs, publishName), publishName)
        return

    def add_out_attribute(self, publishName, **kwargs):
        cmds.addAttr(self.outputs, ln=publishName, **kwargs)
        self.publishAttribute("{}.{}".format(self.outputs, publishName), publishName)
        return

    def clear_component(self):
        nodes = self.listNodes()
        nodes.remove(self.inputs)
        nodes.remove(self.outputs)
        cmds.lockNode(self.inputs, lock=True)
        cmds.lockNode(self.outputs, lock=True)
        cmds.delete(nodes)
        cmds.lockNode(self.inputs, lock=False)
        cmds.lockNode(self.outputs, lock=False)
        return

    def create_guide(self, name):
        """
        create guide lcoator and connect world matrix to "guides" attribute
        Args:
            name: guide name

        Returns: guide

        """
        return

    def create_control(self, name, publishedName):
        """
        create control and publish node in container
        Args:
            name: control name
            publishedName: published name in container

        Returns: control

        """

        return

    def create_joint(self, name, publishedName):
        """
        create joint and publish node in container
        Args:
            name: joint name
            publishedName: published name in container

        Returns:

        """
        return

    def build_guide_rig(self):
        return

    def remove_guide_rig(self):
        return

    def build_rig(self):
        return

    def remove_rig(self):
        return
