from maya import cmds

def parentSpace (targetControl, triggerControl, settings, parentTranslate, attr_name) :
    """
    Get all selected object. The last one is the object to create an attribut to, the previous is the object to deal with parent spaces.
    With a blend matrix node, setup parent contraints between a trigger and the target.
    blendMatrix weights are controled by choice nodes
    targetControl : object to deal with parent spaces (str)
    triggerControl : list of triggers (list)
    settings  : settings control (str)
    parentTranslate : parent spaces controls translation (bool)
    attr_name : name of the attribut that controls parent space
    """

    # Setup a naming for all created objects used by the function. Also create the string that the cmds.addAttr() comend needs
    target_name = targetControl.replace("_ctrl", "")
    enumList = ''
    targetList = []
    for each in triggerControl : 
        enumList += f':{each}'
        targetList.append (each)
    
    enumList = enumList[1:]    # remove the first caracter of the string (":")

    # create the parent space control attribut
    cmds.addAttr (settings, ln= attr_name, at="enum", en=enumList, k=True)

    # create blendMatrix node
    blendNode = cmds.createNode('blendMatrix', name = "{}_parentSpace_blendMat".format(target_name))
    
    # get the offset off each trigger with the target, connect it to blend matrix and setup choice node values
    for each in targetList :

        # naming for created nodes
        nodeName = each.replace ('_ctrl','')

        # create an empty transform node to connect parent spaces (not needed anymore)
        group = cmds.createNode('transform', name = '{}__{}_parent_grp'.format(nodeName, target_name))
        cmds.matchTransform (group, targetControl, pos = True, rot = True)

        # create multMatrix node and decomposeMatrix node. connect them
        mult_node = parent_space_parent_const (each, group)
        group_decMat = cmds.createNode("decomposeMatrix", name = '{}__{}_parent_decMat'.format(nodeName, target_name))
        cmds.connectAttr("{}.matrixSum".format(mult_node), "{}.inputMatrix".format(group_decMat))
        cmds.connectAttr ("{}.outputTranslate".format(group_decMat), "{}.translate".format(group))
        cmds.connectAttr ("{}.outputRotate".format(group_decMat), "{}.rotate".format(group))
        cmds.connectAttr ("{}.outputScale".format(group_decMat), "{}.scale".format(group))

        # If the object is the first list item, connect the result to "inputMatrix" attribut
        # Else, connect to target[n].targetMatrix
        if each == targetList[0] :
            cmds.connectAttr ('{}.wm[0]'.format(group), '{}.inputMatrix'.format(blendNode))

        else : 
            choiceNode = cmds.createNode ('choice', name = '{}__{}_parentSpace_choice'.format(nodeName, target_name))

            # set input value to 1 if the current index is the actual target, otherwise set it to 0
            for x in range (len(targetList)) :

                if x == targetList.index(each) :
                    cmds.setAttr ('{}.input[{}]'.format(choiceNode, x), 1)

                else : 
                    cmds.setAttr ('{}.input[{}]'.format(choiceNode, x), 0)
            
            # Connect nodes together
            cmds.connectAttr ('{}.{}'.format(settings, attr_name), '{}.s'.format(choiceNode))
            cmds.connectAttr ('{}.o'.format(choiceNode), '{}.target[{}].weight'.format(blendNode, targetList.index(each)))
            cmds.connectAttr ('{}.wm[0]'.format(group), '{}.target[{}].tmat'.format(blendNode, targetList.index(each)))

        # For rotation mode (ie. parentTranslate = False), keep the last multMatrix object
        if each == targetList[-1] :
            last_mult_node = mult_node

    # Rotation mode (ie. parentTranslate = False) : 
    # create an aditionnal blendmatrix to rule only rotate values
    # Connect the result to the target attribut
    if parentTranslate == False :

        rotBlend = cmds.createNode('blendMatrix', name = target_name + '_parentSpace_merge_blendMat')
        cmds.connectAttr (f'{blendNode}.omat', f'{rotBlend}.inputMatrix')
        cmds.connectAttr (f'{last_mult_node}.matrixSum', f'{rotBlend}.target[0].tmat')
        cmds.setAttr (f'{rotBlend}.target[0].rot', 0)
        cmds.connectAttr (f'{rotBlend}.omat', f'{targetControl}.opm')
        
    else :
        cmds.connectAttr (f'{blendNode}.omat', f'{targetControl}.opm')

    # Reset targetControl trtansform and rotate values
    cmds.setAttr (f'{targetControl}.t', *(0,0,0))
    cmds.setAttr (f'{targetControl}.r', *(0,0,0))


