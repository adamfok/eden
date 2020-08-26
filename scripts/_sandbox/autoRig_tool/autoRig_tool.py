"""
Author : Adam Chun Wai Fok
Date : Feb 2020
Description : auto rig tool
"""

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import os
from shutil import copy

from pixo_rigging.lib.classes import UI as class_UI

from pixo_rigging.tools.Rigging.autoRig_tool.utils import \
    weightIO, fileIO, guideIO, utils_autoRig, controllerIO, utils_bind, utils_deltaMush, finalize

reload(controllerIO)


def main(*args):
    print "\nLoading ... AutoRig Tool UI"
    character = CharacterSetup()
    ui = AutoRigTool_UI(character)
    ui.show()
    if character.has_setup_dir():
        ui.refresh_UI()


class CharacterSetup(object):

    def __init__(self):
        # self.v_autoRig = "V:\Rigging\_autoRig"
        # self.asset_path = os.environ.get("PXO_ASSET_ROOT", "") or ""
        # self.project_abbr = os.environ.get("PXO_PROJECT_ABBR", "") or ""
        # self.asset_name = os.environ.get("PXO_ASSET", "") or ""

        self.v_autoRig = "D:/WORKS/autoRig"
        self.asset_path = "D:/WORKS/autoRig/chr_test"
        self.project_abbr = "project_test"
        self.asset_name = "chr_test"

        self.template_path = os.path.abspath(os.path.join(self.v_autoRig, self.project_abbr))
        self._template_path = os.path.abspath(os.path.join(self.v_autoRig, "_template"))

        self.rig_path = os.path.abspath(os.path.join(self.asset_path, "rig"))
        self.setup_path = os.path.abspath(os.path.join(self.asset_path, "rig", "_setup"))

        self.mdl_path = os.path.abspath(os.path.join(self.asset_path, "mdl"))
        self.mdl_publish_path = os.path.abspath(os.path.join(self.mdl_path, "_publish"))

        self.guide_path = os.path.abspath(os.path.join(self.setup_path, "guides"))
        self.control_path = os.path.abspath(os.path.join(self.setup_path, "controls"))
        self.bindProxy_path = os.path.abspath(os.path.join(self.setup_path, "bind_proxys"))
        self.baseRig_path = os.path.abspath(os.path.join(self.setup_path, "base_rigs"))
        self.skin_weights_path = os.path.abspath(os.path.join(self.setup_path, "skin_weights"))

        assert os.path.exists(self.rig_path), "Missing Rig Directory"
        assert os.path.exists(self.mdl_publish_path), "Missing Mdl Publish Directory"

    def has_setup_dir(self):
        return os.path.exists(self.setup_path)

    def initialize_setup_directory(self):
        for directory in [self.setup_path, self.guide_path, self.control_path, self.bindProxy_path, self.baseRig_path,
                          self.skin_weights_path]:
            if not os.path.exists(directory):
                print "Created Directory %s" % directory
                os.makedirs(directory)

        # check guide
        template_path = self.template_path if os.path.exists(self.template_path) else self._template_path

        guide_template_file_path = os.path.join(self.guide_path, "guides_template.mb")
        guides_v000_file_path = os.path.join(self.guide_path, "guides_v000.json")
        controls_v000_file_path = os.path.join(self.control_path, "controls_v000.json")

        for file_path in [guide_template_file_path, guides_v000_file_path, controls_v000_file_path]:
            if not os.path.exists(file_path):
                file_dir = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                template_file_path = os.path.join(template_path, file_name)

                print template_file_path

                copy(template_file_path, file_dir)
                print "Copied file from %s" % template_file_path

        print "Initialized Setup Directory"


