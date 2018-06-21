import pymel.core as pm
# import sys
# sys.path.append('D:/Google Drive/PythonScripting/scripts/thirdParty/')
# import nVec
import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
from math import sqrt
import logging
_logger = logging.getLogger(__name__)


'''
import maya.api.OpenMaya as om
import mo_Utils.mo_mathUtils as mo_mathUtils
reload(mo_mathUtils)
objA = pm.PyNode('joint1')
objB = pm.PyNode('joint2')
#get the translation and store those as MVectors
t1, t2 = cmds.xform(cube1, t=1, q=1), cmds.xform(cube2, t=1, q=1)
v1, v2 = om.MVector(t1), om.MVector(t2)
print v1, v2

###### get info shoulder, ellbow angle ####
startObj = 'JILL:jill_sk_lf_shoulder'
midObj = 'JILL:jill_sk_lf_elbow'
endObj = 'JILL:jill_sk_lf_armend1'
vecA = om.MVector(pm.xform(midObj, q=1, t=1, ws=1)) - om.MVector(pm.xform(startObj, q=1, t=1, ws=1))
vecB = om.MVector(pm.xform(endObj, q=1, t=1, ws=1)) - om.MVector(pm.xform(midObj, q=1, t=1, ws=1))

mathUtils.vecViz(vecA, name='vA')
mathUtils.vecViz(vecB, name='vB')

mathUtils.vectorInfo(vecA, vecB)


#############################
import mo_Utils.mo_mathUtils as mathUtils
reload(mathUtils)

startObj = 'JILL:jill_sk_lf_shoulder'
mitObj = 'JILL:jill_sk_lf_elbow'
endObj = 'JILL:jill_sk_lf_armend'
startPos, midPos , endPos = pm.xform(startObj, q=1, t=1, ws=1), pm.xform(midObj, q=1, t=1, ws=1), pm.xform(endObj, q=1, t=1, ws=1)
startVec= om.MVector(startPos[0],startPos[1],startPos[2])
midVec= om.MVector(midPos[0],midPos[1],midPos[2])

reload(mathUtils)
mathUtils.angleBetween(startObj, midObj, endObj)
mathUtils.vecViz(startVec)
mathUtils.vecViz(midVec)


'''


def eigh(a, tol=1.0e-9):
    """
    Calculates the eigenValues and vectors using jacobi method.
    Code configured without numpy from http://goo.gl/U3m7nX

    Returns:
        (list of 3 floats) EigenValues
        (3x3 list of floats) EigenVectors

    Raises:
        None
    """
    # Find largest off-diag. element a[k][l]
    def maxElem(a):
        n = len(a)
        aMax = 0.0
        for i in xrange(n-1):
            for j in xrange(i+1, n):
                if abs(a[i][j]) >= aMax:
                    aMax = abs(a[i][j])
                    k = i
                    l = j
        return aMax, k, l

    # Rotate to make a[k][l] = 0
    def rotate(a, p, k, l):
        n = len(a)
        aDiff = a[l][l] - a[k][k]
        if abs(a[k][l]) < abs(aDiff) * 1.0e-36:
            t = a[k][l] / aDiff
        else:
            phi = aDiff/(2.0 * a[k][l])
            t = 1.0/(abs(phi) + sqrt(phi**2 + 1.0))
            if phi < 0.0:
                t = -t
        c = 1.0/sqrt(t**2 + 1.0)
        s = t*c
        tau = s/(1.0 + c)
        temp = a[k][l]
        a[k][l] = 0.0
        a[k][k] = a[k][k] - t * temp
        a[l][l] = a[l][l] + t * temp
        for i in xrange(k):      # Case of i < k
            temp = a[i][k]
            a[i][k] = temp - s*(a[i][l] + tau*temp)
            a[i][l] = a[i][l] + s*(temp - tau*a[i][l])
        for i in xrange(k+1, l):  # Case of k < i < l
            temp = a[k][i]
            a[k][i] = temp - s*(a[i][l] + tau*a[k][i])
            a[i][l] = a[i][l] + s*(temp - tau*a[i][l])
        for i in xrange(l+1, n):  # Case of i > l
            temp = a[k][i]
            a[k][i] = temp - s*(a[l][i] + tau*temp)
            a[l][i] = a[l][i] + s*(temp - tau*a[l][i])
        for i in xrange(n):      # Update transformation matrix
            temp = p[i][k]
            p[i][k] = temp - s*(p[i][l] + tau*p[i][k])
            p[i][l] = p[i][l] + s*(temp - tau*p[i][l])

    # Set limit on number of rotations
    n = len(a)
    maxRot = 5*(n**2)

    p = [[1.0,  0.0,  0.0],
         [0.0,  1.0,  0.0],
         [0.0,  0.0,  1.0]]

    # Jacobi rotation loop
    for i in xrange(maxRot):

        aMax, k, l = maxElem(a)

        if aMax < tol:
            return [a[i][i] for i in xrange(len(a))], p

        rotate(a, p, k, l)


