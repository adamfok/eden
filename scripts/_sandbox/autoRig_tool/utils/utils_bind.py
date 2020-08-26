#===============================================================================
# INFO (__doc__)
#===============================================================================
"""
Author : Adam Chun Wai Fok

Date : Oct 2014

Description : skinning utilities functions

Note : None

"""
#===============================================================================
# IMPORT
#===============================================================================
import pymel.core as pm

def bind_like(src, dst):
    skin = get_skinCluster(src)
    joints = get_skinCluster_joints(skin)
    pm.skinCluster(joints, dst, tsb=True)
    pm.copySkinWeights(src, dst, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='oneToOne')
        
   
#===============================================================================
#---------------------------------------------------------------- SKIN CLUSTERS
#===============================================================================

def get_skinCluster(mesh):
    """
    return skinCluster (string) from mesh (string)
    """
    skinCluster = pm.mel.eval('findRelatedSkinCluster("%s")' %(mesh))
    result = pm.PyNode(skinCluster)
    
    return  result

def get_skinCluster_joints(skinCluster):
    return [ y for x, y  in skinCluster.matrix.listConnections(type='joint', c=True)] 
    
def get_skinCluster_jointIndex(skinCluster):
    return [ x.index() for x, y  in skinCluster.matrix.listConnections(type='joint', c=True)]

def get_skinCluster_jointInfo(skinCluster):
    """
    return {jointName : jointIndex}
    """
    result = {}
    for x, y in skinCluster.matrix.listConnections(type='joint', c=True):
         result[y.name()] = x.index()
         
    return result
    
def get_joint_weightMap( mesh, joint ):
    result = []
    skin = get_skinCluster(mesh)
    jointInfo = get_skinCluster_jointInfo(skin)
    
    jointIndex = jointInfo[joint]
    
    for vertex in xrange(mesh.numVertices()):
        weight = pm.getAttr("%s.wl[%d].w[%d]" %(skin, vertex, jointIndex))
        result.append(weight)
        
    return result

def set_vertex_weights(mesh, joint, weightMap):
    result = []
    skin = get_skinCluster(mesh)
    jointInfo = get_skinCluster_jointInfo(skin)
    
    jointIndex = jointInfo[joint]

    for vertex in xrange(mesh.numVertices()):
        pm.setAttr("%s.wl[%s].w[%s]" %(skin, vertex, jointIndex), weight)
    
    return

def multiply_weightMaps(weightMaps):
    result = []
    for i in range(len(weightMaps[0])):
        weight = 1
        
        for weightMap in weightMaps:
            weight = weight * weightMap[i]
            
        result.append(weight)
        
    return result
        
def copy_vertex_weight (src_mesh, dst_mesh):
    src_skin = get_skinCluster(src_mesh)
    dst_skin = get_skinCluster(dst_mesh)
    
    src_skinCls_matrix_dict = get_skinCluster_matrix(src_mesh)
    dst_skinCls_matrix_dict = get_skinCluster_matrix(dst_mesh)
    
    pm.skinCluster(dst_skin, e=True, normalizeWeights=False)
    
    for vertex in xrange(dst_mesh.numVertices()):
        pm.skinPercent( dst_skin, "%s.vtx[%d]"%(dst_mesh, vertex), pruneWeights=100)
        
        for src_joint, src_jointIndex in src_skinCls_matrix_dict.iteritems():
            weight = pm.getAttr("%s.wl[%d].w[%d]" %(src_skin, vertex, src_jointIndex))
            
            if weight != 0.0:
                dst_jointIndex = dst_skinCls_matrix_dict[src_joint]
                pm.setAttr("%s.wl[%d].w[%d]" %(dst_skin, vertex, dst_jointIndex), weight)
                
    pm.skinCluster(dst_skin, e=True, normalizeWeights=True)
    