class AutoRigTool_UI(class_UI.UI):

    def __init__(self, character_setup):
        super(AutoRigTool_UI, self).__init__()

        # Define Window
        self.window = "autoRig_tool_win"
        self.title = "Auto Rig Tool v3.0"
        self.windowWidth = 400
        self.windowHeight = 600

        self.dock = False
        self.sizeable = False
        self.allowArea = ['left', 'right']

        self.topColumnWidth = self.windowWidth - 15

        self.character_setup = character_setup
        self.asset_path = self.character_setup.asset_path
        self.asset_name = os.path.basename(self.asset_path)

        self.mdl_path = os.path.abspath(os.path.join(self.asset_path, "mdl"))
        self.mdl_publish_path = os.path.abspath(os.path.join(self.mdl_path, "_publish"))

        self.rig_path = os.path.abspath(os.path.join(self.asset_path, "rig"))
        self.setup_path = os.path.abspath(os.path.join(self.asset_path, "rig", "_setup"))

        self.guide_path = os.path.abspath(os.path.join(self.setup_path, "guides"))
        self.control_path = os.path.abspath(os.path.join(self.setup_path, "controls"))
        self.bindProxy_path = os.path.abspath(os.path.join(self.setup_path, "bind_proxys"))
        self.baseRig_path = os.path.abspath(os.path.join(self.setup_path, "base_rigs"))
        self.skin_weights_path = os.path.abspath(os.path.join(self.setup_path, "skin_weights"))

    # Layout
    def initialiseLayout(self):

        # ASSET LAYOUT
        self.widgets["autoRig_asset_column"] = pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])

        h = pm.horizontalLayout(h=40)
        self.widgets['asset_path_textField'] = pm.textField(editable=False, text=self.asset_path)
        pm.button(label='Open', c=self.asset_open_btn_clicked)
        h.redistribute(8.5, 1.5)
        pm.setParent('..')

        h = pm.horizontalLayout()
        pm.button(label='Initialize Setup Directory', c=self.create_directory_btn_clicked)
        h.redistribute()
        pm.setParent('..')

        h = pm.horizontalLayout()
        pm.button(label='Refresh UI', c=self.refresh_btn_clicked)
        pm.button(label='Reference Mdl', c=self.reference_mdl_btn_clicked)
        h.redistribute()
        pm.setParent('..')

        pm.separator(h=10)

        # TAP LAYOUT
        forms = pm.formLayout()
        self.widgets['tapLayout'] = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        pm.formLayout(forms, edit=True, attachForm=((self.widgets['tapLayout'], 'top', 0),
                                                    (self.widgets['tapLayout'], 'left', 0),
                                                    (self.widgets['tapLayout'], 'bottom', 0),
                                                    (self.widgets['tapLayout'], 'right', 0)))

        # BUILD BASE RIG LAYOUT
        cmds.setParent(self.widgets['tapLayout'])

        self.widgets["build_rig_column"] = pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])

        # GUIDE LAYOUT
        cmds.setParent(self.widgets["build_rig_column"])

        pm.separator()
        pm.text(label="Guides")
        pm.separator()

        # GUIDE TEXT SCROLL
        h1 = pm.horizontalLayout()

        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])
        self.widgets['guide_textScroll'] = GuideTextScroll(directory=self.guide_path)

        h3 = pm.horizontalLayout()
        pm.button(label="Import Guides", c=self.import_guide_btn_clicked)
        h3.redistribute()
        pm.setParent("..")

        h2 = pm.horizontalLayout()
        pm.button(label='Load', c=self.load_guide_btn_clicked)
        pm.button(label='Save', c=self.save_guide_btn_clicked)
        h2.redistribute(1, 1)

        # GUIDE BUTTONS COLUMN 1
        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 1])

        pm.button(label='Mirror', c=self.mirror_guide_btn_clicked)
        pm.button(label='Pin Children', c=self.pin_children_guide_btn_clicked)
        pm.button(label='Pre-Guides', c=self.create_pre_guides_btn_clicked)
        pm.button(label='Joints Displays', c=self.create_joint_display)
        pm.button(label='Up Planes', c=self.create_up_display_btn_clicked)

        pm.setParent(h1)

        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 1])
        # pm.button(label='UnMirror', c=self.unmirror_guide_btn_clicked)
        # pm.button(label='UnPin', c=self.delete_pin_btn_clicked)
        # pm.button(label='Delete Pre', c=self.delete_pre_guides_btn_clicked)
        # pm.button(label='Delete Joints', c=self.delete_joint_display)
        # pm.button(label='Delete Plane', c=self.delete_up_display_btn_clicked)

        pm.button(label='X', c=self.unmirror_guide_btn_clicked)
        pm.button(label='X', c=self.delete_pin_btn_clicked)
        pm.button(label='X', c=self.delete_pre_guides_btn_clicked)
        pm.button(label='X', c=self.delete_joint_display)
        pm.button(label='X', c=self.delete_up_display_btn_clicked)

        h1.redistribute(2, 1.5, 0.5)

        # CONTROL LAYOUT

        cmds.setParent(self.widgets["build_rig_column"])

        pm.separator()
        pm.text(label="Controllers")
        pm.separator()

        # CONTROL TEXT SCROLL
        h1 = pm.horizontalLayout()

        pm.setParent(h1)
        c1 = pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])

        pm.setParent(c1)
        self.widgets['control_textScroll'] = ControlTextScroll(self.control_path)

        h2 = pm.horizontalLayout()
        pm.button(label='Load', c=self.load_control_btn_clicked)
        pm.button(label='Save', c=self.save_control_btn_clicked)

        h2.redistribute(1, 1)

        # CONTROL BUTTONS COLUMN 1
        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 1])

        pm.button(label='Replace Shape', c=self.replace_shape_btn_clicked)
        pm.button(label='Reset Sub Shape', c=self.reset_sub_btn_clicked)
        pm.button(label='Default Color', c=self.default_colors_btn_clicked)
        pm.button(label='Mirror Shapes (L > R)', c=self.mirror_control_btn_clicked)
        pm.button(label='Toggle Sub Ctrl Visibility', c=self.toggle_sub_ctrl_btn_clicked)
        pm.button(label='Reposition Ctrl', c=self.reset_ctrl_position_btn_clicked)

        h1.redistribute(1, 1)

        # BUILD BUTTON
        cmds.setParent(self.widgets["build_rig_column"])
        pm.separator()
        pm.text(label="Build Rig")
        pm.separator()

        h1 = pm.horizontalLayout(h=50)
        pm.button(label="Build Base Rig", command=self.build_baseRig_btn_clicked)
        pm.button(label="Save Base Rig", command=self.save_baseRig_btn_clicked)
        h1.redistribute()

        # BIND RIG LAYOUT
        cmds.setParent(self.widgets['tapLayout'])

        self.widgets["bind_rig_column"] = pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])

        # BASE RIG LAYOUT
        cmds.setParent(self.widgets["bind_rig_column"])

        pm.separator()
        pm.text(label="Base Rig")
        pm.separator()

        cmds.setParent(self.widgets["bind_rig_column"])
        h1 = pm.horizontalLayout()
        pm.button(label='Import Base Rig', command=self.import_baseRig_btn_clicked)
        pm.button(label='Select Bind Joints', command=self.select_bind_joints_btn_clicked)
        h1.redistribute(1, 1)

        cmds.setParent(self.widgets["bind_rig_column"])
        h1 = pm.horizontalLayout()

        pm.button(label='Geo Volex Bind + Delta Mush + Remove Unused Influence', command=self.initial_bind_btn_clicked)
        h1.redistribute(1)

        cmds.setParent(self.widgets["bind_rig_column"])
        h1 = pm.horizontalLayout()
        pm.button(label='Convert Delta Mush', c=self.convert_deltaMush_btn_clicked)
        pm.button(label='Bind Like', c=self.bind_like_btn_clicked)
        h1.redistribute(1, 1)

        # WEIGHT LAYOUT
        cmds.setParent(self.widgets["bind_rig_column"])

        pm.separator()
        pm.text(label="Skin Weights")
        pm.separator()

        # WEIGHT TEXT SCROLL
        h1 = pm.horizontalLayout()

        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])
        self.widgets['weight_textScroll'] = SkinWeightsTextScroll(directory=self.skin_weights_path)

        h2 = pm.horizontalLayout()
        pm.button(label='Apply All', c=self.load_weight_btn_clicked)
        pm.button(label='Save All', c=self.save_weight_btn_clicked)
        h2.redistribute(1, 1)

        # GUIDE BUTTONS COLUMN 1
        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 1])
        pm.button(label="Bind Selected", c=self.bind_selected_geo_btn_clicked)
        pm.button(label="Apply Selected", c=self.load_selected_geo_btn_clicked)
        pm.button(label='Save Selected', c=self.save_selected_geo_btn_clicked)

        h1.redistribute(1, 1)

        # BIND TOOLS
        cmds.setParent(self.widgets["bind_rig_column"])

        pm.separator()
        pm.text(label="Weights Tools")
        pm.separator()

        cmds.setParent(self.widgets["bind_rig_column"])
        h1 = pm.horizontalLayout()

        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])
        pm.button(label='Rebind Geo', c=self.rebind_btn_clicked)
        pm.button(label='Vertex Weight to Shell', c=self.vtx_weight_to_shell_btn_clicked)

        # ----------------------------------------------------------- ____EDIT BUTTONS
        pm.setParent(h1)
        pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])
        pm.button(label='Select Influences', command=self.select_influennces_btn_clicked)
        pm.button(label='Remove Unused Influences', command=self.remove_unused_influences_btn_clicked)
        # pm.button(label='Remove Unused Influences')

        h1.redistribute()

        # -------------------------------------------------- BUILD RIG LAYOUT END
        # -----------------------------------------------------------------------

        cmds.setParent(self.widgets['tapLayout'])

        self.widgets["finalize_rig_column"] = pm.columnLayout(adj=True, rowSpacing=2, columnAttach=['both', 5])

        pm.separator()
        pm.text(label="Finalize")
        pm.separator()
        #
        # pm.button(label="Custom Scripts")
        #
        # h1 = pm.horizontalLayout(h=50)
        # pm.button(label="Unlock Auto Rig", c=self.unfinalize_rig_btn_clicked)

        self.cb1 = pm.checkBox(label="Delete all ctrl keys.", en=False)

        self.cb2 = pm.checkBox(label="Reset all ctrl attributes.", en=False)

        self.cb3 = pm.checkBox(label="Reset all sharedAttr.", en=False)

        self.cb4 = pm.checkBox(label="Reset all ctrl channels.", en=False)

        self.cb5 = pm.checkBox(label="Reset all space switches setting.", en=False)

        self.cb6 = pm.checkBox(label="Reset layers", en=False)

        self.cb7 = pm.checkBox(label="Hide Rig Group", en=False)

        self.cb8 = pm.checkBox(label="Hide Sub Controls", en=False)

        self.cb9 = pm.checkBox(label="Add extra_grp to delete_on_publish_set", en=False)

        self.cb10 = pm.checkBox(label="Debug mode setup", en=False)

        self.cb11 = pm.checkBox(label="Reset Geo Display Override", en=False)

        pm.button(label="Finalize Rig", c=self.finalize_rig_btn_clicked, h=30)

        # =======================================================================
        # TABLAYOUT
        # =======================================================================
        pm.tabLayout(self.widgets['tapLayout'], edit=True,
                     tabLabel=((self.widgets["build_rig_column"], 'Build Rig'.center(27)),
                               (self.widgets["bind_rig_column"], 'Bind Rig'.center(27)),
                               (self.widgets["finalize_rig_column"], 'Finalize Rig'.center(27)),
                               ))

    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------- UI FUNCTIONS
    def create_directory_btn_clicked(self, *args):
        self.character_setup.initialize_setup_directory()
        return

    def refresh_btn_clicked(self, *args):
        self.refresh_UI()

    def refresh_UI(self):
        self.widgets["guide_textScroll"].refresh()
        self.widgets["control_textScroll"].refresh()
        self.widgets["weight_textScroll"].refresh()

        self.reset_checkboxes()

    def asset_open_btn_clicked(self, *args):
        try:
            os.startfile(self.setup_path)
        except Exception as e:
            pm.warning(e)
        return

    def reference_mdl_btn_clicked(self, *args):
        file_name = fileIO.get_files_by_type(self.mdl_publish_path, ext="mb")[-1]
        file_path = os.path.join(self.mdl_publish_path, file_name)
        cmds.file(file_path, r=True, namespace="GEO")
        return

    def import_guide_btn_clicked(self, *args):
        self.widgets["guide_textScroll"].import_guides()
        return

    def pin_children_guide_btn_clicked(self, *args):
        sel = pm.selected()
        for node in sel:
            guideIO.pin_children(node)
        pm.select(sel)

    def delete_pin_btn_clicked(self, *args):
        guideIO.delete_pin()

    def create_pre_guides_btn_clicked(self, *args):
        guideIO.create_landmark_guides()

    def delete_pre_guides_btn_clicked(self, *args):
        guideIO.delete_landmark_guides()

    def create_up_display_btn_clicked(self, *args):
        for node in pm.selected():
            guideIO.create_up_display(node)

    def delete_up_display_btn_clicked(self, *args):
        for node in pm.selected():
            guideIO.delete_up_display(node)

    def create_joint_display(self, *args):
        guideIO.create_joint_display()

    def delete_joint_display(self, *args):
        pm.delete(pm.ls("*_jointDisplay"))

    def save_guide_btn_clicked(self, *args):
        self.widgets["guide_textScroll"].save()
        return

    def load_guide_btn_clicked(self, *args):
        self.widgets["guide_textScroll"].load()
        return

    def save_control_btn_clicked(self, *args):
        self.widgets["control_textScroll"].save()
        return

    def load_control_btn_clicked(self, *args):
        self.widgets["control_textScroll"].load()
        return

    def replace_shape_btn_clicked(self, *args):
        src, dst = pm.selected()
        controllerIO.replace_controllers(src.getShape(), dst.getShape())

    def reset_sub_btn_clicked(self, *args):
        controllerIO.reset_all_sub_controllers()

    def reset_ctrl_position_btn_clicked(self, *args):
        for ctrl in cmds.ls(sl=True):
            controllerIO.reset_ctrl_position(ctrl)

    def mirror_control_btn_clicked(self, *args):
        controllerIO.mirror_controllers()
        return

    def default_colors_btn_clicked(self, *args):
        controllerIO.assign_default_colors()

    def toggle_sub_ctrl_btn_clicked(self, *args):
        controllerIO.toggle_all_subCtrl_vis()
        return

    def mirror_guide_btn_clicked(self, *args):
        guideIO.mirror_guides()

    def unmirror_guide_btn_clicked(self, *args):
        guideIO.unMirror_guides()

    def load_weight_btn_clicked(self, *args):
        self.widgets['weight_textScroll'].load()

        return

    def save_weight_btn_clicked(self, *args):
        self.widgets['weight_textScroll'].save()
        return

    def rename_selected_geo_btn_clicked(self, *args):
        for item in cmds.ls(sl=True):
            weightIO.rename_skinCluster(item)

    def load_selected_geo_btn_clicked(self, *args):
        self.widgets['weight_textScroll'].load_selected()
        return

    def save_selected_geo_btn_clicked(self, *args):
        self.widgets['weight_textScroll'].save_selected()
        return

    def bind_selected_geo_btn_clicked(self, *args):
        self.widgets['weight_textScroll'].bind_selected()

    def build_baseRig_btn_clicked(self, *args):
        self.widgets["guide_textScroll"].import_guides()
        self.widgets["guide_textScroll"].load()

        utils_autoRig.build_autoRig(self.asset_name)

        print "LOADING CONTROLS TEMPLATE... "
        self.widgets["control_textScroll"].load()

        for name in ["guides_set_exported", "guide_display", "guides_grp"]:
            if cmds.objExists(name):
                pm.delete(name)

        print "BASE RIG BUILD COMPLETE..."

    def save_baseRig_btn_clicked(self, *args):
        file_path = fileIO.get_increment_file_path(self.baseRig_path, "baseRig", "ma")
        cmds.file(rename=file_path)
        cmds.file(save=True, type='mayaAscii')
        print "Saved Base Rig %s" % file_path
        return

    def import_baseRig_btn_clicked(self, *args):
        baseRig_files = fileIO.get_files_by_type(self.baseRig_path, "ma")
        if not baseRig_files:
            print "No Maya Ascii File in %s" % self.baseRig_path
            return

        file_path = os.path.join(self.baseRig_path, baseRig_files[-1])
        print "Importing Base Rig %s" % file_path
        cmds.file(file_path, i=True)
        return

    def select_bind_joints_btn_clicked(self, *args):
        if not pm.objExists("root_joint"):
            print "root_joint Not Found"
            return

        selection = pm.listRelatives("root_joint", ad=True, type="joint")
        pm.select(selection)
        return

    def select_influennces_btn_clicked(self, *args):
        result = list()
        for mesh in cmds.ls(sl=True):
            skinCluster = mel.eval('findRelatedSkinCluster("%s")' % (mesh))
            result.extend(cmds.skinCluster(skinCluster, query=True, inf=True))
        cmds.select(result)
        return

    def remove_unused_influences_btn_clicked(self, *args):
        mel.eval("removeUnusedInfluences")
        return

    def initial_bind_btn_clicked(self, *args):
        bind_joints = pm.listRelatives("root_joint", ad=True, type="joint")

        for mesh in pm.selected():
            skin = pm.skinCluster(mesh, bind_joints, bindMethod=3, tsb=True)
            pm.geomBind(skin, bindMethod=3, fo=0, mi=1)
            pm.deformer(mesh, type="deltaMush")
            pm.select(mesh)
            mel.eval("removeUnusedInfluences")

        print "Initial Bind Complete"
        return

    def convert_deltaMush_btn_clicked(self, *args):
        for mesh in pm.selected():
            utils_deltaMush.convert_deltaMush_to_weight(mesh)
            print "DeltaMush Convertion Completed"

    def rebind_btn_clicked(self, *args):
        for obj in pm.selected():
            utils_bind.rebind(obj)

    def vtx_weight_to_shell_btn_clicked(self, *args):
        for vtx in pm.selected():
            utils_bind.vertex_weight_to_shell(vtx)

    def bind_like_btn_clicked(self, *args):
        selection = pm.selected()
        src = selection[-1]
        dsts = selection[:-1]
        for dst in dsts:
            utils_bind.bind_like(src, dst)

    def finalize_rig_btn_clicked(self, *args):
        print "\nReset Biped Rig..."

        finalize.delete_all_ctrl_keys()
        print "\t- Delete all ctrl keys."
        pm.checkBox(self.cb1, e=True, value=True)

        finalize.reset_ctrl_attributes()
        print "\t- Reset all ctrl attributes."
        pm.checkBox(self.cb2, e=True, value=True)

        finalize.reset_sharedAttr_settings()
        print "\t- Reset all sharedAttr."
        pm.checkBox(self.cb3, e=True, value=True)

        finalize.lock_and_hide_channels()
        print "\t- Reset all ctrl channels."
        pm.checkBox(self.cb4, e=True, value=True)

        finalize.reset_space_switchs()
        print "\t- Reset all space switches setting."
        pm.checkBox(self.cb5, e=True, value=True)

        finalize.reset_layers()
        print "\t- Reset layers"
        pm.checkBox(self.cb6, e=True, value=True)

        finalize.hide_rig_grp()
        print "\t- Hide Rig Group"
        pm.checkBox(self.cb7, e=True, value=True)

        finalize.hide_sub_ctrls()
        print "\t- Hide Sub Controls"
        pm.checkBox(self.cb8, e=True, value=True)

        finalize.delete_on_publish_set()
        print "\t- Add extra_grp to delete_on_publish_set"
        pm.checkBox(self.cb9, e=True, value=True)

        finalize.setup_debug_mode()
        print "\t- Debug mode setup"
        pm.checkBox(self.cb10, e=True, value=True)

        finalize.reset_display_override()
        print "\t- Reset Geo Display Override"
        pm.checkBox(self.cb11, e=True, value=True)

        return

    def reset_checkboxes(self, *args):
        all_checkBox = [self.cb1, self.cb2, self.cb3, self.cb4, self.cb5, self.cb6,
                        self.cb7, self.cb8, self.cb9, self.cb10, self.cb11]
        for cb in all_checkBox:
            pm.checkBox(cb, e=True, value=False)