def normalizedDot(vec1, vec2, startPos):
    startPosToVec1 = vec1 - om.MVector(startPos)
    startPosToVec2 = vec2 - om.MVector(startPos)
    return ( startPosToVec1.normal() *  startPosToVec2.normal())


def normalizedDotEllbow(shoulderJnt, armJnt, wristJnt):
    '''

    Close to 0 if perpendicular, 1 same direction, -1 opposing

    moMath.normalizedDotEllbow(shoulderJnt='L_arm01_skinJnt', armJnt='L_arm02_skinJnt', wristJnt='L_hand01_skinJnt')
    '''

    shoulder_pos = cmds.xform(shoulderJnt, q=1, t=1, ws=1)
    elbow_pos = cmds.xform(armJnt, q=1, t=1, ws=1)
    wrist_pos = cmds.xform(wristJnt, q=1, t=1, ws=1)

    bicep_vector = (om.MVector(elbow_pos) -  om.MVector(shoulder_pos)).normal()
    forearm_vector = (om.MVector(*wrist_pos) - om.MVector(*elbow_pos)).normal()

    # DOT
    elbow_bend = bicep_vector * forearm_vector

    print elbow_bend
    return elbow_bend


def angleBetween(startObj, midObj, endObj):
    '''

    Get angle in degree between mid-start-vector and mid-end-vector

    moMath.angleBetweenTwoVectors(shoulderJnt='L_arm01_skinJnt', armJnt='L_arm02_skinJnt', wristJnt='L_hand01_skinJnt')
    '''

    startPos, midPos , endPos = pm.xform(startObj, q=1, t=1, ws=1), pm.xform(midObj, q=1, t=1, ws=1), pm.xform(endObj, q=1, t=1, ws=1)
    startVec= om.MVector(startPos[0],startPos[1],startPos[2])
    midVec= om.MVector(midPos[0],midPos[1],midPos[2])
    endVec= om.MVector(endPos[0],endPos[1],endPos[2])

    midStartVec =  midVec - startVec
    midEndVec = endVec -  midVec

    angle = math.degrees(midStartVec.angle(midEndVec))

    return angle


def selectObjFacingDirection(objList, direction='x', accuracy=0.7):

    # def joints facing x direction
    sel = []

    for obj in objList:
        v = om.MVector(cmds.xform(obj, t=1, q=1)).normal()
        dot = v*om.MVector([1,0,0])
        if dot > accuracy: sel.append(obj)

    cmds.select(sel)
    return sel

def crossVector(name, base, loc1, loc2, target, distance=None):
    
    vecBase = nVec.NVec('%s.worldPosition'%base, name)
    vecA = nVec.NVec('%s.worldPosition'%loc1, name)
    vecB = nVec.NVec('%s.worldPosition'%loc2, name)
    
    
    if distance.__class__.__name__ == 'int':
        scaleV = nVec.NScalar.from_value(distance, 'scal')
    elif distance.__class__.__name__ == 'Transform' or distance.__class__.__name__ == 'str':
        scaleV = nVec.NScalar('%s.ty'%distance, 'scal')
    else:
        scaleV = nVec.NScalar.from_value(10, 'scal')
        
    
    vec1 = vecA - vecBase
    vec2 = vecB - vecBase
    
    cross = vec1 ^ vec2
    
    norm = cross.normalize()
    
    final  = vecBase + norm.scalar_dynamic(scaleV)
    final.connect_to('%s.t'%target)
    return target.as_list()
    
    '''name = 'test'
    base = pm.PyNode('loc_base')
    loc1 = 'loc1'
    loc2 = 'loc2'
    target = 'loc_target'
    distance = 'scal'
    crossVector(name, base, loc1, loc2, target, 22)'''




