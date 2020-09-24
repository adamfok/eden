
from eden.core import attribute; reload(attribute)

node = "null1"
for attrname in cmds.listAttr(node, ud=True):
    attr = attribute.Attribute("%s.%s"%(node, attrname))
    print ""
    for k, v in attr.kwargs.iteritems():
        print "%s : %s"%(k,v)

    attribute.Attribute.create_attr(node="null2", **attr.kwargs)