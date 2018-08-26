# Dynamic Utils
#
# Monika Gelbmann
# Updated 05 Dex 2015
'''
import mo_dynamicUtils as mo_dynamicUtils
mo_dynamicUtils.createPassiveCollider()
'''

import pymel.core as pm
import os.path
import maya.cmds as mc
import maya.mel as mel



###### Dynamic Utils ######

def createPassiveCollider(geo=None):
    '''
    Create passive Collider and rename to 'nRigid_objName'
    '''

    if geo == None: geo = pm.selected()[0]
    makecolide = "makeCollideNCloth;"
    mel.eval(makecolide)
    rigid = pm.selected()[0].listRelatives(parent=1)[0]
    pm.rename(rigid, '%s_nRigid' % geo.name())

def createVolumeCrv(curves=None):
    if curves == None: curves = pm.selected()
    for curve in curves:
        name = '%s_volumeCurve'%curve.replace('_crv', '')
        pm.volumeAxis(name=name, vof=(0, 0, 0), vsw=360, arx=0, dy=0, pos=(0, 0, 0), vsh='cube', alx=0, ia=0, toz=0, tox=0, toy=0, afc=1, afx=1, tsr=0.5, dtr=0, tfy=1, tfx=1, dx=1, tfz=1, mxd=-1, drs=0, trb=0, m=5, att=0, dz=0, trs=0.2)
        pm.connectAttr('time1.outTime', '%s.time'%name)
        pm.connectAttr('%s.worldSpace[0]'%curve, '%s.inputCurve'%name)
        pm.setAttr('%s.volumeShape'%name, 7)

def nclothAttrTransfer(fromNcloth, toNcloth):
    '''
    transfer input attract per vertex to another another ncloth
    '''
    hi = pm.getAttr('%s.inputAttractPerVertex' % fromNcloth)
    CMD = ("setAttr -type doubleArray %s.inputAttractPerVertex %s" % (toNcloth, len(hi)))
    for aVal in hi:
        CMD += (" " + str(aVal))

    pm.mel.eval(CMD)


def nclothAttrFlood(value, ncloths=[], attr='inputAttract', operation='Replace '):
    '''
    flood ncloth vertex attr
    '''
    if ncloths == []: ncloths = pm.selected()  # pm.select(ncloth)
    pm.mel.setNClothMapType(attr, "", 1)
    pm.mel.artAttrNClothToolScript(4, attr)
    pm.mel.artAttrPaintOperation('artAttrCtx', operation)
    pm.artAttrCtx(pm.currentCtx(), e=1, value=value)
    pm.artAttrCtx(pm.currentCtx(), clear=1, e=1)


def nclothAttrSmooth(iterations=1):
    for i in range(iterations):
        pm.mel.artAttrPaintOperation('artAttrCtx', 'Smooth')
        pm.artAttrCtx(pm.currentCtx(), clear=1, e=1)


def connectVisibilityToIsDynamic():
    """
        connect isDynamic of nParticle and nRigid to its Transform nodes visiblity
        hide in outliner will disable the dynamic
    """
    dynamics = pm.ls(type='particle')
    for dynamic in dynamics:
        dynamic.getTransform().visibility >> dynamic.isDynamic

def transferAttrs(sourceObj, targetObjs, attributes=[]):
    """Copies the value(s) of the attribute from sourceObj to targetObj. Handles multi-attributes."""
    sourceObj = pm.PyNode(sourceObj)
    
    if attributes == []:
        attributes=pm.listAttr(sourceObj, k=1, l=0)
    
    for targetObj in targetObjs:
        targetObj = pm.PyNode(targetObj)
    
        for attribute in attributes:
            sourceAttrNode = pm.PyNode('%s.%s'%(sourceObj, attribute))
            print 'sourceAttr is %s'%sourceAttrNode
            
            if pm.attributeQuery(attribute, node = targetObj.name(), exists=True): # Execute only if the entered attribute exists
                
                multiAttr = pm.attributeQuery(attribute, node=targetObj.name(), listChildren=1) # Get list of multi-attribute children, if any
        
                if multiAttr: # If the attribute is a multi-attribute
                    extraInst = set(sourceObj.getAttr(attribute, mi=1)).symmetric_difference( set(targetObj.getAttr(attribute, mi=1)) ) # Get the set of extra instances in multi-attribute
                    for ins in extraInst: # Remove these extra instances
                        pm.removeMultiInstance('{0}.{1}[{2}]'.format(targetObj.name(), attribute, ins) )
                        
                    for attrChild in multiAttr:
                        for ind in sourceObj.getAttr(attribute, mi=1):
                            attrString = '{attr}[{index}].{child}'.format( attr = attribute,
                                                                        index = ind,
                                                                        child = attrChild )
                            
                            attrVal = sourceObj.getAttr( attrString )
                            targetObj.setAttr( attrString, attrVal )
                            print( '//  {objName}.{attr} was set to {val}  //'.format(objName = targetObj.name(),
                                                                            attr = attrString,
                                                                            val = attrVal) )
                else:
                    trgtAttrNode = pm.PyNode('%s.%s'%(targetObj, attribute))
                    
                    # clear target Attr
                    if trgtAttrNode.isConnected():
                        trgtConn = trgtAttrNode.listConnections(scn=1)
                        if trgtConn[0].type() in ['expression', 'animCurveTU']: # If animCurve or Expression connected, delete it
                            pm.delete(trgtConn)
                        else:
                            pm.disconnectAttr(trgtAttrNode)

                    
                    if sourceAttrNode.isConnected():
                        conn = sourceAttrNode.listConnections(scn=1)
                        if conn[0].type() == 'expression': # If the attribute has an expression
                            dupconn = pm.duplicate(conn[0])
                            expressionstring = conn[0].getExpression().replace(sourceObj.name(), targetObj.name())
                            dupconn[0].setExpression(expressionstring)
                        elif conn[0].type() == 'animCurveTU': # If the attribute is keyed
                            pm.copyKey(sourceObj, at=attribute)
                            pm.pasteKey(targetObj, at=attribute, o='replace')
                    else: # Otherwise simple copy paste attr
                            attrVal = sourceObj.getAttr(attribute)
                            try:
                                targetObj.setAttr(attribute, attrVal)
                            except Exception as e:
                                print 'Error occurred : ' + str(e)
                                continue

                            print('//  {0}.{1} was set to {2}  //\n'.format(targetObj.name(), attribute, attrVal) )
            else:
                print('!!  {0} does not exist  !!\n'.format(attribute))