# def vecViz(vector, tfm, name="vectorPoint"):
#     '''
#     Crates cone represenatation of vector based from tfm point
#
#     Args:
#         vector:
#         tfm:
#         name:
#
#     Returns:
#
#     '''
#     """Visual aid for Vectors"""
#     _logger.debug('vector is %s'%vector)
#     vec = pm.dt.Vector(vector[0], vector[1], vector[2])
#     _logger.debug('tfm is %s'%tfm)
#     grp = pm.group(em=True)
#     loc = pm.spaceLocator()
#
#     #cone for visulization
#     pointer = pm.cone(name=name,esw=360,ch=1,d=1,hr=20,ut=0,ssw=0,s=3,r=0.25,tol=0.01,nsp=1,ax=(1, 0, 0))[0]
#     #pivot of cone is in center. for nicer look we shift it 2.5 to start right at the target. We have to move it in direction of the vector
#     #so we get normalized vector (1 in lenth) and multiply it by 2.2
#     vecNorm = vec.normal()
#     pointer.translate.set(vecNorm *(2.5,2.5,2.5))
#
#     #put locator and cone into group
#     loc.setParent(grp)
#     pointer.setParent(grp)
#
#     #move locator to vector and cone to tfm
#     loc.setTranslation(vec)
#     pointer.setTranslation(tfm)
#
#     #aim constrain cone to look at locator
#     pm.delete(pm.aimConstraint(loc,pointer,aimVector=(1,0,0)))
#
#
#
#     #move cone to target position and clean up
#     pm.delete(pm.pointConstraint(tfm,grp,mo=False))
#     pointer.setParent(world=True)
#     pm.delete(grp)

def vecVizPoint(startPoint, endPoint, name="vecViz"):
    '''
    Crates cone represenatation of vector between start and endpoint

    Args:
        vector:
        tfm:
        name:

    Returns:

    '''
    """Visual aid for Vectors"""

    startVec = om.MVector(startPoint[0], startPoint[1], startPoint[2])
    endVec = om.MVector(endPoint[0], endPoint[1], endPoint[2])
    vec = endVec - startVec

    _logger.debug('vec length is %s'%vec.length())


    grp = pm.group(em=True)
    loc = pm.spaceLocator()

    #cone for visulization
    height = vec.length()
    #pivot of cone is in center. for nicer look we shift it to base
    pointer = pm.polyCone(name=name, sx=4, r=0.25, h=height)[0]
    pm.xform(pointer,  piv=(0,(-1*height/2),0), t=(0,(height/2),0),ro=(0,0,-90), os=1)
    pm.makeIdentity(pointer, a=1)


    #move locator to vector and cone to tfm
    loc.setTranslation(endPoint)
    pointer.setTranslation(startPoint)

    #aim constrain cone to look at locator
    pm.delete(pm.aimConstraint(loc,pointer,aimVector=(1,0,0), mo=0))

    # clean up
    pm.delete(loc)

    return pointer

def vecViz(vector, startTranform=[0,0,0], name="vecViz"):
    '''
    Crates cone represenatation of vector between start and endpoint

    Args:
        vector:
        tfm:
        name:

    Returns:

    '''
    """Visual aid for Vectors"""
    startPoint = om.MVector(startTranform[0], startTranform[1], startTranform[2])
    endPoint = vector
    vec = vector


    loc = pm.spaceLocator(n=name)

    #cone for visulization
    height = vec.length()
    #pivot of cone is in center. for nicer look we shift it to base
    pointer = pm.polyCone(name=name+'_pointer', sx=4, r=0.25, h=height)[0]
    pm.xform(pointer,  piv=(0,(-1*height/2),0), t=(0,(height/2),0),ro=(0,0,-90), os=1)
    pm.makeIdentity(pointer, a=1)


    #move locator to vector and cone to tfm
    loc.setTranslation(endPoint)


    #aim constrain cone to look at locator
    pm.delete(pm.aimConstraint(loc,pointer,aimVector=(1,0,0), mo=0))

    # clean up
    pm.parent(loc,pointer)
    pointer.setTranslation(startPoint)

    return pointer

def vectorInfo(startPos, endPos):
    '''
    Print vector infos

    '''
    ''' vectors from startPos, endPos '''
    startVec = om.MVector(startPos[0], startPos[1], startPos[2])
    endVec = om.MVector(endPos[0], endPos[1], endPos[2])

    ''' vector between start and end '''
    vec = endVec - startVec

    ''' Length between start and end
    sqrt(x*x + y*y + z*z)'''
    # print 'Vector Lenght is %s ' % vec.length()
    print 'Length:  %s ' % math.sqrt(vec.x*vec.x + vec.y*vec.y + vec.z*vec.z)

    ''' DOT product '''
    # dot = startVec.length() * endVec.length() * math.cos(startVec.angle(endVec))
    # dot = startVec.x*endVec.x + startVec.y*endVec.y + startVec.z*endVec.z
    dot = startVec*endVec
    print 'Dot: %s ' % dot

    ''' Normalized  - Unit vector
    we can get unit vector by dividing vector with its length '''
    # print startVec.normal().x
    unitVec = vec / vec.length()
    print  'Unit Vector: (%s, %s, %s)'%(unitVec.x, unitVec.y, unitVec.z)

    ''' angle between start and endVector
    v1*v2 / v1.length()*v2.length()
    see from above that v1/v1.length is the unit vector, so basically create the dot procuct'''
    # print math.acos((startVec*endVec) / (startVec.length()*endVec.length())) * 180 / math.pi
    print 'Angle between : %s'%math.degrees(startVec.angle(endVec))



