import maya.cmds as cmds


class Attribute(object):

    @classmethod
    def create_attr(cls, node, **kwargs):
        cmds.addAttr(node, **kwargs)

    def __init__(self, attr):
        """

        Args:
            attr: (node.attrname)
        """

        node, attrname = attr.split(".")
        self.node = node
        self.attrname = attrname
        self.attr = attr

        self.kwargs = self.get_kwargs()

    def get_kwargs(self):
        queries = [self.attributeType,
                   self.dataType,
                   self.defaultValue,
                   self.listEnum,
                   self.indexMatters,
                   self.longName,
                   self.maxValue,
                   self.minValue,
                   self.multi,
                   self.niceName,
                   self.numberOfChildren,
                   self.parent,
                   self.shortName]

        result = dict()
        for query_result in queries:
            if query_result is not None:
                kw, v = query_result
                result[kw] = v
        return result

    @property
    def attributeType(self):
        keyword = "attributeType"
        value = cmds.attributeQuery(self.attrname, node=self.node, attributeType=True)
        if value is None or value == "typed":
            return None
        return [keyword, value]

    @property
    def dataType(self):
        keyword = "dataType"
        if self.attributeType is not None:
            return None

        value = cmds.addAttr(self.attr, q=True, dataType=True)
        if value is None:
            return None
        return [keyword, value[0]]

    @property
    def defaultValue(self):
        keyword = "defaultValue"
        if self.attributeType is None:
            return None
        elif self.attributeType[1] in ["message", "compound"]:
            return None

        value = cmds.attributeQuery(self.attrname, node=self.node, listDefault=True)
        if value is None:
            return None
        return [keyword, value[0]]

    @property
    def listEnum(self):
        keyword = "en"
        value = cmds.attributeQuery(self.attrname, node=self.node, listEnum=True)
        if value:
            return [keyword, value[0]]

    @property
    def indexMatters(self):
        keyword = "indexMatters"

        if not self.multi:
            return None

        value = cmds.attributeQuery(self.attrname, node=self.node, indexMatters=True)
        if value is None:
            return None
        return [keyword, value]

    @property
    def longName(self):
        keyword = "longName"
        value = cmds.attributeQuery(self.attrname, node=self.node, longName=True)
        if value is None:
            return None
        return [keyword, value]

    @property
    def maxValue(self):
        keyword = "maxValue"

        if not cmds.attributeQuery(self.attrname, node=self.node, maxExists=True):
            return None

        value = cmds.attributeQuery(self.attrname, node=self.node, maximum=True)
        if value is None:
            return None

        return [keyword, value[0]]

    @property
    def minValue(self):
        keyword = "minValue"

        if not cmds.attributeQuery(self.attrname, node=self.node, minExists=True):
            return None

        value = cmds.attributeQuery(self.attrname, node=self.node, minimum=True)
        if value is None:
            return None
        return [keyword, value[0]]

    @property
    def multi(self):
        keyword = "multi"
        value = cmds.attributeQuery(self.attrname, node=self.node, multi=True)
        if value:
            return [keyword, value]

    @property
    def message(self):
        keyword = "message"
        value = cmds.attributeQuery(self.attrname, node=self.node, message=True)
        if value:
            return [keyword, value]

    @property
    def niceName(self):
        keyword = "niceName"
        value = cmds.attributeQuery(self.attrname, node=self.node, niceName=True)
        if value is None:
            return None
        return [keyword, value]

    @property
    def numberOfChildren(self):
        keyword = "numberOfChildren"
        value = cmds.attributeQuery(self.attrname, node=self.node, numberOfChildren=True)
        if value is None:
            return None
        return [keyword, int(value[0])]

    @property
    def parent(self):
        keyword = "parent"
        value = cmds.attributeQuery(self.attrname, node=self.node, listParent=True)
        if value is None:
            return None
        return [keyword, value[0]]

    @property
    def shortName(self):
        keyword = "shortName"
        value = cmds.attributeQuery(self.attrname, node=self.node, shortName=True)
        if value is None:
            return None
        return [keyword, value]
