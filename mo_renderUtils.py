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
        print 's is %s' % s
        objs = pm.ls(s, type='transform') + pm.listRelatives(
            s, children=1, ad=1, type='transform')
        for obj in objs:
            try:
                print 'changing %s.%s' % (obj, attribute)
                obj = obj.getShape()
                pm.editRenderLayerAdjustment("%s.%s" % (obj, attribute))
                pm.setAttr("%s.%s" % (obj, attribute), enable)
            except:
                pass
    printon = 'off'
    if enable == 1: printon = 'on'
    pm.system.warning('Successs. Turned %s %s on %s meshes' %
                      (printon, attribute, len(objs)))


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
        valueNew = pm.setAttr(
            '{}.dso'.format(nodeShape),
            valueOld.replace(replaceString[0], replaceString[1]))
        name = valueOld.replace(
            replaceString[0], replaceString[1]).split('/')[-1].split('.ass')[0]
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


def exportASS(obj_to_export):
    '''
    Export as ass files. Name is that of node name. Save into current scene folder.  
    '''
    #obj_to_export = pm.ls('Aspen_Quaking_Field_*_lo', type='transform')
    import pymel.core as pm
    dir = pm.sceneName().parent

    for obj in obj_to_export:
        pm.select(obj)
        obj_name = obj.nodeName()
        pm.arnoldExportAss(f="%s/%s.ass" % (dir, obj_name),
                           mask=2297,
                           lightLinks=0,
                           s=1,
                           boundingBox=1,
                           shadowLinks=0)



def makeCurveRenderable(curves=[], shadername='featherFine_ai', curveWidth=0.002, sampleRate=6):
    if curves == []: curves=pm.selected()
    for dupCurve in curves:
        dupCurveShape=dupCurve.getShape()
        pm.setAttr(dupCurveShape.aiRenderCurve, 1)
        pm.setAttr(dupCurveShape.aiCurveWidth, curveWidth)
        pm.setAttr(dupCurveShape.aiSampleRate, sampleRate)
        pm.connectAttr("%s.outColor"%shadername, dupCurveShape.aiCurveShader, f=1)


def disableAllImageplanes():
        scene_imgplanes = cmds.ls(type='imagePlane')
        hidden_imgplanes = []
        for scene_imgplane in scene_imgplanes:
            print cmds.getAttr('%s.displayMode'%scene_imgplane) 
            if cmds.getAttr('%s.displayMode'%scene_imgplane) > 0:
                    print('Disabling imageplane %s'%scene_imgplane)
                    cmds.setAttr('%s.displayMode'%scene_imgplane, 0)
                    hidden_imgplanes.append(scene_imgplane)
        return hidden_imgplanes

def enableImageplanes(hidden_imgplanes):
        for hidden_imgplane in hidden_imgplanes:
                if cmds.getAttr('%s.displayMode'%hidden_imgplane) == 0:
                        print('Enabling imageplane %s'%hidden_imgplane)
                        cmds.setAttr('%s.displayMode'%hidden_imgplane, 3)