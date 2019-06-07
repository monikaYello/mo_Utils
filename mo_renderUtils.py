import pymel.core as pm


def renderlayerOverride_attribute(attribute, enable=0):
    '''
    Render override primary visiblity off
    # render override primary visibiligy
    mo_renderUtils.renderlayerOverride_attribute('primaryVisibility',enable=0))
    '''
    sel = pm.selected()
    objs = []

    for s in sel:
        objs = pm.ls(s, type='mesh') + pm.listRelatives(s, children=1, ad=1, type='mesh')
        for obj in objs:
            try:
                obj = obj.getShape()
            except:
                pass
            pm.editRenderLayerAdjustment("%s.%s"%(obj, attribute))
            pm.setAttr("%s.%s"%(obj, attribute), enable)
    printon = 'off'
    if enable == 1: printon = 'on'
    pm.system.warning('Successs. Turned %s %s on %s meshes'%(printon, attribute, len(objs)))


def renameAssNodes():

    nodes = pm.selected()

    for node in nodes:
        nodeShape = node.getShape()
        valueOld = pm.getAttr('{}.dso'.format(nodeShape))
        name = valueOld.split('/')[-1].split('.ass')[0]
        pm.rename(node, name)
# renameAssNodes()


def repathAss(newpath=''):

    nodes = pm.selected()

    for node in nodes:
        nodeShape = node.getShape()
        valueOld = pm.getAttr('{}.dso'.format(nodeShape))
        valueNew = pm.setAttr('{}.dso'.format(newpath), newpath)
        name = newpath.split('/')[-1].split('.ass')[0]
        pm.rename(node, name)

def replaceAss(replaceString=['Z:', '//192.168.120.60/3d/']):

    nodes = pm.selected()

    for node in nodes:
        nodeShape = node.getShape()
        valueOld = pm.getAttr('{}.dso'.format(nodeShape))
        valueNew = pm.setAttr('{}.dso'.format(nodeShape), valueOld.replace(replaceString[0], replaceString[1]))
        name = valueOld.replace(replaceString[0], replaceString[1]).split('/')[-1].split('.ass')[0]
        pm.rename(node, name)

def lowresAss():

    nodes = pm.selected()

    for node in nodes:
        nodeShape = node.getShape()
        valueOld = pm.getAttr('{}.dso'.format(nodeShape))
        newpath = valueOld.replace('.ass.gz', '_lores.ass.gz')
        print(newpath)

        valueNew = pm.setAttr('{}.dso'.format(nodeShape), newpath)
        name = newpath.split('/')[-1].split('.ass')[0]
        pm.rename(node, name)
