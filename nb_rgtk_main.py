"""
This script provides several rigging tools to help riggers.
- matrix parent constraint
- matrix aim constraint
- create parent spaces
- reset joint orientation
- create a module (transform node hierarchie) to help organize rigging process
- set world transform to offset arent matrix attibut
- 
"""
# PySide modules
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from shiboken2 import wrapInstance
import sys

# Maya api 1.0
import maya.OpenMayaUI as omui

# Import other module script
from nb_rigging_toolkit import nb_rgtk_matrix as nb_mat
from nb_rigging_toolkit import nb_rgtk_utils as nb_utils
from nb_rigging_toolkit import nb_rgtk_parent_space as nb_ps

def maya_main_windows() :
    '''
    Return maya main window widget as python object
    '''
    maya_main_window = omui.MQtUtil.mainWindow()
    
    # return int value if current python version is 3 or upper, otherwise return long
    if sys.version_info.major >= 3 :
        return wrapInstance(int(maya_main_window), QtWidgets.QWidget)
    else :
        return wrapInstance(long(maya_main_window), QtWidgets.QWidget)

class ParentMatrixWdgt (QtWidgets.QDialog):
    '''
    Parent Matrix constraint Dialog. This Dialog contains all options for parent matrix constraint
    '''
    def __init__(self, parent = None) :
        '''
        Initialize parent dialog
        '''
        super (ParentMatrixWdgt, self).__init__(parent)     # Init QtWidgets.QDialog

        self.create_widgets()                               # Build dialog
        self.create_layouts ()
        self.create_connections()
        
        self.setMaximumSize(350, 300)

    def create_widgets (self):
        '''
        Create and setup all widget
        '''
        # label object
        self.p_const_parent_text = QtWidgets.QLabel ("Parent")
        self.p_const_translate_text = QtWidgets.QLabel ("Translate")
        self.p_const_rotate_text = QtWidgets.QLabel ("Rotate")
        self.p_const_scale_text = QtWidgets.QLabel ("Scale")
        self.p_const_x_text = QtWidgets.QLabel ("X")
        self.p_const_y_text = QtWidgets.QLabel ("Y")
        self.p_const_z_text = QtWidgets.QLabel ("Z")

        # checkboxs objects
        #       translate
        self.p_const_tx_cbox = QtWidgets.QCheckBox()
        self.p_const_ty_cbox = QtWidgets.QCheckBox()
        self.p_const_tz_cbox = QtWidgets.QCheckBox()
        self.p_const_tx_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_ty_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_tz_cbox.setCheckState(QtCore.Qt.Checked)

        #       rotate
        self.p_const_rx_cbox = QtWidgets.QCheckBox()
        self.p_const_ry_cbox = QtWidgets.QCheckBox()
        self.p_const_rz_cbox = QtWidgets.QCheckBox()
        self.p_const_rx_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_ry_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_rz_cbox.setCheckState(QtCore.Qt.Checked)
        
        #       scale
        self.p_const_sx_cbox = QtWidgets.QCheckBox()
        self.p_const_sy_cbox = QtWidgets.QCheckBox()
        self.p_const_sz_cbox = QtWidgets.QCheckBox()
        self.p_const_sx_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_sy_cbox.setCheckState(QtCore.Qt.Checked)
        self.p_const_sz_cbox.setCheckState(QtCore.Qt.Checked)
        
        #       cheboxs buttons
        self.p_const_all_t_butt = QtWidgets.QPushButton("All")
        self.p_const_all_r_butt = QtWidgets.QPushButton("All")
        self.p_const_all_s_butt = QtWidgets.QPushButton("All")

        self.p_const_none_t_butt = QtWidgets.QPushButton("None")
        self.p_const_none_r_butt = QtWidgets.QPushButton("None")
        self.p_const_none_s_butt = QtWidgets.QPushButton("None")
        
        # offset and offset parent matrix checkboxs
        self.opm_text = QtWidgets.QLabel("OffsetParentMatrix")
        self.offset_text = QtWidgets.QLabel("Maintaint Offset")
        
        self.opm_cbox = QtWidgets.QCheckBox()
        self.offset_cbox = QtWidgets.QCheckBox()
        self.opm_cbox.setCheckState(QtCore.Qt.Checked)
        self.offset_cbox.setCheckState(QtCore.Qt.Checked)
        
        # apply buttons
        self.parent_button = QtWidgets.QPushButton("Parent Constraint")
        self.aim_button = QtWidgets.QPushButton("Aim Constraint")
        self.parent_button.setIcon(QtGui.QIcon(':parentConstraint.png'))
        
        
    def create_layouts (self):
        '''
        Order all created widget in layouts
        '''        
        #main grid
        parent_layout = QtWidgets.QGridLayout()
        parent_layout.addWidget(self.p_const_parent_text, 0, 0, QtCore.Qt.AlignRight)
        parent_layout.addWidget(self.p_const_translate_text, 1, 0, QtCore.Qt.AlignRight)
        parent_layout.addWidget(self.p_const_rotate_text, 2, 0, QtCore.Qt.AlignRight)
        parent_layout.addWidget(self.p_const_scale_text, 3, 0, QtCore.Qt.AlignRight)
        
        #text
        parent_layout.addWidget(self.p_const_x_text, 0, 1)
        parent_layout.addWidget(self.p_const_y_text, 0, 2)
        parent_layout.addWidget(self.p_const_z_text, 0, 3)
        
        #translate
        parent_layout.addWidget(self.p_const_tx_cbox, 1, 1)
        parent_layout.addWidget(self.p_const_ty_cbox, 1, 2)
        parent_layout.addWidget(self.p_const_tz_cbox, 1, 3)
        parent_layout.addWidget(self.p_const_all_t_butt, 1, 4)
        parent_layout.addWidget(self.p_const_none_t_butt, 1, 5)
        
        #rotate
        parent_layout.addWidget(self.p_const_rx_cbox, 2, 1)
        parent_layout.addWidget(self.p_const_ry_cbox, 2, 2)
        parent_layout.addWidget(self.p_const_rz_cbox, 2, 3)
        parent_layout.addWidget(self.p_const_all_r_butt, 2, 4)
        parent_layout.addWidget(self.p_const_none_r_butt, 2, 5)
        
        #scale
        parent_layout.addWidget(self.p_const_sx_cbox, 3, 1)
        parent_layout.addWidget(self.p_const_sy_cbox, 3, 2)
        parent_layout.addWidget(self.p_const_sz_cbox, 3, 3)
        parent_layout.addWidget(self.p_const_all_s_butt, 3, 4)
        parent_layout.addWidget(self.p_const_none_s_butt, 3, 5)
        
        #set row minimum height
        parent_layout.setRowMinimumHeight(0,10) 
        parent_layout.setRowMinimumHeight(1,20)
        parent_layout.setRowMinimumHeight(2,20)
        parent_layout.setRowMinimumHeight(3,20)
        parent_layout.setHorizontalSpacing (15)
        
        #maintain offset and opm check box
        offset_opm_layout = QtWidgets.QHBoxLayout()
        offset_opm_layout.addWidget (self.offset_text)
        offset_opm_layout.addWidget (self.offset_cbox)
        offset_opm_layout.addWidget (self.opm_text)
        offset_opm_layout.addWidget (self.opm_cbox)
        
        # buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.parent_button)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(parent_layout)
        main_layout.addLayout(offset_opm_layout)
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        '''
        Connect widgets signals with class functions
        '''
        # parent button
        self.parent_button.clicked.connect(self.do_matrix_parent_constraint)

        # all axis button
        self.p_const_all_t_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_tx_cbox, self.p_const_ty_cbox, self.p_const_tz_cbox], QtCore.Qt.Checked))
        self.p_const_all_r_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_rx_cbox, self.p_const_ry_cbox, self.p_const_rz_cbox], QtCore.Qt.Checked))
        self.p_const_all_s_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_sx_cbox, self.p_const_sy_cbox, self.p_const_sz_cbox], QtCore.Qt.Checked))

        # None axis button
        self.p_const_none_t_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_tx_cbox, self.p_const_ty_cbox, self.p_const_tz_cbox], QtCore.Qt.Unchecked))
        self.p_const_none_r_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_rx_cbox, self.p_const_ry_cbox, self.p_const_rz_cbox], QtCore.Qt.Unchecked))
        self.p_const_none_s_butt.clicked.connect(lambda  _ : self.check_all_axis ([self.p_const_sx_cbox, self.p_const_sy_cbox, self.p_const_sz_cbox], QtCore.Qt.Unchecked))
        
    def do_matrix_parent_constraint (self):
        '''
        This function store all checkbox widget values and call nb_mat.MatrixConstraint.matrix_parent_constraint functions
        '''
        
        # get offset and offset parent matrix checkboxs state
        offset = True if self.offset_cbox.isChecked() else False
        in_opm_connect = True if self.opm_cbox.isChecked() else False
        
        trigger_matrix = 'worldMatrix[0]'
        
        # get transform checkboxs state
        is_tx = True if self.p_const_tx_cbox.isChecked() else False
        is_ty = True if self.p_const_ty_cbox.isChecked() else False
        is_tz = True if self.p_const_tz_cbox.isChecked() else False
        
        is_rx = True if self.p_const_rx_cbox.isChecked() else False
        is_ry = True if self.p_const_ry_cbox.isChecked() else False
        is_rz = True if self.p_const_rz_cbox.isChecked() else False
        
        is_sx = True if self.p_const_sx_cbox.isChecked() else False
        is_sy = True if self.p_const_sy_cbox.isChecked() else False
        is_sz = True if self.p_const_sz_cbox.isChecked() else False
        
        # list of keywords to connect object later on and bool attribut to connect to matrix or offset parent matrix
        out_connect =   [[[['TranslateX', 'translateX'], is_tx], [['TranslateY', 'translateY'], is_ty], [['TranslateZ', 'translateZ'], is_tz]], 
                        [[['RotateX', 'rotateX'], is_rx], [['RotateY', 'rotateY'], is_ry], [['RotateZ', 'rotateZ'], is_rz]],
                        [[['ScaleX', 'scaleX'], is_sx], [['ScaleY', 'scaleY'], is_sy], [['ScaleZ', 'scaleZ'], is_sz]],
                        in_opm_connect]
        
        # do paarent constraint
        nb_mat.MatrixConstraint.matrix_parent_constraint (nb_mat.MatrixConstraint, offset, trigger_matrix, out_connect)
        
    def check_all_axis (self, attributs, checked_value) : 
        '''
        Set all checkbox in attribut variable with checked_value vaiable
        attributs -> list of 3 checkboxs for x, y and z axis (list : [QtWidget.QCheckBox, QtWidget.QCheckBox, QtWidget.QCheckBox])
        checked_value -> check state to turn checkbox (QtCore.Qt.Checked or QtCore.Qt.Unchecked)
        '''
        for check_box in attributs :
            check_box.setCheckState(checked_value)