class TextScroll(object):

    def __init__(self, directory, prefix, ext):
        self._wh = [60, 100]
        self.text_scroll = pm.textScrollList(w=self._wh[0], h=self._wh[1])
        self.directory = directory
        self.ext = ext
        self.prefix = prefix

    def refresh(self):
        self.text_scroll.removeAll()

        files = fileIO.get_files_by_type(self.directory, self.ext)

        if not files:
            return
        files.reverse()

        for f in files:
            self.text_scroll.append(f)
        self.text_scroll.setSelectIndexedItem(1)
        return

    def get_increment_file_path(self):
        return fileIO.get_increment_file_path(self.directory, self.prefix, self.ext)

    def get_selected(self):
        sel = self.text_scroll.getSelectItem()
        assert sel, "Nothing Selected"

        return os.path.abspath(os.path.join(self.directory, sel[-1]))


class GuideTextScroll(TextScroll):

    def __init__(self, directory):
        self.directory = directory
        self.guide_template = os.path.join(directory, "guides_template.mb")

        self.prefix = "guides"
        self.ext = "json"
        TextScroll.__init__(self, self.directory, self.prefix, self.ext)

    def load(self):
        guideIO.load_positions(self.get_selected())
        return

    def save(self):
        guideIO.save_positions(self.get_increment_file_path())
        self.refresh()
        return

    def import_guides(self):
        guideIO.import_guides(self.guide_template)
        guideIO.create_guide_display()


