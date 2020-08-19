class MatrixUtils(object):

    @staticmethod
    def create_decomposeMatrix_network(node, name):
        dMtx = cmds.createNode("decomposeMatrix", name=name)
        cmds.connectAttr("{}.outputTranslate".format(dMtx), "{}.translate".format(node))
        cmds.connectAttr("{}.outputRotate".format(dMtx), "{}.rotate".format(node))
        cmds.connectAttr("{}.outputScale".format(dMtx), "{}.scale".format(node))
        return dMtx

    @staticmethod
    def create_multMatrix_network(nodes, name, attr=None):
        attr = attr or "worldMatrix[0]"
        name = name or "{}_mltMtx".format(nodes[0])

        mltMtx = cmds.createNode("multMatrix", name=name)
        for i, node in enumerate(nodes):
            cmds.connectAttr("{}.{}".format(node, attr), "{}.matrixIn[{}]".format(mltMtx, i))
        return mltMtx

    @staticmethod
    def matrix_constraint(src, dst, mo=True):
        prefix = dst
        if mo:
            # offset
            offsetCache = cmds.createNode("network", name="{}_offsetCache".format(prefix))

            offset_attr = "{}_offset".format(src)
            _temp_mltMtx = cmds.createNode("multMatrix", name="{}_temp_mltMtx".format(prefix))
            cmds.addAttr(offsetCache, at="matrix", ln=offset_attr)

            cmds.connectAttr("{}.worldMatrix[0]".format(dst), "{}.matrixIn[0]".format(_temp_mltMtx), f=True)
            cmds.connectAttr("{}.worldInverseMatrix[0]".format(src), "{}.matrixIn[1]".format(_temp_mltMtx), f=True)

            cmds.connectAttr("{}.matrixSum".format(_temp_mltMtx), "{}.{}".format(offsetCache, offset_attr))

            cmds.disconnectAttr("{}.matrixSum".format(_temp_mltMtx), "{}.{}".format(offsetCache, offset_attr))
            cmds.delete(_temp_mltMtx)

        dMtxName = "{}_dMtx".format(dst)
        mltMtxName = "{}_mltMtx".format(dst)

        dMtx = MatrixUtils.create_decomposeMatrix_network(dst, dMtxName)
        mltMtx = cmds.createNode("multMatrix", name=mltMtxName)

        if mo:
            cmds.connectAttr("{}.{}".format(offsetCache, offset_attr), "{}.matrixIn[0]".format(mltMtx))

        cmds.connectAttr("{}.worldMatrix[0]".format(src), "{}.matrixIn[1]".format(mltMtx), f=True)
        cmds.connectAttr("{}.parentInverseMatrix[0]".format(dst), "{}.matrixIn[2]".format(mltMtx), f=True)
        cmds.connectAttr("{}.matrixSum".format(mltMtx), "{}.inputMatrix".format(dMtx))

        return

    @staticmethod
    def matrix_constraint_with_space_switch(srcs, dst):
        prefix = dst

        offsetChoice = cmds.createNode("choice", name="{}_offsetChoice".format(prefix))
        parentChoice = cmds.createNode("choice", name="{}_parentChoice".format(prefix))
        offsetCache = cmds.createNode("network", name="{}_offsetCache".format(prefix))

        for i, src in enumerate(srcs):
            offset_attr = "{}_offset".format(src)

            _temp_mltMtx = cmds.createNode("multMatrix", name="{}_temp_mltMtx".format(prefix))
            cmds.addAttr(offsetCache, at="matrix", ln=offset_attr)

            # offset
            cmds.connectAttr("{}.worldMatrix[0]".format(dst), "{}.matrixIn[0]".format(_temp_mltMtx), f=True)
            cmds.connectAttr("{}.worldInverseMatrix[0]".format(src), "{}.matrixIn[1]".format(_temp_mltMtx), f=True)

            cmds.connectAttr("{}.matrixSum".format(_temp_mltMtx), "{}.{}".format(offsetCache, offset_attr))
            cmds.connectAttr("{}.{}".format(offsetCache, offset_attr), "{}.input[{}]".format(offsetChoice, i))

            cmds.disconnectAttr("{}.matrixSum".format(_temp_mltMtx), "{}.{}".format(offsetCache, offset_attr))
            cmds.delete(_temp_mltMtx)

            # parent
            cmds.connectAttr("{}.worldMatrix[0]".format(src), "{}.input[{}]".format(parentChoice, i))

        dMtxName = "{}_dMtx".format(prefix)
        mltMtxName = "{}_mltMtx".format(prefix)

        dMtx = MatrixUtils.create_decomposeMatrix_network(dst, dMtxName)
        mltMtx = MatrixUtils.create_multMatrix_network([offsetChoice, parentChoice], mltMtxName, attr="output")

        cmds.connectAttr("{}.matrixSum".format(mltMtx), "{}.inputMatrix".format(dMtx))
        cmds.connectAttr("{}.parentInverseMatrix[0]".format(dst), "{}.matrixIn[2]".format(mltMtx), f=True)

        # if cmds.attributeQuery('spaceSwitch', node=dst, exists=True):
        #     cmds.deleteAttr("{}.spaceSwitch".format(prefix))

        # cmds.addAttr(dst, ln='spaceSwitch', at="enum", en=":".join(srcs), k=True)
        # cmds.connectAttr("{}.spaceSwitch".format(dst), "{}.selector".format(parentChoice))
        # cmds.connectAttr("{}.spaceSwitch".format(dst), "{}.selector".format(offsetChoice))

        return offsetChoice, parentChoice, dMtx, mltMtx

    @staticmethod
    def matrix_constraint_with_split_space_switch(srcs, dst):

        space_switch_grp = Transform.buffer_group(dst, suffix="spaceSwitch")

        temp_translate = cmds.group(empty=True, name="{}_translate".format(dst))
        cmds.matchTransform(temp_translate, dst)

        temp_rotate = cmds.group(empty=True, name="{}_rotate".format(dst))
        cmds.matchTransform(temp_rotate, dst)

        # dst = space_switch_grp # temp override

        tOffsetChoice, tParentChoice, tDMtx, tMltMtx = MatrixUtils.matrix_constraint_with_space_switch(srcs,
                                                                                                       temp_translate)
        rOffsetChoice, rParentChoice, rDMtx, rMltMtx = MatrixUtils.matrix_constraint_with_space_switch(srcs,
                                                                                                       temp_rotate)

        cmds.connectAttr("{}.outputTranslate".format(tDMtx), "{}.translate".format(dst))
        cmds.connectAttr("{}.outputScale".format(tDMtx), "{}.scale".format(dst))

        cmds.connectAttr("{}.outputRotate".format(rDMtx), "{}.rotate".format(dst))

        cmds.connectAttr("{}.parentInverseMatrix[0]".format(dst), "{}.matrixIn[2]".format(tMltMtx), f=True)
        cmds.connectAttr("{}.parentInverseMatrix[0]".format(dst), "{}.matrixIn[2]".format(rMltMtx), f=True)

        cmds.addAttr(space_switch_grp, ln='parentSpace', at="enum", en=":".join(srcs), k=True)
        cmds.connectAttr("{}.parentSpace".format(space_switch_grp), "{}.selector".format(tParentChoice))
        cmds.connectAttr("{}.parentSpace".format(space_switch_grp), "{}.selector".format(tOffsetChoice))

        cmds.addAttr(space_switch_grp, ln='rotateSpace', at="enum", en=":".join(srcs), k=True)
        cmds.connectAttr("{}.rotateSpace".format(space_switch_grp), "{}.selector".format(rParentChoice))
        cmds.connectAttr("{}.rotateSpace".format(space_switch_grp), "{}.selector".format(rOffsetChoice))

        cmds.delete(temp_rotate, temp_translate)

        return

    @staticmethod
    def swap_parentInverseMatrix(node):
        invMtx = None
        plug = None

        parentInverseMatrix = "{}.parentInverseMatrix[0]".format(node)

        parents = cmds.listRelatives(node, p=True)
        if not parents:
            cmds.warning("{} Has No Parent".format(node))
            return
        else:
            parentWorldInvMtx = "{}.worldInverseMatrix[0]".format(parents[0])

        # if node's parentWorldInvMtx is connected, swap plug with node's parent's worldInverMatrix
        connections = cmds.listConnections(parentInverseMatrix, p=True)
        if connections:
            invMtx = parentWorldInvMtx
            plugs = connections

        # if not connected, check parent's worldInverseMatrix is connected, reverse swap if it is
        else:
            parent_connections = cmds.listConnections(parentWorldInvMtx, p=True)
            if parent_connections:
                invMtx = parentInverseMatrix
                plugs = parent_connections

        if invMtx and plugs:
            for plug in plugs:
                cmds.connectAttr(invMtx, plug, f=True)
                print "Connected {} >> {}".format(invMtx, plug)