def add_skinCluster_weights (vertexIDs, src_mesh, dst_mesh, mask_joint=None):
    src_skin = get_skinCluster(src_mesh)
    dst_skin = get_skinCluster(dst_mesh)
    
    src_skinCls_matrix_dict = loads_skinCluster_matrix(src_mesh)
    dst_skinCls_matrix_dict = loads_skinCluster_matrix(dst_mesh)
    
    cmds.skinCluster(dst_skin, e=True, normalizeWeights=False)
    
    for vertexID in vertexIDs:
        if not mask_joint: #if no mask joint defined, overwrite weight onto dst mesh
            cmds.skinPercent( dst_skin, "%s.vtx[%s]"%(dst_mesh, vertexID), pruneWeights=100)
            maskValue = 1
        else:
            mask_jointIndex = dst_skinCls_matrix_dict[mask_joint]
            maskValue = cmds.getAttr("%s.wl[%s].w[%s]" %(dst_skin, vertexID, mask_jointIndex))
            cmds.setAttr("%s.wl[%s].w[%s]" %(dst_skin, vertexID, mask_jointIndex), 0)
                        
        for src_joint, src_jointIndex in src_skinCls_matrix_dict.iteritems():
            weight = cmds.getAttr("%s.wl[%s].w[%s]" %(src_skin, vertexID, src_jointIndex)) * maskValue
            if weight != 0.0:
                dst_jointIndex = dst_skinCls_matrix_dict[src_joint]
                cmds.setAttr("%s.wl[%s].w[%s]" %(dst_skin, vertexID, dst_jointIndex), weight)

    cmds.skinCluster(dst_skin, e=True, normalizeWeights=True)

def export_skinWeight(meshs, dir):
    #deformerWeights -export -deformer "skinCluster96" -path "V:/Adam Scripts/base_geos/halJordan/" "weight.xml";    

    for mesh in meshs:
        skin = get_skinCluster(mesh)    

    return
        
def import_skinWeight(mesh, dir):    
    #deformerWeights -import -method "index" -deformer "skinCluster96" -path "V:/Adam Scripts/base_geos/halJordan/" "weight.xml"; 
    #skinCluster -e -forceNormalizeWeights "skinCluster96";
    return

def rebind(mesh):
    src_skin = get_skinCluster(mesh)
    src_skin.envelope.set(0)    
    
    dup = pm.duplicate(mesh, name='temp_geo')[0]
    bind_like(mesh, dup)

    pm.copySkinWeights(mesh, dup, noMirror=True, uvSpace=['map1', 'map1'], surfaceAssociation='closestPoint',influenceAssociation='oneToOne')
    
    pm.delete(src_skin)
    
    bind_like(dup, mesh)
    
    pm.copySkinWeights(dup, mesh, noMirror=True, uvSpace=['map1', 'map1'], surfaceAssociation='closestPoint',influenceAssociation='oneToOne')
    
    pm.delete(dup)

def vertex_weight_to_shell(vtx):
    pm.mel.eval('artAttrSkinWeightCopy')
    
    pm.select(vtx.name().split(".")[0] + '.vtx[*]')
    pm.mel.eval('artAttrSkinWeightPaste')    
    


#===========================================================================
# DOUBLE SKINCLUSTER 
#===========================================================================
def create_inverse_bind_group(jnt, mesh):
    skin = get_skinCluster(mesh)
    mtxDict = get_skinCluster_jointInfo(skin)
    
    name="%s_invBind"%jnt.name()
    invGrp = pm.group(empty=True, name=name)
    pm.delete(pm.parentConstraint(jnt, invGrp, mo=False))
    #invGrp = add_parent_group(jnt, name=name)
    
    index = mtxDict[jnt.name()]
    pm.connectAttr("%s.worldInverseMatrix"%(invGrp.name()), "%s.bindPreMatrix[%d]"%(skin.name(), index), f=True)
    
    return invGrp    

#===============================================================================
# SKINCLUSTER SWITCH
#===============================================================================
def skinCluster_switch():
    global_sharedAttr = pm.PyNode('global_sharedAttr')

    #---------------------------------------------------------------------- HIGH
    switch = pm.createNode('condition', name='skinCluster_switch')
    global_sharedAttr.geoResolution >> switch.firstTerm
    
    switch.colorIfTrueG.set(1) #low res
    switch.colorIfFalseG.set(0) #low res
    
    for mesh in pm.listRelatives('hi_geo', ad=True, type='mesh'):
        sc = pm.listHistory(mesh, type='skinCluster')
        if sc:
            sc[0].nodeState.set(k=True)
            switch.outColorR >> sc[0].nodeState
            
    for mesh in pm.listRelatives('lo_geo', ad=True, type='mesh'):
        sc = pm.listHistory(mesh, type='skinCluster')
        if sc:
            sc[0].nodeState.set(k=True)
            switch.outColorG >> sc[0].nodeState