class ControlTextScroll(TextScroll):
    def __init__(self, directory):
        self.directory = directory
        self.prefix = "controls"
        self.ext = "json"
        TextScroll.__init__(self, self.directory, self.prefix, self.ext)

    def save(self):
        controllerIO.save_controllers(self.get_increment_file_path())
        self.refresh()
        return

    def load(self):
        controllerIO.load_controllers(self.get_selected())
        return


class SkinWeightsTextScroll(object):

    def __init__(self, directory):
        self._wh = [60, 150]
        self.text_scroll = pm.textScrollList(w=self._wh[0], h=self._wh[1])
        self.directory = directory

    def refresh(self):
        self.text_scroll.removeAll()

        folders = fileIO.get_folders_in_directory(self.directory)

        if not folders:
            return

        for f in folders:
            self.text_scroll.append(f)
        self.text_scroll.setSelectIndexedItem(1)

        return

    def get_selected(self):
        sel = self.text_scroll.getSelectItem()
        assert sel, "Nothing Selected"

        return os.path.abspath(os.path.join(self.directory, sel[-1]))

    def load(self):
        for node in weightIO.get_all_mesh():
            weightIO.import_skinCluster(node, self.get_selected())

        return

    def save(self):
        folder_name = self.get_description_dialog()
        folder_path = os.path.join(self.directory, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for node in weightIO.get_all_mesh():
            weightIO.export_skinCluster(node, folder_path)

        self.refresh()
        return

    def load_selected(self):
        for node in cmds.ls(sl=True):
            weightIO.import_skinCluster(node, self.get_selected())
        return

    def save_selected(self):
        for node in cmds.ls(sl=True):
            weightIO.export_skinCluster(node, self.get_selected())
        return

    def bind_selected(self):
        for node in cmds.ls(sl=True):
            print "Binding %s" % node
            weightIO.bind_mesh(node, self.get_selected())
            weightIO.import_skinCluster(node, self.get_selected())

        return

    def get_description_dialog(self):
        result = pm.promptDialog(title='Export Weights',
                                 message='Enter Description:',
                                 button=['OK', 'Cancel'],
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')

        if result == 'OK':
            description = pm.promptDialog(query=True, text=True)

            if description:
                return description.replace(" ", "_")
            else:
                return "skinWeights"
        else:
            return


if __name__ == "__main__":
    main()