def solveTriangle(a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    print 'test'

    # no angle known
    if (alpha==None) and (beta==None) and (gamma==None):
        print 'no angle known'
        if (a==None) or (b==None) or (c==None):
            return 'Cannot solve without all three sides known'
        # angle alpha
        alpha = math.degrees(math.acos((c*c+b*b-a*a) / (2*b*c)))

        # solve remaining
        beta = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * b))
        gamma = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * c))
        print alpha + beta + gamma
        print 'alpha is %s. beta is %s. gamma is %s'%(alpha, beta, gamma)
        return {'a': a, 'b': b, 'c': c, 'alpha': alpha, 'beta': beta, 'gamma': gamma}

    # two sides and one angel known - law of sine
    elif (a!=None) and (b!=None) and (gamma!=None):
        c = math.sqrt(math.pow(a,2)+math.pow(b,2)-2*a*b*math.cos(math.radians(gamma)))
    elif (b!=None) and (c!=None) and (alpha!=None):
        a = math.sqrt(math.pow(b,2)+math.pow(c,2)-2*b*c*math.cos(math.radians(alpha)))
    elif (a!=None) and (c!=None) and (beta!=None):
        b = math.sqrt(math.pow(a,2)+math.pow(c,2)-2*a*c*math.cos(math.radians(beta)))

    # solve remaining. law of sines
    print 'solving for side with law of sine'
    for i in range(3):
        if (a!=None) and (alpha!=None):
            print 'a and alpha known'
            if (beta!=None):
                if (b==None):
                    b = math.sin(math.radians(beta))/math.sin(math.radians(alpha)) * a
                if (gamma==None): gamma  = 180 - alpha - beta

            if (beta == None) and (b!=None): beta = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * b))

            if (gamma!=None):
                if (c==None):
                    c = math.sin(math.radians(gamma))/math.sin(math.radians(alpha)) * a
                if (beta==None):beta  = 180 - alpha - gamma

            if (gamma==None) and (c!=None): gamma = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * c))

        if (b!=None) and (beta!=None):
            print 'b and beta known'
            if (alpha!=None):
                if (a==None):a = math.sin(math.radians(alpha))/math.sin(math.radians(beta)) * b
                if (gamma==None): gamma  = 180 - alpha - beta

            if alpha == None and (a!=None): alpha = math.degrees(math.asin(math.sin(math.radians(beta)) / b * a))

            if (gamma!=None):
                if (c==None): c = math.sin(math.radians(gamma))/math.sin(math.radians(beta)) * b
                if (alpha==None): alpha  = 180 - beta - gamma

            if gamma == None and (c!=None): gamma = math.degrees(math.asin(math.sin(math.radians(beta)) / b * c))

        if (c!=None) and (gamma!=None):
            print 'c and gamma known'
            print {'a': a, 'b': b, 'c': c, 'alpha': alpha, 'beta': beta, 'gamma': gamma}
            if (alpha!=None):
                if (a==None):
                    print 'calculating a'
                    a = math.sin(math.radians(alpha))/math.sin(math.radians(gamma)) * c
                if (beta==None): beta  = 180 - alpha - gamma

            if alpha == None and (a!=None): alpha = math.degrees(math.asin(math.sin(math.radians(gamma)) / c * a))

            if (beta!=None):
                if (b==None):
                    print 'calculating b'
                    b = math.sin(math.radians(beta))/math.sin(math.radians(gamma)) * c
                if (alpha==None): alpha  = 180 - beta - gamma

            if (beta == None) and (b!=None): beta = math.degrees(math.asin(math.sin(math.radians(gamma)) / c * b))

    print 'solving for angle with law of sine'
    print {'a': a, 'b': b, 'c': c, 'alpha': alpha, 'beta': beta, 'gamma': gamma}
    # solving for angle with law of sine
    if beta == None:
        beta = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * b))
    if gamma == None:
        gamma = math.degrees(math.asin(math.sin(math.radians(alpha)) / a * c))
    if alpha == None:
        alpha = math.degrees(math.asin(math.sin(math.radians(beta)) / b * a))


    return {'a': a, 'b': b, 'c': c, 'alpha': alpha, 'beta': beta, 'gamma': gamma}





