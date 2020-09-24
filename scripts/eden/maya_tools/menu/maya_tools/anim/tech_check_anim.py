def main(*args):
    import maya.cmds as cmds
    angle = 45

    sel = cmds.ls(sl=True)
    attrs = ["x", "x", "y", "y", "z", "z"]
    keys = [angle, -angle, angle, -angle, angle, -angle]

    for node in sel:
        for i in range(7):
            frame = i * 10
            cmds.setKeyframe(node, t=frame)

    for node in sel:
        for i in range(6):
            frame = (i *10) + 5
            cmds.setAttr("%s.r"%node, 0,0,0)
            cmds.setAttr("%s.r%s"%(node, attrs[i]), keys[i])
            cmds.setKeyframe(node, t=frame)