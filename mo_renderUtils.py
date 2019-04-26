import pymel.core as pm

def renderlayerOverride_primaryVisiblity(enable=0):
    '''
    Render override primary visiblity off
    '''
    objs = pm.selected()
    for obj in objs:
        try:
            obj = obj.getShape()
        except:
            pass
        pm.editRenderLayerAdjustment("%s.primaryVisibility"%obj)
        pm.setAttr("%s.primaryVisibility"%obj, enable)

def renderlayerOverride_attribute(attribute, enable=0):
    '''
    Render override primary visiblity off
    '''
    objs = pm.selected()
    for obj in objs:
        try:
            obj = obj.getShape()
        except:
            pass
        pm.editRenderLayerAdjustment("%s.%s"%(obj, attribute))
        pm.setAttr("%s.%s"%(obj, attribute), enable)