def do_parent_space (mode, attribut_name) :
    """
    Get selected object and sort them to be used in parentSpace function
    """

    # List selected objects
    object_list = cmds.ls(sl=True)

    # sort selected object
    target_control = object_list[-2]
    settings_control = object_list[-1]
    trigger_controls = object_list[:-2]

    # do parent space
    parentSpace (target_control, trigger_controls, settings_control, mode, attribut_name)

def parent_space_parent_const (trigger_obj, target_obj) :
    """
    Create a parent constraint for parent space between one trigger and one target. Retrun multMatrix node
    """
    
    offset_matrix = cmds.createNode ('composeMatrix', name = '{}_parentMConstraint_offset'.format(target_obj))
    temp_offset = cmds.createNode ('composeMatrix', name = trigger_obj + '_temp_offset')
    temp_mult = cmds.createNode ('multMatrix', name = trigger_obj + '_temp_mult')
    temp_decMat = cmds.createNode ('decomposeMatrix', name = trigger_obj + '_temp_decMat')

    #get parent
    parent = cmds.listRelatives (target_obj, p=True, typ = 'transform')

    #parent target_ to trigger_
    cmds.parent (target_obj, trigger_obj)

    #get translate relative to trigger_
    temp_target_ = target_obj

    try :
        cmds.connectAttr ('{}.t'.format (target_obj), '{}.inputTranslate'.format (temp_offset))
    except RuntimeError :
        cmds.connectAttr ('{}|{}.t'.format (trigger_obj,target_obj), '{}.inputTranslate'.format (temp_offset))
        temp_target_ = f'{trigger_obj}|{target_obj}'
        
    cmds.connectAttr ('{}.r'.format (temp_target_), '{}.inputRotate'.format (temp_offset))
    cmds.connectAttr ('{}.s'.format (temp_target_), '{}.inputScale'.format (temp_offset))

    cmds.disconnectAttr ('{}.t'.format (temp_target_), '{}.inputTranslate'.format (temp_offset))
    cmds.disconnectAttr ('{}.r'.format (temp_target_), '{}.inputRotate'.format (temp_offset))
    cmds.disconnectAttr ('{}.s'.format (temp_target_), '{}.inputScale'.format (temp_offset))

    #reparent target_ to initial parent
    if parent != None :
        cmds.parent (temp_target_, parent)
    else :
        cmds.parent (temp_target_, w=True)  

    cmds.connectAttr ('{}.outputMatrix'.format(temp_offset), '{}.matrixIn[0]'.format(temp_mult))
    cmds.connectAttr ('{}.offsetParentMatrix'.format(target_obj), '{}.matrixIn[1]'.format(temp_mult))
    cmds.connectAttr ('{}.matrixSum'.format(temp_mult), '{}.inputMatrix'.format(temp_decMat))

    #parent target_ to trigger_
    cmds.connectAttr ('{}.outputTranslate'.format (temp_decMat), '{}.inputTranslate'.format (offset_matrix))
    cmds.connectAttr ('{}.outputRotate'.format (temp_decMat), '{}.inputRotate'.format (offset_matrix))
    cmds.connectAttr ('{}.outputScale'.format (temp_decMat), '{}.inputScale'.format (offset_matrix))

    cmds.disconnectAttr ('{}.outputTranslate'.format (temp_decMat), '{}.inputTranslate'.format (offset_matrix))
    cmds.disconnectAttr ('{}.outputRotate'.format (temp_decMat), '{}.inputRotate'.format (offset_matrix))
    cmds.disconnectAttr ('{}.outputScale'.format (temp_decMat), '{}.inputScale'.format (offset_matrix))

    #delete unused nodes
    if cmds.objExists(temp_offset) :
        cmds.delete (temp_offset)
    if cmds.objExists(temp_mult) :
        cmds.delete (temp_mult)
    if cmds.objExists(temp_decMat) :
        cmds.delete (temp_decMat) 

    mult_node = cmds.createNode('multMatrix', name = '{}_parentMConstraint_multMat'.format(target_obj))

    cmds.connectAttr ('{}.outputMatrix'.format(offset_matrix), '{}.matrixIn[0]'.format(mult_node))
    cmds.connectAttr ('{}.worldMatrix[0]'.format(trigger_obj), '{}.matrixIn[1]'.format(mult_node))

    return mult_node

