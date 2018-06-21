
import pymel.core as pm

def findClosestObject(lookupNode=None, searchNodes=[]):
    if searchNodes ==[]:
        searchNodes = pm.selected()[:-1]
    if lookupNode == None:
        lookupNode =pm.selected()[-1]

    lookupVec =  pm.dt.Vector(pm.xform(lookupNode, q=1, t=1, ws=1))

    closestNode = None
    closestVec = W

    for iterNode in searchNodes:
        iterVec =  pm.dt.Vector(pm.xform(iterNode, q=1, t=1, ws=1))
        print (iterVec - lookupVec)
        if closestVec == None:
            closestVec = ( iterVec - lookupVec)
            closestNode = iterNode
        if (iterVec - lookupVec).length() < closestVec.length():
            closestVec = (iterVec - lookupVec)
            closestNode = iterNode

    print 'Closest Node is %s'%closestNode
    return closestNode

def printsomething():
    print 'test'
    
def measureExpression():
    '''
    /// exp
    measureRefPython:distanceDimension1.visibility=1;
    python("import measureUtils as mu"); 
    python("reload(mu)");
    python("mu.createMeasure()");
    '''
    sel = pm.selected()
    name = "distanceDimension1_annotation"

    if pm.objExists('measuregroup'):
        print 'exists'
        pm.delete('measuregroup')
    pm.group(n='measuregroup', empty=1)
    
    pm.setAttr('distanceDimension1.distanceFeet', pm.getAttr('distanceDimensionShape1.distance')*0.0328084)
    t = pm.textCurves(ch=0, f="Utopia-Regular" , n=name, t=pm.getAttr('distanceDimension1.distanceFeet'))
    pm.parent(t, 'measuregroup')

    pm.select(sel)



def createMeasure():
    sel = pm.selected()
    name = "distanceDimension1_annotation"
    
    if pm.objExists('measuregroup'):
        print 'exists'
        pm.delete('measuregroup')
    pm.group(n='measuregroup', empty=1)
    
    pm.setAttr('distanceDimension1.distanceFeet', pm.getAttr('distanceDimensionShape1.distance')*0.0328084)
    t = pm.textCurves(ch=0, f="Utopia-Regular" , n=name, t=pm.getAttr('distanceDimension1.distanceFeet'))
    pm.parent(t, 'measuregroup')

    pm.select(sel)

