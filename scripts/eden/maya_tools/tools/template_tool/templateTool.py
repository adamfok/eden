from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtUiTools
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class TemplateTool(QtWidgets.QDialog):
    dlg_instance = None  # maintain a single instance of the dialog in Production

    default_template_path = "R:/Users/afok/shared/template_tool/template_scene.mb"

    @classmethod
    def display(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TemplateTool()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, ui_path=None, parent=maya_main_window()):
        super(TemplateTool, self).__init__(parent)

        # Set Title
        self.setWindowTitle("Template Tool")

        # Remove ? button
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.ui = self.init_ui(ui_path)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def init_ui(self, ui_path=None):
        if not ui_path:
            ui_path = "{0}/templateTool.ui".format(os.path.dirname(__file__))

        print ui_path

        f = QtCore.QFile(ui_path)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        ui = loader.load(f, parentWidget=self)

        f.close()
        return ui

    def create_widgets(self):
        self.ui.pathLineEdit.setText(self.default_template_path)
        pass

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.ui)

    def create_connections(self):
        self.ui.importBtn.clicked.connect(lambda: self.import_template(self.ui.pathLineEdit.text()))

        self.ui.deleteRshoulderBtn.clicked.connect(lambda: self.delete_node("shoulder_R0_root"))
        self.ui.deleteRlegBtn.clicked.connect(lambda: self.delete_node("leg_R0_root"))
        self.ui.deleteMouthBtn.clicked.connect(lambda: self.delete_node("mouth_C0_root"))
        self.ui.deleteEyesBtn.clicked.connect(self.delete_eyes)

        self.ui.blendShapeBtn.clicked.connect(self.blendShape_body_mesh)
        self.ui.mgearToTemplateBtn.clicked.connect(self.use_mgear_positions)

        self.ui.templateToMgearBtn.clicked.connect(self.use_template_position)

        self.ui.selectLshoulderBtn.clicked.connect(lambda: self.select_node("shoulder_L0_root"))
        self.ui.selectLlegBtn.clicked.connect(lambda: self.select_node("leg_L0_root"))

        self.ui.cleanUpBtn.clicked.connect(self.clean_up)

        pass

    def import_template(self, filepath):
        cmds.file(filepath, i=True, mergeNamespacesOnClash=False)
        return

    def delete_node(self, node):
        if cmds.objExists(node):
            cmds.delete(node)

    def delete_eyes(self):
        for node in ["eyeslook_C0_root", "eye_R0_root", "eye_L0_root"]:
            self.delete_node(node)

    def use_mgear_positions(self):
        constraints = list()
        for node in cmds.sets("template_locators", q=True):
            mgear = cmds.getAttr("{}.mgearGuide".format(node))
            template = cmds.getAttr("{}.templateGuide".format(node))

            if cmds.getAttr("{}.t".format(node), lock=True):
                continue

            skips = list()
            for axis in "xyz":
                isLocked = cmds.getAttr("{}.t{}".format(template, axis), lock=True)
                if isLocked:
                    skips.append(axis)

            const = cmds.pointConstraint(mgear, template, mo=False, skip=skips)[0]
            constraints.append(const)
        cmds.delete(constraints)

    def blendShape_body_mesh(self):
        selected = cmds.ls(sl=True)
        if selected:
            mesh = selected[0]

        cmds.blendShape(mesh, "input_mesh", w=[0, 1])

    def use_template_position(self):
        constraints = list()
        for node in cmds.sets("template_locators", q=True):
            mgear = cmds.getAttr("{}.mgearGuide".format(node))
            template = cmds.getAttr("{}.templateGuide".format(node))

            const = cmds.pointConstraint(template, mgear, mo=False)[0]
            constraints.append(const)
        cmds.delete(constraints)

    def select_node(self, node):
        if cmds.objExists(node):
            cmds.select(node)

    def clean_up(self):
        nodes = ["template_rig_group",
                 "jointDisplay",
                 "mesh",
                 "primary_guides",
                 "secondary_guides",
                 "tertiary_guides"]

        for node in nodes:
            if cmds.objExists(node):
                cmds.delete(node)


if __name__ == "__main__":

    try:
        open_import_dialog.close()  # pylint: disable=E0601
        open_import_dialog.deleteLater()
    except:
        pass

    open_import_dialog = OpenImportDialog()
    open_import_dialog.show()
