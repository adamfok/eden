#=======================================================================
# INFO (__doc__)
#=======================================================================
"""
File Name : controller_tool.py

Author : Adam Chun Wai Fok

Date : Dec 2014

Description : controller making tool

Arguments : 
    None    

Return : 
    None

Execute : 
    import controller_tool ; reload(controller_tool)
    controller_tool.main()

"""

#=======================================================================
# IMPORT 
#=======================================================================
import maya.cmds as cmds
import pymel.core as pm

import pixo_rigging.lib.classes.UI as class_UI
from pixo_rigging.lib.utils.utils_shape import get_valid_shapes, add_shape
from pixo_rigging.lib.utils.utils_control import add_ctrl, add_parent_group, add_sub_ctrl, add_pivot_ctrl

#=======================================================================
# MAIN()
#=======================================================================
def main(*args):
    print "\nLoading ... Controller Tool UI"
    ui = ControllerTool_UI()
    ui.show()

#=======================================================================
# CLASS
#=======================================================================
class ControllerTool_UI(class_UI.UI):

    #=======================================================================
    # __init__
    #=======================================================================
    def __init__ (self) :
        super(ControllerTool_UI, self).__init__()
        
        # Define Window
        self.window = "controller_tool_win"
        self.title = "Controller Tool v1.0"
        self.windowWidth = 250
        self.windowHeight = 600
        
        self.dock=False
        self.sizeable = True
        self.allowArea = ['left', 'right']
        
        self.topColumnWidth = self.windowWidth - 15
        
        temp = pm.group(empty=True)
        self.shapeList = sorted(get_valid_shapes())
        pm.delete(temp)

    #=======================================================================
    # Layout
    #=======================================================================
    def initialiseLayout(self):
        
        #=======================================================================
        # Top Level Layout
        #=======================================================================
        self.widgets['top_level_layout'] = pm.verticalLayout()
        self.widgets['top_level_column'] = pm.columnLayout(adj=True, rowSpacing=2, columnAttach = ['both', 5])

        #=======================================================================
        # NAME
        #=======================================================================
        #------------------------------------------------------------- Separator
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.separator(style='out')
        pm.text(label=' Name ')
        pm.separator(style='out')
        h.redistribute(1,1,1)           

        #------------------------------------------------------- Prefix / Suffix
        pm.setParent(self.widgets['top_level_column'])
        self.widgets["suffix_TFG"] = pm.textFieldGrp(label='Suffix :', cw=[1,50], adj=2, text='ctrl')

        #=======================================================================
        # CONTROL
        #=======================================================================
        #------------------------------------------------------------- Separator
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.separator(style='out')
        pm.text(label=' Control ')
        pm.separator(style='out')
        h.redistribute(1,1,1)        

        #----------------------------------------------------------- Offset Node
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        self.widgets['offsetNode_CB'] = pm.checkBox( label = 'Offset Node ', value=True)
        self.widgets['offsetNode_TF'] = pm.textField(text='offset')
        h.redistribute(1,2)
        
        #--------------------------------------------------------------- Joint
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        self.widgets['joint_CB'] = pm.checkBox( label = 'Create Joint', value=False)
        self.widgets['jointGroup_RBG'] = pm.radioButtonGrp( labelArray2=['Each Object', 'All Objects'], 
                                                              numberOfRadioButtons=2 , 
                                                              cw=[1,100], 
                                                              adj=3, 
                                                              select=1)
        h.redistribute(1,2)
        
        #------------------------------------------------------------- ShapeNode
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        self.widgets['shape_CB'] = pm.checkBox( label = 'Shape Node ', value=True)
        self.widgets['shape_TSL'] = pm.textScrollList( numberOfRows=5, 
                                                       allowMultiSelection=False, 
                                                       append = self.shapeList, 
                                                       selectIndexedItem=1)
        h.redistribute(1,2)
        
        #------------------------------------------------------------ Shape Axis
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.text(label = 'Shape Axis')
        self.widgets['shapeAxis_OM'] = pm.optionMenu()
        pm.menuItem(label = "+x")
        pm.menuItem(label = "+y")
        pm.menuItem(label = "+z")
        pm.menuItem(label = "-x")
        pm.menuItem(label = "-y")
        pm.menuItem(label = "-z")        
        h.redistribute(1,2)
        
        #------------------------------------------------------------- Hierarchy
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()  
        pm.text(label='Parent')      
        self.widgets['hierarchry_RB'] = pm.radioButtonGrp( labelArray2=['World', 'Selection Order'], 
                                                           numberOfRadioButtons=2 , 
                                                           cw=[1,100], 
                                                           adj=3, 
                                                           select=1)
        h.redistribute(1,2)        
        
        #------------------------------------------------------- Constraint Type
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.text(label='Constraint Type:')
        self.widgets['tConst_CB'] = pm.checkBox(label='Point', value=False)
        self.widgets['rConst_CB'] = pm.checkBox(label='Orient', value=False)
        h.redistribute(1,1,1)
        
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.text(label="")
        self.widgets['pConst_CB'] = pm.checkBox(label='Parent', value=True)
        self.widgets['sConst_CB'] = pm.checkBox(label='Scale', value=True)
        h.redistribute(1,1,1)   
        
        #--------------------------------------------------------- Create Button
        pm.setParent(self.widgets['top_level_column'])
        self.widgets['create_BTN'] = pm.button( label="Create Control(s)",
                                                h=50, 
                                                c=pm.Callback(self.create_BTN_pressed))
        
        #--------------------------------------------------------- Create Button
        pm.setParent(self.widgets['top_level_column'])
        self.widgets['createSubCtrl_BTN'] = pm.button( label="Create Sub Control",
                                                c=pm.Callback(self.createSubCtrl_BTN_pressed))        
        
        #--------------------------------------------------------- Create Button
        pm.setParent(self.widgets['top_level_column'])
        self.widgets['createPivot_BTN'] = pm.button( label="Create Pivot Control",
                                                c=pm.Callback(self.createPivot_BTN_pressed))          
        
        #=======================================================================
        # EDIT
        #=======================================================================

        #------------------------------------------------------------- Separator
        pm.setParent(self.widgets['top_level_column'])
        pm.separator(style="none", h=10)
                
        h = pm.horizontalLayout()
        pm.separator(style='out')
        pm.text(label=' Edit Color')
        pm.separator(style='out')
        h.redistribute(1,1,1)            
        
        #----------------------------------------------------------------- Color
        pm.setParent(self.widgets['top_level_column'])
        main_layout = pm.formLayout()
        columns = 32 / 2
        rows = 2
        cell_width = 24
        cell_height = 24

        self.widgets['color_palette'] = pm.palettePort( dimensions=(columns, rows), 
                                                        transparent=0,
                                                        width=(columns*cell_width),
                                                        height=(rows*cell_height),
                                                        topDown=True,
                                                        colorEditable=False,
                                                        changeCommand=pm.Callback(self.color_palette_changed));
        for index in range(1, 32):
            color_component = pm.colorIndex(index, q=True)
            pm.palettePort( self.widgets['color_palette'],
                            edit=True,
                            rgbValue=(index, color_component[0], color_component[1], color_component[2]))


        #------------------------------------------------------------- Separator
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.separator(style='out')
        pm.text(label=' Edit Channels')
        pm.separator(style='out')
        h.redistribute(1,1,1)     
        
        #--------------------------------------------------------------- Channel
        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.text(label='Translate')
        self.widgets['tHide_BTN'] = pm.button(label='Hide', command=pm.Callback(self.tHide_BTN_pressed))        
        self.widgets['tShow_BTN'] = pm.button(label='Show', command=pm.Callback(self.tShow_BTN_pressed))
        pm.text(label='Rotate')
        self.widgets['rHide_BTN'] = pm.button(label='Hide', command=pm.Callback(self.rHide_BTN_pressed))        
        self.widgets['rShow_BTN'] = pm.button(label='Show', command=pm.Callback(self.rShow_BTN_pressed))
        h.redistribute(1,1,1,1,1,1)

        pm.setParent(self.widgets['top_level_column'])
        h = pm.horizontalLayout()
        pm.text(label='Scale')
        self.widgets['sHide_BTN'] = pm.button(label='Hide', command=pm.Callback(self.sHide_BTN_pressed))        
        self.widgets['sShow_BTN'] = pm.button(label='Show', command=pm.Callback(self.sShow_BTN_pressed))
        pm.text(label='Visibility')
        self.widgets['vHide_BTN'] = pm.button(label='Hide', command=pm.Callback(self.vHide_BTN_pressed))        
        self.widgets['vShow_BTN'] = pm.button(label='Show', command=pm.Callback(self.vShow_BTN_pressed))
        h.redistribute(1,1,1,1,1,1)        
        
        #=======================================================================
        # Redistribute
        #=======================================================================
        self.widgets['top_level_layout'].redistribute()                           
        
    #===========================================================================
    # CALLBACK
    #===========================================================================
    def color_palette_changed(self):
        colorIndex = self.widgets['color_palette'].getSetCurCell()
        for obj in pm.selected():
            obj.overrideEnabled.set(True) 
            obj.overrideColor.set(colorIndex)

    def tHide_BTN_pressed(self):
        for obj in pm.selected(): obj.translate.set_lock_and_hide(True)
        
    def tShow_BTN_pressed(self):
        for obj in pm.selected(): obj.translate.set_lock_and_hide(False)
          
    def rHide_BTN_pressed(self):
        for obj in pm.selected(): obj.rotate.set_lock_and_hide(True)
                  
    def rShow_BTN_pressed(self):
        for obj in pm.selected(): obj.rotate.set_lock_and_hide(False)
          
    def sHide_BTN_pressed(self):
        for obj in pm.selected(): obj.scale.set_lock_and_hide(True)          
        
    def sShow_BTN_pressed(self):
        for obj in pm.selected(): obj.scale.set_lock_and_hide(False)
          
    def vHide_BTN_pressed(self):
        for obj in pm.selected(): obj.visibility.set_lock_and_hide(True)
                  
    def vShow_BTN_pressed(self):
        for obj in pm.selected(): obj.visibility.set_lock_and_hide(False)  
        
    def create_BTN_pressed(self):
        ctrl_suffix = self.widgets['suffix_TFG'].getText()
        
        create_offsetNode = self.widgets['offsetNode_CB'].getValue()
        offsetNode_suffix = self.widgets['offsetNode_TF'].getText()
        
        create_joint = self.widgets['joint_CB'].getValue()
        joint_group = self.widgets['jointGroup_RBG'].getSelect()
        
        create_shape = self.widgets['shape_CB'].getValue()
        shape_type = self.widgets['shape_TSL'].getSelectItem()[0]
        
        shape_axis = self.widgets['shapeAxis_OM'].getValue()
        
        hierarchy = self.widgets['hierarchry_RB'].getSelect()
        
        tConst = self.widgets['tConst_CB'].getValue()
        rConst = self.widgets['rConst_CB'].getValue()
        pConst = self.widgets['pConst_CB'].getValue()
        sConst = self.widgets['sConst_CB'].getValue()
        
        joints = []
        if create_joint:
            if joint_group == 1: #each
                for obj in pm.selected():
                    clr = pm.cluster(obj)[1]
                    pm.select(clear=True)
                    jnt = pm.joint(name = "%s_joint"%obj.name())
                    pm.delete(pm.parentConstraint(clr, jnt, mo=False))
                    pm.delete(clr)
                
                    pm.skinCluster(jnt, obj, tsb=True)
                    
                    joints.append(jnt)
                    
            elif joint_group == 2: #all
                objs = pm.selected()
                clr = pm.cluster(objs)[1]
                pm.select(clear=True)
                jnt = pm.joint(name = "%s_joint"%objs[0].name())
                pm.delete(pm.parentConstraint(clr, jnt, mo=False))
                pm.delete(clr)
            
                pm.skinCluster(jnt, objs, tsb=True)
                
                joints.append(jnt)
            
        ctrls = []
        objects = joints or pm.selected()
        for i, obj in enumerate(objects):
            
            ctrlName = "%s_%s" %(obj.name(), ctrl_suffix)
            ctrl = add_ctrl(obj, name=ctrlName, point=tConst, orient=rConst, scale=sConst, parent=pConst)
            ctrls.append(ctrl)
            
            if hierarchy == 2 and i != 0: #selectionOrder
                pm.parent(ctrl, ctrls[ i-1 ])
            
            if create_offsetNode:
                add_parent_group(ctrl, suffix=offsetNode_suffix)
                
            if create_shape:
                add_shape(ctrl, shape=shape_type, axis=shape_axis)
                
    def createSubCtrl_BTN_pressed(self):
        ctrls = pm.selected()
        for ctrl in ctrls:
            add_sub_ctrl(ctrl)

    def createPivot_BTN_pressed(self):
        ctrls = pm.selected()
        for ctrl in ctrls:
            isParent = True if pm.selected()[0].getChildren(type='transform') else False
            add_pivot_ctrl(ctrl, orderChildren=isParent)