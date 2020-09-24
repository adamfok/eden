from maya.api import OpenMaya as om2

objName = "null1"
selection = om2.MSelectionList()
selection.add(objName)
mob = selection.getDependNode(0)

itr_dag = om2.MItDag(om2.MItDag.kBreadthFirst)
itr_dag.reset(mob)

while not itr_dag.isDone():
    mfn_dep = om2.MFnDependencyNode(itr_dag.currentItem())
    print mfn_dep.name()
    itr_dag.next()