class AimMatrixWdgt (QtWidgets.QDialog):
    '''
    Dialog with all widget to perform a matrix aim constraint
    '''
    def __init__(self, parent = None) :
        '''
        Initialize Dialog
        '''
        super (AimMatrixWdgt, self).__init__(parent)

        self.create_widgets()
        self.create_layouts ()
        self.create_connections()
        
        self.setMaximumSize(350, 300)
    
    def create_widgets (self):
        '''
        Create all dialog widgets and setup them
        '''
        #text
        self.aim_const_text = QtWidgets.QLabel ("Aim")
        self.aim_const_primary_text = QtWidgets.QLabel ("Primary Axis")
        self.aim_const_secondary_text = QtWidgets.QLabel ("Secondary Axis")
        self.aim_const_world_up_axis_text = QtWidgets.QLabel ("World Up Axis")
        self.aim_const_world_up_obj_text = QtWidgets.QLabel ("World Up Object")
        self.aim_const_x_text = QtWidgets.QLabel ("X")
        self.aim_const_y_text = QtWidgets.QLabel ("Y")
        self.aim_const_z_text = QtWidgets.QLabel ("Z")

        # primary axis float field
        self.aim_primary_x_field = QtWidgets.QDoubleSpinBox()
        self.aim_primary_x_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_primary_x_field.setDecimals(3)
        self.aim_primary_x_field.setRange (0,1)
        self.aim_primary_x_field.setValue(1)

        self.aim_primary_y_field = QtWidgets.QDoubleSpinBox()
        self.aim_primary_y_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_primary_y_field.setDecimals(3)
        self.aim_primary_y_field.setRange (0,1)

        self.aim_primary_z_field = QtWidgets.QDoubleSpinBox()
        self.aim_primary_z_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_primary_z_field.setDecimals(3)
        self.aim_primary_z_field.setRange (0,1)

        self.aim_secondary_x_field = QtWidgets.QDoubleSpinBox()
        self.aim_secondary_x_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_secondary_x_field.setDecimals(3)
        self.aim_secondary_x_field.setRange (0,1)

        self.aim_secondary_y_field = QtWidgets.QDoubleSpinBox()
        self.aim_secondary_y_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_secondary_y_field.setDecimals(3)
        self.aim_secondary_y_field.setRange (0,1)
        self.aim_secondary_y_field.setValue(1)

        self.aim_secondary_z_field = QtWidgets.QDoubleSpinBox()
        self.aim_secondary_z_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_secondary_z_field.setDecimals(3)
        self.aim_secondary_z_field.setRange (0,1)

        self.aim_world_up_x_field = QtWidgets.QDoubleSpinBox()
        self.aim_world_up_x_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_world_up_x_field.setDecimals(3)
        self.aim_world_up_x_field.setRange (0,1)

        self.aim_world_up_y_field = QtWidgets.QDoubleSpinBox()
        self.aim_world_up_y_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_world_up_y_field.setDecimals(3)
        self.aim_world_up_y_field.setRange (0,1)
        self.aim_world_up_y_field.setValue(1)

        self.aim_world_up_z_field = QtWidgets.QDoubleSpinBox()
        self.aim_world_up_z_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_world_up_z_field.setDecimals(3)
        self.aim_world_up_z_field.setRange (0,1)

        self.aim_world_up_object = QtWidgets.QLineEdit()
        self.aim_world_up_object.setDragEnabled(True)
        self.aim_world_up_object.setPlaceholderText("World up object (if empty, target)")

        self.in_opm_cb = QtWidgets.QCheckBox("OPM")

        self.aim_button = QtWidgets.QPushButton("Aim Constraint")
        self.aim_button.setIcon(QtGui.QIcon(':aimConstraint.png'))
        
    def create_layouts (self):
        '''
        Order all created widget in layouts
        '''   
        #main grid
        aim_layout = QtWidgets.QGridLayout()
        aim_layout.addWidget(self.aim_const_text, 0, 0, QtCore.Qt.AlignRight)
        aim_layout.addWidget(self.aim_const_primary_text, 1, 0, QtCore.Qt.AlignRight)
        aim_layout.addWidget(self.aim_const_secondary_text, 2, 0, QtCore.Qt.AlignRight)
        aim_layout.addWidget(self.aim_const_world_up_axis_text, 3, 0, QtCore.Qt.AlignRight)
        aim_layout.addWidget(self.aim_const_world_up_obj_text, 4, 0, QtCore.Qt.AlignRight)

        aim_layout.addWidget(self.aim_const_x_text, 0, 1, QtCore.Qt.AlignHCenter)
        aim_layout.addWidget(self.aim_const_y_text, 0, 2, QtCore.Qt.AlignHCenter)
        aim_layout.addWidget(self.aim_const_z_text, 0, 3, QtCore.Qt.AlignHCenter)

        aim_layout.addWidget(self.aim_primary_x_field, 1, 1)
        aim_layout.addWidget(self.aim_primary_y_field, 1, 2)
        aim_layout.addWidget(self.aim_primary_z_field, 1, 3)

        aim_layout.addWidget(self.aim_secondary_x_field, 2, 1)
        aim_layout.addWidget(self.aim_secondary_y_field, 2, 2)
        aim_layout.addWidget(self.aim_secondary_z_field, 2, 3)

        aim_layout.addWidget(self.aim_world_up_x_field, 3, 1)
        aim_layout.addWidget(self.aim_world_up_y_field, 3, 2)
        aim_layout.addWidget(self.aim_world_up_z_field, 3, 3)

        aim_layout.addWidget(self.aim_world_up_object, 4, 1, 1, 2)
        aim_layout.addWidget(self.in_opm_cb, 4, 3)

        aim_layout.addWidget(self.aim_button, 5, 0, 1, 4)

        main_aim_layout = QtWidgets.QVBoxLayout(self)
        main_aim_layout.addLayout(aim_layout)
        main_aim_layout.addStretch()

    def create_connections(self):
        '''
        Connect widgets signals with class functions
        '''
        # aim button
        self.aim_button.clicked.connect(self.do_matrix_aim_constraint) 
        
    def do_matrix_aim_constraint(self) :
        '''
        This function stock all aim matrix widget in variable and call nb_mat.MatrixConstraint.matrix_aim_constraint 
        '''
        in_opm = self.in_opm_cb.isChecked()
        world_up_vector = (self.aim_world_up_x_field.value(),
                           self.aim_world_up_y_field.value(),
                           self.aim_world_up_z_field.value())
        
        primary_axis = (self.aim_primary_x_field.value(),
                           self.aim_primary_y_field.value(),
                           self.aim_primary_z_field.value())
        
        secondary_axis = (self.aim_secondary_x_field.value(),
                           self.aim_secondary_y_field.value(),
                           self.aim_secondary_z_field.value())
        
        world_up_object = self.aim_world_up_object.text()

        nb_mat.MatrixConstraint.matrix_aim_constraint(nb_mat.MatrixConstraint, in_opm, world_up_vector, world_up_object, primary_axis, secondary_axis)

