import pymel.core as pm

def ro_primaryVisiblity(enable=0):
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
