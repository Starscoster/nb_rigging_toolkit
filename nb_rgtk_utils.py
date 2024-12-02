from maya import cmds

def test_output_connections (connections_, target_) :
    '''
    This function test if objects has already a connection
    connection_ -> tested attribut list (list)
    target_ -> tested object (str)
    '''
    result_list = []

    # Testing attribut connection. If True, append taget_.attr in result_list
    for attr in connections_ : 
        if cmds.listConnections( "{}.{}".format (target_, attr)) : 
            result_list.append ('{}.{}'.format(target_, attr))

    # If result list, display cmds.warning message with "already connected" and return False. Otherwise, return True
    if len(result_list) == 1 :
        cmds.warning ("Channel {} is already connected".format (result_list[0]))
        return False
    elif len(result_list) !=0 : 
        cmds.warning ("Channels {} are already connected".format (', '.join(result_list)))
        return False
    
    return True

def create_rigging_module (module_name) :
    '''
    This functions create a rigging module setup wich is basicly four groups in one module group ordered as follow :
    Module_grp
        public_grp
        private_grp
        input_grp
        output_grp
    '''
    # Created groups
    group_list = [["_module_grp", (1,1,1)],
    ["_public_grp", (0,1,0)],
    ["_private_grp", (1,0,0)],
    ["_input_grp", (0,1,1)],
    ["_output_grp", (0,1,1)]]

    # Created groups, parent them and set outliner color attribut
    for group_name, group_color in group_list :

        if not cmds.objExists("{}{}".format(module_name, group_name)) :

            group = cmds.createNode("transform", name = "{}{}".format(module_name, group_name))
            cmds.setAttr("{}.useOutlinerColor".format (group), True)
            cmds.setAttr("{}.outlinerColor".format (group), *group_color)
            
            if not group_list[0][0] in group :
                cmds.parent (group, "{}{}".format(module_name, group_list[0][0]))

        else : 
            cmds.warning ("{}{} already exists, passed.".format (module_name, group_name))

def set_transform_in_opm () :
    '''
    This function set all translate, rotate and scale attributs values in offsetParentMatrix
    '''

    # get object selected
    sel = cmds.ls(sl=True)
    if not sel:
        return
    
    # For each object, get new matrix by multiply offsetParentMatrix and transformMatrix.
    # This process allows to maintain control position regardless of his parents
    for each in sel :

        # if offsetParentMatrix is already connected, pass
        if not test_output_connections(['offsetParentMatrix'], each) :
            continue

        cmds.select (d=True)
        
        # Create necessary nodes
        composeMat = cmds.createNode ('composeMatrix', name = 'OPMtemp_compMat')
        decomposeMat = cmds.createNode ('decomposeMatrix', name = 'OPMtemp_decompMat')
        multMat = cmds.createNode ('multMatrix', name = 'OPMtemp_multMat')
        
        # Multiply offsetParentMatrix and transformMatrix
        cmds.connectAttr('{}.matrix'.format(each), '{}.matrixIn[0]'.format(multMat))
        cmds.connectAttr('{}.offsetParentMatrix'.format(each), '{}.matrixIn[1]'.format(multMat))
        
        cmds.connectAttr('{}.matrixSum'.format(multMat), '{}.inputMatrix'.format(decomposeMat))
        
        cmds.connectAttr('{}.outputTranslate'.format(decomposeMat), '{}.inputTranslate'.format(composeMat))
        cmds.connectAttr('{}.outputRotate'.format(decomposeMat), '{}.inputRotate'.format(composeMat))
        cmds.connectAttr('{}.outputScale'.format(decomposeMat), '{}.inputScale'.format(composeMat))
        
        cmds.disconnectAttr('{}.outputTranslate'.format(decomposeMat), '{}.inputTranslate'.format(composeMat))
        cmds.disconnectAttr('{}.outputRotate'.format(decomposeMat), '{}.inputRotate'.format(composeMat))
        cmds.disconnectAttr('{}.outputScale'.format(decomposeMat), '{}.inputScale'.format(composeMat))
        
        # Set composeMat matrix in offsetParentMatrix
        cmds.connectAttr('{}.outputMatrix'.format(composeMat), '{}.offsetParentMatrix'.format(each))
        
        # reset transform matrix
        cmds.setAttr ('{}.translate'.format(each), *(0,0,0))
        cmds.setAttr ('{}.rotate'.format(each), *(0,0,0))
        cmds.setAttr ('{}.scale'.format(each), *(1,1,1))
        
        # delete created node if still exists
        for custom_node in [composeMat, decomposeMat, multMat] :
            if cmds.objExists(custom_node) :
                cmds.delete (custom_node)
        
def reset_joint_orient() :
    '''
    This function takes current selection and, if each element is a joint, reset jointOrient attribut
    '''
    obj_list = cmds.ls(sl=True)

    if not obj_list :
        return
    
    for element in obj_list :
        if cmds.objectType(element) == "joint" :
            cmds.setAttr ("{}.jointOrient".format(element), *(0,0,0))

def fast_connect_attr (attribut) :
    '''
    This function takes object selected and connect the first of them attribut with all others  selected object attribut
    attribut -> attribut to connect (str)
    '''
    object_list = cmds.ls(sl=True)

    if not object_list :
        return
    
    for obj in object_list :
        if not cmds.objExists("{}.{}".format(obj, attribut)) :
            cmds.warning("{}.{} doesn't exists".format(obj, attribut))
            return
    
    for x in range(len(object_list)-1) :
        cmds.connectAttr("{}.{}".format(object_list[0], attribut), "{}.{}".format(object_list[x+1], attribut))