class RiggingProcessWindow (QtWidgets.QDialog) :
    '''
    Rigging Process Dialog
    '''

    def __init__(self, parent=maya_main_windows()):
        '''
        Initialize Dialog
        '''
        super (RiggingProcessWindow, self).__init__(parent)

        self.create_widgets()
        self.create_layouts ()
        self.create_connections()

    def create_widgets(self) :
        '''
        Create all dialog widgets and setup them
        '''
        self.ps_text = QtWidgets.QLabel("Parent Space")
        self.ps_attribut_name_lineEdit = QtWidgets.QLineEdit()
        self.ps_attribut_name_lineEdit.setFont("Parent Space Attribut Name...")
        self.ps_parent_transform_cb = QtWidgets.QCheckBox("Parent Translate")
        self.ps_button = QtWidgets.QPushButton("Create Parent Spaces")

        self.attr_connect_text = QtWidgets.QLabel("Fast Connect Attribut")
        self.attr_connect_lineEdit = QtWidgets.QLineEdit()
        self.attr_connect_button = QtWidgets.QPushButton("Connect")

    def create_layouts(self) :
        '''
        Order all created widget in layouts
        '''   
        parent_space_layout = QtWidgets.QGridLayout()
        parent_space_layout.addWidget(self.ps_text, 0, 0)
        parent_space_layout.addWidget(self.ps_attribut_name_lineEdit, 0, 1, 1, 2)
        parent_space_layout.addWidget(self.ps_parent_transform_cb, 0, 3)
        parent_space_layout.addWidget(self.ps_button, 1, 0, 1, 4)

        attr_connect_layout = QtWidgets.QHBoxLayout()
        attr_connect_layout.addWidget(self.attr_connect_text)
        attr_connect_layout.addWidget(self.attr_connect_lineEdit)
        attr_connect_layout.addWidget(self.attr_connect_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(parent_space_layout)
        main_layout.addLayout(attr_connect_layout)

    def create_connections(self) :
        '''
        Connect widgets signals with class functions
        '''
        self.ps_button.clicked.connect(self.do_parent_spaces)
        self.attr_connect_button.clicked.connect(self.do_connect_attr)

    def do_parent_spaces (self):
        '''
        This function get self.ps_parent_transform_cb and self.ps_attribut_name_lineEdit values and call nb_ps.do_parent_space
        '''
        is_fk = self.ps_parent_transform_cb.isChecked()
        attribut_name = self.ps_attribut_name_lineEdit.text()

        nb_ps.do_parent_space (is_fk, attribut_name)

    def do_connect_attr (self) :
        '''
        This function get self.attr_connect_lineEdit text and call nb_utils.fast_connect_attr
        '''
        attribut = self.attr_connect_lineEdit.text()
        print (attribut)

        nb_utils.fast_connect_attr (attribut)

class ToolkitWindow (QtWidgets.QDialog):
    '''
    Main Window function
    '''

    def __init__(self, parent=maya_main_windows()) :
        '''
        Initialize Dialog
        '''
        super (ToolkitWindow, self).__init__(parent)

        self.setWindowTitle("NB Rigging Toolkit")
        self.setFixedSize(400,300)
        self.setWindowFlags(self.windowFlags()^QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_actions ()
        self.create_widgets ()
        self.create_layouts ()
        self.create_connections ()

    def create_actions (self) :
        '''
        Create all dialog actions
        '''
        self.about_action = QtWidgets.QAction("About", self)
        
        self.module_action = QtWidgets.QAction("Create Module", self)
        self.in_opm_action = QtWidgets.QAction("Set Transform in OPM", self)
        self.reset_joint_orient_action = QtWidgets.QAction("Reset Joint Orient", self)

    def create_widgets (self) :
        '''
        Create all dialog widgets and setup them
        '''

        self.menu_bar = QtWidgets.QMenuBar()

        file_menu = self.menu_bar.addMenu("File")

        control_menu = self.menu_bar.addMenu("Control")
        control_menu.addAction(self.module_action)
        control_menu.addAction(self.in_opm_action)

        skeleton_menu = self.menu_bar.addMenu("Skeleton")
        skeleton_menu.addAction(self.reset_joint_orient_action)

        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

        self.parent_matrix_widget = ParentMatrixWdgt()
        self.aim_matrix_widget = AimMatrixWdgt()
        self.rigging_process_widget = RiggingProcessWindow ()

        self.tab_widget = QtWidgets.QTabWidget()    
        self.tab_widget.addTab(self.parent_matrix_widget, "Parent Matrix Constraint")
        self.tab_widget.addTab(self.aim_matrix_widget, "Aim Matrix Constraint")
        self.tab_widget.addTab(self.rigging_process_widget, "Rigging Process")
    
    def create_layouts(self) :
        '''
        Order all created widget in layouts
        '''   
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(self.tab_widget)
        main_layout.addStretch()

    def create_connections(self) :
        '''
        Connect widgets signals with class functions
        '''
        self.about_action.triggered.connect(self.about)
        self.module_action.triggered.connect(self.call_create_module)
        self.in_opm_action.triggered.connect(self.call_set_in_opm)
        self.reset_joint_orient_action.triggered.connect(self.call_reset_joint)

    def call_create_module (self) :
        '''
        This function call an QInputDialog and get his text. Then call nb_utils.create_rigging_module with input text
        '''
        message_box = QtWidgets.QInputDialog.getText(self, "Module's Prefix", "Enter Module's Prefix")
        nb_utils.create_rigging_module(message_box[0])

    def call_set_in_opm (self) :
        '''
        This function only call nb_utils.set_transform_in_opm
        '''
        nb_utils.set_transform_in_opm()

    def about (self) :
        '''
        This function call a QMessage box with some documentation about the script   ### Todo Later ###
        '''
        QtWidgets.QMessageBox.about(self, "About Simple Outliner", "Add About Text Here")

    def call_reset_joint(self) :
        '''
        This function only call nb_utils.reset_joint_orient
        '''
        nb_utils.reset_joint_orient()
