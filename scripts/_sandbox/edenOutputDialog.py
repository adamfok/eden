from PySide2 import QtWidgets, QtCore
from eden.utils.loggerUtils import QtLogger
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def install():
    try:
        window.close()  # pylint: disable=E0601
        window.deleteLater()
    except:
        pass

    window = EdenOutputDialog()
    window.show()


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class EdenOutputDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(EdenOutputDialog, self).__init__(parent)

        self.setWindowTitle("Eden Output Window")
        self.setMinimumSize(400, 300)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.plain_text_edit = QtWidgets.QPlainTextEdit()

        self.warning_btn = QtWidgets.QPushButton("Warning")
        self.warning_btn.clicked.connect(self.print_warning)

        self.error_btn = QtWidgets.QPushButton("Error")
        self.error_btn.clicked.connect(self.print_error)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.warning_btn)
        button_layout.addWidget(self.error_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.plain_text_edit)
        main_layout.addLayout(button_layout)

        QtLogger.signal_handler().emitter.message_logged.connect(self.plain_text_edit.appendPlainText)

    def print_warning(self):
        QtLogger.warning("warning message")

    def print_error(self):
        QtLogger.error("error message")
