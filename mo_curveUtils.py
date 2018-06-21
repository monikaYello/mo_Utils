import pymel.core as pm
'''
import mo_Utils.mo_curveUtils as curveUtils
reload(curveUtils)
curveUtils.snapCurveToBoundingBox('building_ctrl', 'building_geo')
curveUtils.getCurveWorldPoints(crv)
'''
def test():
    print 'test'

def getCurveWorldPoints(crv):
    crv = pm.ls(crv)[0]
    print crv
    ss = crv.getShape()
    if (ss.__class__ is not pm.nodetypes.NurbsCurve):
        print 'Error. No Nurbs Curve'
        return False
    curvepoints = ss.numCVs()
    pointList = []
    pointPosList = []
    for curvepoint in range(curvepoints):
        pointp = pm.pointPosition('%s.cv[%s]'%(ss,curvepoint))
        if(pointp not in pointPosList):
            pointPosList.append(pointp)
            pointList.append(curvepoint)
    return pointList, pointPosList


def getClosestVertex(locator, searchGeo):
    ''' Find closest Vertex from given Locator
    Args:
        locator (transform): The locator as the base for the search
        searchGeo (transform): The geo on with the vertex to find
    Returns: 
        MeshVertex: Closest vertex (pSphere.vtx[7])
    '''
    import maya.OpenMaya as OpenMaya
    geo = pm.PyNode(searchGeo)
    loc = pm.PyNode(locator)
    pos = loc.getRotatePivot(space='world')
     
    nodeDagPath = OpenMaya.MObject()
    try:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(geo.name())
        nodeDagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, nodeDagPath)
    except:
        raise RuntimeError('OpenMaya.MDagPath() failed on %s' % geo.name())
     
    mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
     
    pointA = OpenMaya.MPoint(pos.x, pos.y, pos.z)
    pointB = OpenMaya.MPoint()
    space = OpenMaya.MSpace.kWorld
     
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()
     
    mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)  
    idx = OpenMaya.MScriptUtil(idPointer).asInt()
     
    faceVerts = [geo.vtx[i] for i in geo.f[idx].getVertices()]
    closestVert = None
    minLength = None
    for v in faceVerts:
        thisLength = (pos - v.getPosition(space='world')).length()
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v
    return closestVert

def snapCurveToClosestVertices(crv, geo):
    ''' Find closest Vertex on geo for each cv on curve and snaps to it
    Args:
        crv (transform): The curve which shall be snapped
        geo (transform): The geo as the base for the search
    Returns: 
         True if no error
    '''
    crvShape = pm.PyNode(crv).getShape()
    geoShape = pm.PyNode(geo).getShape()
    
    numcvs = crvShape.numCVs()
    
    
    for curvePoint in range(numcvs):
        # find closest vertex
        tempLoc = pm.spaceLocator(n='tempLoc')
        pm.xform(tempLoc, t=pm.pointPosition(crvShape.cv[curvePoint]))
        closestVertex = getClosestVertex(tempLoc, geo)
        
        # move curvepoint to closest vertex
        pm.xform(tempLoc, t=pm.pointPosition(closestVertex))
        pm.move(crvShape.cv[curvePoint], pm.pointPosition(closestVertex))
        
        pm.delete(tempLoc)
    return True


def snapCurveToBoundingBox(crvToAlign, geo):
    
    ''' Align existing crv(ctrl) to a geo's bounding box 
        creates temp bounding box object and determining closest vertex for each curve point
        so it will only work if curve is centered overall over the geo
    Args:
        crvToAlign (transform): The curve which shall be modified
        geo (transform): The geo to align to
    Returns: 
        True if no error
    '''
    import riggTool.thirdParty.python.boundingBox as bb #### <<<<<<<<<<<<< modify this to proper path >>>>>>>>>>>>>>> ######
    reload(bb)
    
    # create bounding box for geo
    pm.select(geo)
    bbGeo = bb.boundBox(1,0,0,0,0,[0,0,0])
    # snap curve to closest vertices on bounding box
    snapCurveToClosestVertices(crvToAlign, bbGeo[0])
    # delete bounding bos
    pm.delete(bbGeo)
    pm.select(crvToAlign)
    return True