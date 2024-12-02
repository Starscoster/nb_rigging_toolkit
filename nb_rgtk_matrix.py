from maya import cmds
from nb_rigging_toolkit import nb_rgtk_utils as nb_utils

class MatrixConstraint () :

    def get_objects (self) :
        '''
        Get maya current selected objects. First object is the target, the other are triggers objects
        Return target_object and trigger_objects
        '''
        # Get maya selection
        maya_sel = cmds.ls(sl=True)

        # Test maya current selection
        if not maya_sel :
            cmds.warning ("No object selected")
            return False
        elif len(maya_sel) < 2 :
            cmds.warning ("Only one object is selected. Need at least two")
            return False

        # If selection is valid, set target and trigger variable
        target_obj = maya_sel[-1]
        trigger_obj = maya_sel[:-1]

        return [trigger_obj, target_obj]

    def get_offset_matrix(self, target_, trigger_) :
        '''
        This function get offset matrix between two objects
        Return an composeMatrix with offsetMatrix value in
        target_ -> target object to get offset
        trigger_ -> target object to base offset
        '''
        # Creates necesary nodes
        offset_node = cmds.createNode ('composeMatrix', name = '{}_{}_parentMConstraint_offset'.format(trigger_, target_))
        temp_offset = cmds.createNode ('composeMatrix', name = trigger_ + '_temp_offset')
        temp_mult = cmds.createNode ('multMatrix', name = trigger_ + '_temp_mult')
        temp_decMat = cmds.createNode ('decomposeMatrix', name = trigger_ + '_temp_decMat')

        # Get target parent
        parent = cmds.listRelatives (target_, p=True, typ = 'transform')

        # Parent target_ to trigger_
        cmds.parent (target_, trigger_)

        # Try to connect target_ to temp_offset. If RuntimeError, then connect trigger_|target_ to temp_offset. This is necessary due to maya
        # name spaces
        temp_target_ = target_
        try :
            cmds.connectAttr ('{}.t'.format (target_), '{}.inputTranslate'.format (temp_offset))
        except RuntimeError :
            cmds.connectAttr ('{}|{}.t'.format (trigger_,target_), '{}.inputTranslate'.format (temp_offset))
            temp_target_ = f'{trigger_}|{target_}'
            
        # Get translate relative to trigger_
        cmds.connectAttr ('{}.r'.format (temp_target_), '{}.inputRotate'.format (temp_offset))
        cmds.connectAttr ('{}.s'.format (temp_target_), '{}.inputScale'.format (temp_offset))

        cmds.disconnectAttr ('{}.t'.format (temp_target_), '{}.inputTranslate'.format (temp_offset))
        cmds.disconnectAttr ('{}.r'.format (temp_target_), '{}.inputRotate'.format (temp_offset))
        cmds.disconnectAttr ('{}.s'.format (temp_target_), '{}.inputScale'.format (temp_offset))

        # Reparent target_ to initial parent
        if parent != None :
            cmds.parent (temp_target_, parent)
        else :
            cmds.parent (temp_target_, w=True)  

        # Get offset Node
        cmds.connectAttr ('{}.outputMatrix'.format(temp_offset), '{}.matrixIn[0]'.format(temp_mult))
        cmds.connectAttr ('{}.offsetParentMatrix'.format(target_), '{}.matrixIn[1]'.format(temp_mult))
        cmds.connectAttr ('{}.matrixSum'.format(temp_mult), '{}.inputMatrix'.format(temp_decMat))

        cmds.connectAttr ('{}.outputTranslate'.format (temp_decMat), '{}.inputTranslate'.format (offset_node))
        cmds.connectAttr ('{}.outputRotate'.format (temp_decMat), '{}.inputRotate'.format (offset_node))
        cmds.connectAttr ('{}.outputScale'.format (temp_decMat), '{}.inputScale'.format (offset_node))

        cmds.disconnectAttr ('{}.outputTranslate'.format (temp_decMat), '{}.inputTranslate'.format (offset_node))
        cmds.disconnectAttr ('{}.outputRotate'.format (temp_decMat), '{}.inputRotate'.format (offset_node))
        cmds.disconnectAttr ('{}.outputScale'.format (temp_decMat), '{}.inputScale'.format (offset_node))

        # Delete unused nodes
        if cmds.objExists(temp_offset) :
            cmds.delete (temp_offset)
        if cmds.objExists(temp_mult) :
            cmds.delete (temp_mult)
        if cmds.objExists(temp_decMat) :
            cmds.delete (temp_decMat) 

        return offset_node
            
    def reset_transform (self, target_) :
        '''
        Reset all transform of object, in transform matrix and offsetParentMatrix
        target_ -> target to reset (str)
        '''
        cmds.xform(target_, translation=(0,0,0), rotation = (0,0,0), scale = (1,1,1))
        
        temp_comp = cmds.createNode('composeMatrix')
        cmds.connectAttr('{}.outputMatrix'.format(temp_comp), '{}.offsetParentMatrix'.format((target_)))
        cmds.disconnectAttr('{}.outputMatrix'.format(temp_comp), '{}.offsetParentMatrix'.format((target_)))

        if cmds.objExists(temp_comp) :
            cmds.delete (temp_comp)

    def connect_out_constraint (self, out_connect, target_, out_attribut) :
        '''
        This function connect one attribut to objec based on out_connect
        out_connect -> list of rules to connect object (list)
            [[[['TranslateX', 'translateX'], bool], [['TranslateY', 'translateY'], bool], [['TranslateZ', 'translateZ'], bool]], 
            [[['RotateX', 'rotateX'], bool], [['RotateY', 'rotateY'], bool], [['RotateZ', 'rotateZ'], bool]],
            [['ScaleX', 'scaleX'], bool], [['ScaleY', 'scaleY'], bool], [['ScaleZ', 'scaleZ'], bool]],
            bool]
        target_ -> target object to connect (str)
        out_attribut -> attribut to connect to object (str)
        '''
        # Connect to offsetParentMatrix bool 
        is_offset_parent_matrix = out_connect[3]

        # Create a decomposeMatrix node and connect out attribut to input matrix
        decomp_mat = cmds.createNode('decomposeMatrix', name = '{}_parentMConstraint_decMat'.format(target_))
        cmds.connectAttr(out_attribut, '{}.inputMatrix'.format(decomp_mat))
        out_translate = out_connect[0]
        out_rotate = out_connect[1]
        out_scale = out_connect[2]

        # if is_offset_parent_matrix, create a compose matrix so the file attribut type will be matrix
        if is_offset_parent_matrix :
            comp_mat = cmds.createNode('composeMatrix', name = '{}_parentMConstraint_compMat'.format(target_))
            # Connect traslate, rotate and scale according to out_connect values
            for each in out_translate, out_rotate, out_scale:
                for transform_axis, is_connect in each:
                    if is_connect :
                        cmds.connectAttr ('{}.output{}'.format(decomp_mat, transform_axis[0]), '{}.input{}'.format(comp_mat, transform_axis[0]))
                        
                        if not 'scale' in transform_axis[1] :
                            cmds.setAttr ('{}.{}'.format(target_, transform_axis[1]), 0)
                        else :
                            cmds.setAttr ('{}.{}'.format(target_, transform_axis[1]), 1) 

            # Connect compose Matrix to target's offsetParentMatrix
            cmds.connectAttr('{}.outputMatrix'.format(comp_mat), '{}.offsetParentMatrix'.format(target_))

        else :
            # Connect decomposeMatrix attributs to target's translate, rotate and scale according to out_connect values
            out_connect_list = out_connect[0] + out_connect[1] + out_connect[2]
            for transform_axis, is_connect in out_connect_list:
                if is_connect :
                    cmds.connectAttr ('{}.output{}'.format(decomp_mat, transform_axis[0]), '{}.{}'.format(target_, transform_axis[1]))

    # main parent matrix function
    def matrix_parent_constraint (self, offset, trigger_matrix, out_connect) :

        '''
        This function create a parent constraint with matrix
        offset -> Maintain offset between objects (bool)
        trigger_matrix -> matrix to connect for parent constraint (str)
        out_connect -> parameter of connections to connect target object (list)
            [[[['TranslateX', 'translateX'], bool], [['TranslateY', 'translateY'], bool], [['TranslateZ', 'translateZ'], bool]], 
            [[['RotateX', 'rotateX'], bool], [['RotateY', 'rotateY'], bool], [['RotateZ', 'rotateZ'], bool]],
            [['ScaleX', 'scaleX'], bool], [['ScaleY', 'scaleY'], bool], [['ScaleZ', 'scaleZ'], bool]],
            bool]
        '''
        # Get selected objects
        objects_ = self.get_objects(self)
        if not objects_ :
            return
        
        # Set target and trigger variable
        trigger_obj = objects_[0]
        target_obj = objects_[1]

        # Out mult matrix attributs
        out_attribut = []

        if out_connect [3] == True : 
            out_attr_list = ['offsetParentMatrix'] 
        else : 
            out_attr_list = ['translateX', 'translateY', 'translateZ',
                             'rotateX', 'rotateY', 'rotateZ',
                             'scaleX', 'scaleY', 'scaleZ'] 

        # If one attr of out_attr_list is already connected, abort parent matrix
        if not  nb_utils.test_output_connections ( out_attr_list, target_obj) :
            return
        
        # Get each trigger, create nodal network to parent constraint
        for x in range(len(trigger_obj)) :

            mult_node = cmds.createNode('multMatrix', name = '{}_{}_parentMConstraint_multMat'.format(trigger_obj, target_obj))

            if offset :

                offset_matrix = self.get_offset_matrix(self, target_obj, trigger_obj[x])

                cmds.connectAttr ('{}.outputMatrix'.format(offset_matrix), '{}.matrixIn[0]'.format(mult_node))
                cmds.connectAttr ('{}.{}'.format(trigger_obj[x], trigger_matrix), '{}.matrixIn[1]'.format(mult_node))
                if not out_connect [3] :
                    cmds.connectAttr ('{}.inverseParentMatrix'.format(target_obj), '{}.matrixIn[2]'.format(mult_node))

            else :
                cmds.connectAttr ('{}.{}'.format(trigger_obj[x], trigger_matrix), '{}.matrixIn[0]'.format(mult_node))
                if not out_connect [3] :
                    cmds.connectAttr ('{}.inverseParentMatrix'.format(target_obj), '{}.matrixIn[1]'.format(mult_node))

            out_attribut.append('{}.matrixSum'.format(mult_node))

        # If more than one out_attribut, create a blend node to make a multiple target parent Matrix
        if len(out_attribut) == 1 :
            self.connect_out_constraint (self, out_connect, target_obj, out_attribut[0])
        else :
            blend_node = cmds.createNode('blendMatrix', name = '{}_parentMConstraint_blendMat'.format(target_obj))

            number_of_parent = len(out_attribut)
            attr_weight = 1/number_of_parent

            for attr in range(number_of_parent):
                if attr == 0 :
                    cmds.connectAttr (out_attribut[attr], '{}.inputMatrix'.format(blend_node))

                else :
                    cmds.connectAttr(out_attribut[attr], '{}.target[{}].targetMatrix'.format(blend_node, attr))
                    cmds.setAttr ('{}.target[{}].weight'.format(blend_node, attr), attr_weight)

            
            self.connect_out_constraint (self, out_connect, target_obj, '{}.outputMatrix'.format(blend_node))

    def check_aim_variables (self, world_up_vector, primary_axis, secondary_axis) :
        '''
        This function check if each axis is correct. Unvalid axis is 0,0,0
        Return True if axis is valide, Otherwise False
        world_up_vector -> world up vector for aimConstraint (list)
        primary_axis -> primary vector for aimConstraint (list)
        secondary_axis -> scondary vector for aimConstraint (list)
        '''
        world_up_vector_named = world_up_vector + tuple(['World Up Vector'])
        primary_axis_named = primary_axis + tuple(['Primary Axis'])
        secondary_axis_named = secondary_axis + tuple(['Secondary Axis'])
        unvalid_axis = []
        
        # Check if vector is valid, append nvalid_axis if not
        for x_axis, y_axis, z_axis, name_axis in world_up_vector_named, primary_axis_named, secondary_axis_named:
            if x_axis == 0 and y_axis == 0 and z_axis == 0 :
                unvalid_axis.append (name_axis)

        # warn if unvalid axis and retrun false
        if unvalid_axis :
            cmds.warning ("Unvalid Axes : {}".format(', '.join(unvalid_axis)))
            return False
        
        return True

    def matrix_aim_constraint(self, in_opm, world_up_vector, world_up_object, primary_axis, secondary_axis) :

        objects_ = self.get_objects(self)

        if not objects_:
            return
        
        target_ = objects_ [1]
        trigger_ = objects_ [0]

        if not self.check_aim_variables(self, world_up_vector, primary_axis, secondary_axis) :
            return

        if world_up_object and not cmds.objExists(world_up_object) :
            cmds.warning ("World up Object doesn't exists")
            return

        if len(trigger_) != 1 :
            cmds.warning ("More than two objects are selected")
            return
        
        trigger_ = trigger_[0]
        
        if in_opm == True : 
            out_attr_list = ['offsetParentMatrix'] 
        else : 
            out_attr_list = ['rotateX', 'rotateY', 'rotateZ'] 

        if not  nb_utils.test_output_connections ( out_attr_list, target_) :
            return

        aim_node = cmds.createNode('aimMatrix', name = target_ + '_aimMConstraint_aimMat')

        cmds.setAttr ('{}.secondaryMode'.format (aim_node), 2)
        cmds.setAttr ("{}.primaryInputAxis".format(aim_node), *primary_axis)
        cmds.setAttr ("{}.secondaryInputAxis".format(aim_node), *secondary_axis)
        cmds.setAttr ("{}.secondaryTargetVector".format(aim_node), *world_up_vector)
        cmds.connectAttr ("{}.worldMatrix[0]".format(trigger_), "{}.primaryTargetMatrix".format(aim_node))

        if world_up_object :
            cmds.connectAttr ("{}.worldMatrix[0]".format(world_up_object), "{}.secondaryTargetMatrix".format(aim_node))
        else :
            cmds.connectAttr ("{}.worldMatrix[0]".format(trigger_), "{}.secondaryTargetMatrix".format(aim_node))

        aim_grp = cmds.createNode("transform", name = target_ + '_aimMConstraint_input')
        cmds.matchTransform(aim_grp, target_, position = True)
        cmds.connectAttr ("{}.worldMatrix[0]".format(aim_grp), "{}.inputMatrix".format(aim_node))
        cmds.parent (target_, aim_grp)

        cmds.setAttr ("{}.rotate".format(aim_grp), lock = True)

        decompose_mat = cmds.createNode ("decomposeMatrix", name = target_ + '_aimMConstraint_decMat')
        cmds.connectAttr("{}.outputMatrix".format(aim_node), "{}.inputMatrix".format(decompose_mat))

        if not in_opm :
            cmds.connectAttr ("{}.outputRotate".format(decompose_mat), "{}.rotate".format(target_))
            
        else :
            compose_node = cmds.createNode ("composeMatrix", name = target_ + '_aimMConstraint_compMat')
            
            cmds.setAttr ("{}.rotate".format(target_), *(0,0,0))
            
            cmds.connectAttr ("{}.outputRotate".format(decompose_mat), "{}.inputRotate".format(compose_node))
            cmds.connectAttr ("{}.outputMatrix".format(compose_node), "{}.offsetParentMatrix".format(target_))
            
        cmds.setAttr ("{}.translate".format(target_), *(0,0,0))
        cmds.setAttr ("{}.scale".format(target_), *(1,1,1))
