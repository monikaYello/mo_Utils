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
    pm.rename(rigid, 'nRigid_%s' % geo.name())


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
