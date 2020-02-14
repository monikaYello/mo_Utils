import pymel.core as pm
# import riggTool.lib.libName as libName
# import riggTool.lib.libValues as libValues
# reload(libValues)
import pymel.core.datatypes as dt


def applyShader(name, obj, color=(.5,.5,.5), sType='lambert', sSet='__none__'):
    """easy way to apply shaders into a mesh
    A =applyShader('templateShader', obj, color=(1,0,0), sType='surfaceShader', sSet='__none__')
    """
    ##print 'evaluating'
    if sSet=='__none__':
        sSet=name+'SG'
        ##print 'no SG set given'

    if pm.objExists(name)==0 and pm.objExists(sSet)==0:
        ##print 'creating shader'
        myShader=pm.shadingNode(sType, asShader=1, name=name)
        pm.sets(n=sSet, renderable=1, empty=1, noSurfaceShader=1)
        if sType=='surfaceShader':
            myAt='.outColor'
        else:
            myAt='.color'
        pm.connectAttr(myShader+myAt, sSet+'.surfaceShader')
        pm.setAttr(myShader+myAt, color)
    pm.sets(sSet, fe=obj)
    return name

####################
#ATTACH TO CURVE
######################
def attatchToCrv(crv, objArray=None, dv=0):
    if objArray is None:objArray = pm.ls(sl=1)
    crvInfo=[]
    for obj in objArray:
        basename=libName.simpleName(obj)+'CrvInfo'
        poc = pm.createNode('pointOnCurveInfo', n=basename+'_poc')
        poc.attr('turnOnPercentage').set(1)
        pm.connectAttr(crv.getShape()+".worldSpace", poc+".inputCurve", f=1)
        pm.connectAttr(poc+".position", obj+".translate", f=1)
        crvInfo.append(poc)
    return crvInfo

####################
# MAKE COLOR GRADIENT
######################
def makeColorGradient(objArray=None, descriptor=None, mul=1.5, center=0.4, phase1=2, phase2=4, phase3=6):
    width=1
    if objArray is None:objArray=pm.ls(sl=1)

    import math
    n=len(objArray)

    frequency1=1/float(n)*math.pi*2*mul
    frequency2=1/float(n)*math.pi*2*mul
    frequency3=1/float(n)*math.pi*2*mul

    for i in range(0, n):
        num='%003d'%i
        red = math.sin(frequency1*i + phase1) * width + center
        grn = math.sin(frequency2*i + phase2) * width + center
        blu = math.sin(frequency3*i + phase3) * width + center

        if descriptor is None:
            shader=objArray[i].split('_')[1]+'_shader'
            shaderSet=objArray[i].split('_')[1]+'_shaderSG'
        else:
            shader=descriptor+num+'_shader'
            shaderSet=descriptor+num+'_shaderSG'

        if pm.objExists(shader)==0:
            pm.shadingNode('lambert', asShader=1, name=shader)
            pm.setAttr(shader+'.color', (red,grn,blu))
        if pm.objExists(shaderSet)==0:
            pm.sets(n=shaderSet, renderable=1, empty=1, noSurfaceShader=1)

        pm.connectAttr(shader+'.outColor', shaderSet+'.surfaceShader', f=1)

        pm.sets(shaderSet, fe=objArray[i])


#############################################################
#create softMod
#import softModRig;
#softModRig.SoftModMaker()
#created for management of arrays. split in 2 halfs, 3 parts, or 1 to many
#type could be any number but 1 wounbd be 1 to everything and -1 would be everything against the last
#type can be ['segmented', 0], ['correlative', 1]
# libUtil.arraySplit(pm.ls(sl=1), 3, 'segmented')
# NOTE: returns a dictionary
# Result: {
# 0: [nt.Transform(u'pCube1'),
#     nt.Transform(u'pCube2'),
#     nt.Transform(u'pCube3')],
# 1: [nt.Transform(u'pSphere1'),
#     nt.Transform(u'pSphere2'),
#     nt.Transform(u'pSphere3')],
# 2: [nt.Transform(u'nurbsPlane1'),
#     nt.Transform(u'nurbsPlane2'),
#     nt.Transform(u'nurbsPlane3')]} #
#############################################################
def arraySplit(myArray, num=2, typeArray='segmented'):
    grps={}

    if num ==0:
        grps[0]=myArray
        return grps
    if len(myArray)%num!=0:
        print 'ERROR array cannot by divided in '+str(num)+ 'grps!!!!'
        return
    elif num==1:
        grps[1]=[]
        for obj in myArray[1:]:
            grps[0].append(obj)
        grps[0]=myArray[0]
    elif num==-1:
        grps[0]=myArray[-1]
        grps[1]=[]
        for obj in myArray[1:]:
            grps[1].append(obj)
    elif typeArray in ['segmented', 0]:
        for i in range(0, num):
            grps[i]=[]
            for x in range(    len(myArray)/num*i , len(myArray)/num*(i+1)   ):
                grps[i].append(myArray[x])
    elif typeArray in ['correlative', 1]:
        for i in range(0, num):
            grps[i]=[]
        i=0
        for x in myArray:
            grps[i].append(x)
            if i!=num-1:
                i=i+1
            else:
                i=0
    return grps


#############################################################
# averageNode  select obj that u want to do averageNOde and run averageNode
# averageNode(['A','B','C']
# return {$grp, $grpFollow, $grpBind ,$grpHalf, $mul}
#############################################################

def averageNode(sel=None):
    # select  object for averageRotate
    if sel==None:
        sel = pm.ls(sl =1)
    node=[]
    for obj in sel:

        pm.select(obj)
        names=libName.getName()
        grp=pm.group(em=1,n=(names[0] + "_" + names[1] + names[2] + "_aveGrp"))
        grpFollow=(names[0] + "_" + names[1] + names[2] + "_follow")
        grpBind=(names[0] + "_" + names[1] + names[2] + "_bindPose")
        grpHalf=(names[0] + "_" + names[1] + names[2] + "_half")
        #get rotate order
        rotOrder=pm.getAttr(obj + ".rotateOrder")
        # create locator
        pm.spaceLocator(p=(0, 0, 0),n=grpFollow)
        pm.spaceLocator(p=(0, 0, 0),n=grpBind)
        pm.spaceLocator(p=(0, 0, 0),n=grpHalf)
        # set rotate order
        pm.setAttr(grp + ".rotateOrder",rotOrder)
        pm.setAttr(grpFollow + ".rotateOrder",rotOrder)
        pm.setAttr(grpBind + ".rotateOrder",rotOrder)
        pm.setAttr(grpHalf + ".rotateOrder",rotOrder)
        pm.parent(grpFollow,grpBind,grpHalf,grp)
        pm.delete(pm.orientConstraint(sel[0],grp))
        pm.orientConstraint(sel[0],grpFollow)
        oriCon= pm.orientConstraint(grpFollow,grpBind,grpHalf)
        # set to shortest mode
        pm.setAttr((oriCon + ".interpType"),2)
        mul=pm.createNode('multiplyDivide',n=(names[0] + "_" + names[1] + names[2] + "_mdn"))
        pm.connectAttr((grpHalf + ".rx"),(mul + ".input1X"),f=1)
        pm.connectAttr((grpHalf + ".ry"),(mul + ".input1Y"),f=1)
        pm.connectAttr((grpHalf + ".rz"),(mul + ".input1Z"),f=1)
        pm.setAttr((mul + ".input2X"),2)
        pm.setAttr((mul + ".input2Y"),2)
        pm.setAttr((mul + ".input2Z"),2)
        # hide averageGrp
        pm.setAttr((grp + ".v"),0)
        node.append([grp,grpFollow,grpBind,grpHalf,mul])
    return node
# end of averageNode



#############################################################
#add extra 2 node on top of select obj
#list = pm.ls(sl=1)
#A = addNode('temp','parent',['obj'])
#B = addNode('temp','parent',list)
#B = addNode('temp')
# type = 'parent' , 'child'
# return in list
#############################################################
def addNode (name,typeCnx='parent',sel=None):
    if sel==None:
        sel = pm.ls(sl =1)
    listNode = []
    for obj in sel:
        rotOrder = pm.getAttr (obj+'.rotateOrder')
        node = pm.group (em =1,n= obj+name)
        pm.setAttr ( node+'.rotateOrder', rotOrder)
        pm.delete (pm.pointConstraint (obj , node))
        pm.delete (pm.orientConstraint (obj , node))
        if typeCnx=='parent'or typeCnx =='upper'or typeCnx =='up':
            # list parent
            listParent = pm.listRelatives(obj, p=1)
            #if parent == 1, do this one or if parent == 0, do nothing
            if listParent:
                pm.parent( node, listParent[0])
                #freeze transform first
                pm.makeIdentity(node, apply=True, t=1, r=1, s=1)
            pm.parent ( obj , node )
        if typeCnx=='child' or typeCnx=='below'or typeCnx =='dn':
            # list all children in obj
            listChild = pm.listRelatives(obj, c=1,type='transform')
            #pm.parent(listChild[0],node)
            pm.parent(node,obj)
            if not len(listChild)==0:
                pm.parent(listChild,node)
        pm.select ( node)
        listNode.append(node)
    return listNode



def averageTrigger(objAttrList, name):
    """use to create a trigger between several notes """

    for obj in [name+'_aveTrigger', name+'_setRange']:
        if pm.objExists(obj):
            pm.delete(obj)
            print 'warning previous %s deleted'%(obj)

    if pm.objExists(name)==0:
        loc=pm.spaceLocator(n=name)

        cleanUpAttr(sel=[loc],listAttr =['tx','ty','tz','rx','ry','rz','sx','sy','sz', 'v'],l=1,k=0,cb=0)
        pm.addAttr(loc, ln='mul', k=1, dv=1)
        pm.addAttr(loc, ln='user', k=1, dv=0, min=0, max=3)
        pm.addAttr(loc, ln='finalOutput', k=0)
        pm.setAttr(loc+'.finalOutput', cb=1)



    else:
        loc=pm.PyNode(name)

    ave=pm.createNode('plusMinusAverage', name=name+'_aveTrigger')
    ave.attr('operation').set(1)
    i=0
    for objAttr in objAttrList:
        pm.connectAttr(objAttr, '%s.input1D[%1d]'%(ave, i), f=1)
        i=i+1
    pm.connectAttr(loc+'.user', '%s.input1D[%1d]'%(ave, i), f=1)

    sr=pm.createNode('setRange', n=name+'_setRange')
    pm.connectAttr(loc+'.mul', sr+'.maxX', f=1)
    sr.attr('oldMaxX').set(1)
    pm.connectAttr(ave+'.output1D', sr+'.valueX', f=1)
    pm.connectAttr(sr+'.outValueX', loc+'.finalOutput', f=1)

def boolSeparate(objArray=None, removeObjs=1):
    '''last obj will be the cube'''
    if objArray is None:
        objArray=pm.ls(sl=1)
    objs=objArray[:-1]
    cube=objArray[-1]

    returnList = []
    for obj in objs:
        dupA=pm.duplicate(obj)[0]
        dupB=pm.duplicate(obj)[0]
        cutCubeA=pm.duplicate(cube)[0]
        cutCubeB=pm.duplicate(cube)[0]

        newA=pm.polyCBoolOp( dupA, cutCubeA, op=2, n=obj+'A' , ch=0, classification=2)[0]
        newB=pm.polyCBoolOp( dupB, cutCubeB, op=3, n=obj+'B' , ch=0, classification=2)[0]
        print newA, newB

        movePivot(sel=[ obj, newA])
        movePivot(sel=[ obj, newB])

        local=pm.listRelatives(obj, p=1)
        if len(local)!=0:
            pm.parent(newA, newB, local)

        returnList.append( [newA, newB] )

    if removeObjs==1:
        pm.delete(objs)

    return returnList

def createNode(type, name):
    if pm.objExists(name)==1:
        pm.delete(name)
    return pm.createNode(type, name)


#############################################################
#libUtil.cleanUpAttr(sel=[obj],listAttr=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radi'],l=0,k=1,cb=1)
#libUtil.cleanUpAttr(sel=[obj],listAttr=['radi'],l=0,k=0,cb=0)
#libUtil.cleanUpAttr(sel=[obj],listAttr=['sx','sy','sz'],l=1,k=0,cb=0)
#libUtil.cleanUpAttr(sel=[obj],listAttr=['v'],l=0,k=0,cb=0)
#############################################################
def cleanUpAttr(sel=None,listAttr =['sx','sy','sz','v'],l=1,k=1,cb=0):
    #l = 1 lock attr , l=0 unlock attr
    #k =1  show attr ,k= 0 hide attr
    #cb = 1 nonkeyable ,cb =0 make atte keyable
    if sel==None:
        sel =pm.ls(sl=1)
    for obj in sel:
        #make pynode
        obj = pm.PyNode(obj)
        for attr in listAttr:
            if pm.objExists(obj+'.'+attr):
                obj.attr(attr).set(l=l,k=k,cb=cb)

def cleanTransforms(objArray = None):
    if objArray is None:
        objArray = pm.selected()

    for obj in objArray:
        try:
            pm.cutKey(obj)
        except:
            pass
    deleteChildrenConstraints(objArray)

def connectScaleX(objArray=None):
    if objArray == None:
        objArray=pm.ls(sl=1)

    for obj in objArray:
        pm.connectAttr('%s.sx'%obj, '%s.sy'%obj)
        pm.connectAttr('%s.sx'%obj, '%s.sz'%obj)

    cleanUpAttr(sel=objArray,listAttr =['sy','sz'],l=1,k=1,cb=0)


#############################################################
# select crv
# return list of cluster nodes and transfrom nodes
#list = pm.ls(sl=1)
#clusterOnCrv('temp',list)
#clusterOnCrv('temp')

#############################################################

def clusterOnCrv(name=None,sel=None):
    # select curve first
    if sel is None:
        sel=pm.ls(sl=1)
    listClus=[]

    for x in sel:
        for i in range(0, x.getShape().numCVs()):
            pm.select(x.getShape().cv[i])
            if name is None:
                listClus.append(pm.cluster())
            else:
                A = pm.cluster()
                num = '%02d'%(i+1)
                B = pm.rename(A[1], name+str(num)+'_clusCtrl')
                cluster = pm.listConnections(B.getShape(), type='cluster')[0]
                listClus.append([cluster,B])
                #for cluster in B:
                    #cluster.attr('relative').set(1)

    return listClus


def convertSeltoStrArray(objArray=None, stripNS=0, sort=0):
    if objArray is None:
        objArray=pm.ls(sl=1)
    objArrayClean=[]

    if stripNS==0:
        for obj in objArray:
            objArrayClean.append(str(obj))
    elif stripNS==1:
        for obj in objArray:
            objArrayClean.append(str(obj.split(':')[-1]))
    elif stripNS==2:
        for obj in objArray:
            objArrayClean.append(str(obj.split(':')[-1].rsplit('_', 1)[0]))
    elif stripNS==3:
        for obj in objArray:
            objArrayClean.append(str(obj.split(':')[-1].split('_')[1]))
    elif stripNS==4:
        for obj in objArray:
            objArrayClean.append(obj.replace( obj[0], '%'+'s')+'%side')

    if sort==1:
        objArrayClean.sort()

    print objArrayClean
    return objArrayClean


def compareLists(objArray=None):
    if objArray is None:objArray=pm.ls(sl=1)
    D={}
    for a in pm.listRelatives(objArray[0], t=1, c=1):
        D['listA'].append(pm.PyNode(a))
    for b in pm.listRelatives(objArray[1], t=1, c=1):
        D['listB'].append(pm.PyNode(b))


    D['listA'].sort()
    D['listB'].sort()
    checkList=[]
    for a in D['listA']:
        if a in D['listB']:
            print '%s >>> OK'%(a)
        else:
            print '%s >>> DOESNT EXIST INSIDE OBJ %s'%(a)


#############################################################
#creates Curve from Transform objArray
#############################################################
def curveFromObj(name='curve', objArray=None, curvature=1, rebuild=False):
    allCoo=[]
    if objArray is None:
        objArray=pm.ls(sl=1)
    for x in objArray:
        coo=pm.xform(x, ws=True, rp=True, q=True)
        allCoo.append(coo)
    myCrv=pm.curve(n=name, d=curvature, p=allCoo)
    if rebuild is True:
        pm.rebuildCurve(myCrv, ch=0, rpo=1, rt=0, end=0 ,kr=0, kcp=1, kep=1, kt=1,s=0, d=curvature, tol=0.01)
    return myCrv



#############################################################
#creates nonlinear deformer with proper naming
#############################################################
def createNonlinearDeformer(obj=None, type='bend', name = 'myName', connectAttr=False):
    if obj == None:
        obj = pm.selected()
    bendDef, bendTrans=pm.nonLinear(obj, name='%s_%sDef'%(name, type), type=type, before=True)
    bendTrans = pm.rename(bendTrans, name)
    bendDef = pm.rename(bendDef, '%s_%s'%(name, type))

    if connectAttr is True:

        attrs = pm.PyNode(bendDef).listAttr(k=1, s=1, r=1, w=1, c=1)
        for a in attrs:
            # skip anything with weight
            if 'weight' in a.name():
                continue

            # add attr to ctrl
            try:
                pm.addAttr(bendTrans, longName=a.longName(), shortName=a.shortName(), at=a.type(), k=1)
                newa = pm.PyNode('%s.%s'%(bendTrans, a.longName()))

                # set to default values of deformer
                pm.setAttr('%s.%s'%(bendTrans, a.longName()), a.get())

                min, max = a.getSoftRange()

                if min is not None:
                    newa.setSoftMin(min)
                if max is not None:
                    newa.setSoftMax(max)

                minR, maxR = a.getRange()

                if minR is not None:
                    newa.setMin(minR)
                if maxR is not None:
                    newa.setMax(maxR)




            except:
                pass
            # connect def to ctrl
            pm.connectAttr('%s.%s'%(bendTrans, a.longName()), a)


    return bendDef, bendTrans



#############################################################
# #
#############################################################
def createNormalPlane(objArray=None, name='normalPlane'):
    print 'creating Normal Plane'
    if objArray is None:
        objArray=pm.ls(sl=1)

    myCoo=[]
    for obj in objArray:
        myCoo.append(pm.PyNode(obj).getTranslation(space='world'))

    maxD=libValues.getAverageDistance(myCoo=myCoo)*1.25

    #---#creates the plane
    normalPlane = pm.polyPlane(n=name, w=1, h=1, sx=1, sy=1, ax=[0,1,0], ch=0)[0]

    for obj in objArray:
        con=pm.pointConstraint(obj, normalPlane, mo=0)
    pm.delete(con)


    smpN=libValues.getNormal(myCoo, worldNormal='y')
    pm.delete(  pm.aimConstraint(objArray[-1], normalPlane, aimVector=[1,0,0], upVector=[0,1,0], mo=0, worldUpVector=smpN  )  )

    pm.PyNode(normalPlane).attr('scale').set([maxD,maxD,maxD])


def createDynamicConstraint(sel=None,typeCnx='orientConstraint',ctrl = None):
    #create orientConstraint (for fk) or parent constraint (for ik) make ctrl stay orient to location that you select
    # select control that to you want first then pick node that you want to oriented
    if sel==None:
        sel = pm.ls(sl=1)
    if ctrl ==None:
        ctrl = sel[0]
    names =libName.getName(sel[0])
    cap = pm.util.capitalize(names[2])
    part = names[3]+cap
    side = names[0]
    #add node
    oriCONS = addNode('ORICONS','parent',[sel[0]])[0]
    P = oriCONS.getParent()
    locOri = []
    attrName = []
    for o in sel:
        objName =libName.getName(o)
        if len(objName)<2:name = objName[0]
        else:name = objName[1]
        loc =pm.spaceLocator(n = side+'_'+part+'_parentTo'+name+'Loc')
        snap(ctrl,loc)
        locOri.append(loc)
        attrName.append('parentTo'+name)
    #addAttr to ctrl
    pm.addAttr(ctrl,ln = ('parentTo'),en = "-----------------:",at = "enum")
    pm.setAttr(ctrl + ".parentTo",k = 1,e = 1,l = 1,cb=1)
    for i  in range (0,len(locOri)):
        pm.addAttr(ctrl,ln = attrName[i],dv = 0,max = 1,min = 0,at = 'double',k=1)
        if typeCnx == 'orientConstraint':
            con = pm.orientConstraint(locOri[i],oriCONS,mo=1,w=1)
        if typeCnx =='parentConstraint':
            con = pm.parentConstraint(locOri[i],oriCONS,mo=1,w=1)
        wt = 'W'+str(i)
        con.attr('interpType').set(2) # set to shortest
        pm.connectAttr(ctrl+'.'+attrName[i],con+'.'+locOri[i]+wt,f=1)
        #parentlocator
        if i ==0: # parent to node above oriCONS
            pm.parent(locOri[i],P)
        else:
            pm.parent(locOri[i],sel[i])
        #lock and hide those locator
        locOri[i].attr('v').set(0)
        cleanUpAttr([locOri[i]],['tx','ty','tz','rx','ry','rz','sx','sy','sz'],l=1,k=1,cb=0)


def createFollowCrv(name='followCrv', objArray=None, curvature=3, grp='followCrvGrp', rebuild=False):
    if objArray is None:
        objArray=pm.ls(sl=1)
    crv=curveFromObj(name=name, objArray=objArray, curvature=curvature, rebuild=rebuild)
    cls=clusterOnCrv(name=name+'_cluster',sel=[crv])
    clTr=[]
    for cl, obj in zip(cls, objArray):
        pm.parentConstraint(obj, cl[1], mo=0)
        cl[1].attr('visibility').set(0)
        grpIn(grp, cl[1])
        clTr.append(cl[1])
    grpIn(grp, crv)
    return [crv, clTr]

def createEpCurve(name='curve', objArray=None, curvature=3):
    allCoo=[]
    if objArray is None:
        objArray=pm.ls(sl=1)
    for x in objArray:
        coo=pm.xform(x, ws=True, rp=True, q=True)
        allCoo.append(coo)
    myCrv=pm.curve(n=name, d=curvature, p=allCoo)
    myCrv=pm.fitBspline(myCrv, ch=0, tol=0.01)[0]
    print myCrv

    return myCrv

def createCrvFromMesh(objArray=None):
    if objArray is None:
        objArray=pm.ls(sl=1)

    coos=[]
    for obj in objArray:
        objShp=obj.getShape()
        if objShp.type()=='mesh':
            for i in range(0, objShp.numVertices()):
                coo=objShp.getPoint(i, space='world')
                coos.append( coo )
            myCrv=pm.curve(n=obj+'Crv', d=1, p=coos)

def createNode(type, name, f=1):
    if pm.objExists(name) and f==1:
        pm.delete(name)
    return pm.createNode(type, n=name)

def createPlaceHolder(objArray=None, cnx=0, grpLoc='locatorGrp', setObj='objSet'):
    '''
    import mo_Utils.libUtil as libUtil
    reload(libUtil)
    libUtil.createPlaceHolder()
    :param objArray:
    :param cnx:
    :param grpLoc:
    :param setObj:
    :return:
    '''
    targetMemory='targetMemory'

    if objArray is None:
        objArray=pm.ls(sl=1)
    for x in objArray:
        N=x.name()+'_loc'

        if pm.objExists(N):
            print 'deleteing %s'%N
            pm.delete(N)

        l=pm.spaceLocator(n=N)
        cons=[]

        if x.attr('tx').isLocked()==0 and x.attr('ty').isLocked()==0 and x.attr('tz').isLocked()==0 and x.attr('rx').isLocked()==0 and x.attr('ry').isLocked()==0 and x.attr('rz').isLocked()==0:
            cons.append(pm.parentConstraint(x, l, mo=0))
        elif x.attr('tx').isLocked()==0 and x.attr('ty').isLocked()==0 and x.attr('tz').isLocked()==0:
            cons.append(pm.pointConstraint(x, l, mo=0))
        elif x.attr('rx').isLocked()==0 and x.attr('ry').isLocked()==0 and x.attr('rz').isLocked()==0:
            cons.append(pm.orientConstraint(x, l, mo=0))

        if cnx==0:
            pm.delete(cons)
        elif cnx==1:
            for c in cons:
                setIn('placeHolderConstraints', c)
        elif cnx==2:
            pm.delete(cons)

            if x.attr('tx').isLocked()==0 and x.attr('ty').isLocked()==0 and x.attr('tz').isLocked()==0 and x.attr('rx').isLocked()==0 and x.attr('ry').isLocked()==0 and x.attr('rz').isLocked()==0:
                pm.parentConstraint(l, x, mo=0)
            elif x.attr('tx').isLocked()==0 and x.attr('ty').isLocked()==0 and x.attr('tz').isLocked()==0:
                pm.pointConstraint(l, x, mo=0)
            elif x.attr('rx').isLocked()==0 and x.attr('ry').isLocked()==0 and x.attr('rz').isLocked()==0:
                pm.orientConstraint(l, x, mo=0)

        pm.addAttr(l, ln=targetMemory, dt='string')
        pm.setAttr(l+'.'+targetMemory, str(x))
        pm.setAttr(l+'.'+targetMemory, l=1)

        grpIn(grpLoc, l)
        setIn(setObj, x)


def reconnectAllPlaceholder():
    locs = pm.listRelatives('locatorGrp', children=1)

    ctrls = []
    for l in locs:
        pm.parentConstraint(l, l.replace('_loc', ''), mo=0)

def reconnectPlaceholder():

    locs = pm.selected()

    ctrls = []
    for l in locs:
        ctrl=l.replace('_loc', '')
        deleteChildrenConstraints([ctrl])
        pm.cutKey(ctrl, at=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'])
        pm.parentConstraint(l, l.replace('_loc', ''), mo=0)

    '''
    import mo_Utils.libUtil as libUtil
    reload(libUtil)
    libUtil.createPlaceHolder(objArray=None, cnx=0, grpLoc='locatorGrp', setObj='objSet')
    
    libUtil.selectPlacholderConnected()
    
    libUtil.reconnectPlaceholder()
    
    '''
def selectPlacholderConnected():
    locs = pm.listRelatives('locatorGrp', children=1)

    ctrls = []
    for l in locs:
        ctrls.append(l.replace('_loc', ''))
    pm.select(ctrls)



def cleanMesh(objArray=None):
    objArray=pm.ls(sl=1)
    """exports the each mesh that was selected as obj and brings it back"""
    if objArray is None:objArray=pm.ls(sl=1)
    p = str(pm.sceneName().splitpath()[0] / 'tmpObj.obj')
    print p
    for obj in objArray:
        name=obj.shortName()
        dad=pm.listRelatives(obj, p=1)
        print 'cleaning %s'%name
        dup=pm.duplicate(obj, name='tempMesh')[0]
        pm.parent(dup, w=1)
        pm.select(dup)

        pm.exportSelected(p, type= 'OBJexport', force=1)
        pm.delete(dup)

        pm.importFile(p)
        pm.parent('tempMesh', dad)
        pm.delete(obj)
        pm.rename('tempMesh', name)

def createWorlds(worldArray, objArray=None):
    """Creates transform node that"""
    if objArray is None:objArray=pm.ls(sl=1)

    worldReturn=[]
    for obj in objArray:
        worldNulls=[]
        for world in worldArray:
            basename=obj.name()
            null=pm.createNode('transform', n=basename+pm.util.capitalize(world))
            snap(obj, null)
            worldNulls.append(null)
            if pm.objExists(obj+'.'+world)==0:
                pm.addAttr(obj, ln=world, at='double', k=1, min=0, max=1, dv=0)

        con=pm.parentConstraint(worldNulls, obj, name=basename+'_constraintWorld')
        worldReturn.append(worldNulls)

        i=0
        for world in worldArray:
            pm.connectAttr(obj+'.'+world, con+'.'+basename+pm.util.capitalize(world)+'W'+str(i))
            i=i+1

        if len(worldArray) == 2:
            reverseNode=pm.shadingNode('reverse', asUtility=1, n=basename+'World_reverse')
            pm.connectAttr(obj+'.'+worldArray[0], reverseNode+'.inputX')
            pm.connectAttr(reverseNode+'.outputX', obj+'.'+worldArray[1])
            pm.setAttr(obj+'.'+worldArray[1], l=1)
    return worldReturn


#############################################################
# #creat wrap deformer
#############################################################
def createWrapDeformer(influence=None, surface=None,**kwargs):
    """w = createWrap(selected[0],selected[1], exclusiveBind=1)
    returns [wrapDeformerNode, wrapBaseNode]"""
    if surface == None or influence == None:
        sel = pm.ls(sl=1)
        if len(sel) < 2:
            print 'Error. Need to select at least 2 objects to perform wrap'
            return False
    if surface == None:
        influence= pm.ls(sl=1)[0]
    if influence == None:
        influence = pm.ls(sl=1)[1]

    shapes = pm.listRelatives(influence,shapes=True)
    influenceShape = shapes[0]

    shapes = pm.listRelatives(surface,shapes=True)
    surfaceShape = shapes[0]

    #create wrap deformer
    weightThreshold = kwargs.get('weightThreshold',0.0)
    maxDistance = kwargs.get('maxDistance',1.0)
    exclusiveBind = kwargs.get('exclusiveBind',False)
    autoWeightThreshold = kwargs.get('autoWeightThreshold',True)
    falloffMode = kwargs.get('falloffMode',0)

    wrapData = pm.deformer(surface, type='wrap')
    wrapNode = wrapData[0]

    pm.setAttr(wrapNode+'.weightThreshold',weightThreshold)
    pm.setAttr(wrapNode+'.maxDistance',maxDistance)
    pm.setAttr(wrapNode+'.exclusiveBind',exclusiveBind)
    pm.setAttr(wrapNode+'.autoWeightThreshold',autoWeightThreshold)
    pm.setAttr(wrapNode+'.falloffMode',falloffMode)

    pm.connectAttr(surface+'.worldMatrix[0]',wrapNode+'.geomMatrix')

    #add influence
    duplicateData = pm.duplicate(influence,name=influence+'Base')
    base = duplicateData[0]
    shapes = pm.listRelatives(base,shapes=True)
    baseShape = shapes[0]
    pm.hide(base)

    #create dropoff attr if it doesn't exist
    if not pm.attributeQuery('dropoff',n=influence,exists=True):
        pm.addAttr( influence, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=20.0  )
        pm.setAttr( influence+'.dr', k=True )

    #if type mesh
    if pm.nodeType(influenceShape) == 'mesh':
        #create smoothness attr if it doesn't exist
        if not pm.attributeQuery('smoothness',n=influence,exists=True):
            pm.addAttr( influence, sn='smt', ln='smoothness', dv=0.0, min=0.0  )
            pm.setAttr( influence+'.smt', k=True )

        #create the inflType attr if it doesn't exist
        if not pm.attributeQuery('inflType',n=influence,exists=True):
            pm.addAttr( influence, at='short', sn='ift', ln='inflType', dv=2, min=1, max=2  )

        pm.connectAttr(influenceShape+'.worldMesh',wrapNode+'.driverPoints[0]')
        pm.connectAttr(baseShape+'.worldMesh',wrapNode+'.basePoints[0]')
        pm.connectAttr(influence+'.inflType',wrapNode+'.inflType[0]')
        pm.connectAttr(influence+'.smoothness',wrapNode+'.smoothness[0]')

    #if type nurbsCurve or nurbsSurface
    if pm.nodeType(influenceShape) == 'nurbsCurve' or pm.nodeType(influenceShape) == 'nurbsSurface':
        #create the wrapSamples attr if it doesn't exist
        if not pm.attributeQuery('wrapSamples',n=influence,exists=True):
            pm.addAttr( influence, at='short', sn='wsm', ln='wrapSamples', dv=10, min=1  )
            pm.setAttr( influence+'.wsm', k=True )

        pm.connectAttr(influenceShape+'.ws',wrapNode+'.driverPoints[0]')
        pm.connectAttr(baseShape+'.ws',wrapNode+'.basePoints[0]')
        pm.connectAttr(influence+'.wsm',wrapNode+'.nurbsSamples[0]')

    pm.connectAttr(influence+'.dropoff',wrapNode+'.dropoff[0]')

    return [wrapNode, baseShape]




#############################################################
# #delete all custom attr
#############################################################
def deleteATTR(sel=None):
    """
    clean up all attr
    """
    if sel == None:
        sel = pm.ls(sl=1)
    for obj in sel:
        #remove customAttr with keyable
        attrs = pm.listAttr(obj,k=1)
        listAttrs =  ['visibility','translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
        for A in attrs:
            if A not in listAttrs:
                pm.setAttr(obj+'.'+A,l=0)
                pm.delete(obj+'.'+A,icn=1)
                pm.deleteAttr(obj, at = A)
        #remove customAttr with Nonkeyable
        attrs = pm.listAttr(obj,cb=1)
        listAttrs =  ['visibility','translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
        for A in attrs:
            if A not in listAttrs:
                pm.setAttr(obj+'.'+A,l=0)
                pm.delete(obj+'.'+A,icn=1)
                pm.deleteAttr(obj, at = A)
#############################################################
def deleteChildrenConstraints(objArray=None):
    """deletes the constraints that are children from a specific transform node.meant to clean up a bunch of constraints that are stuck in the outliner"""
    if objArray is None:objArray=pm.ls(sl=1)

    cleanObjs=[]
    for obj in objArray:
        obj=pm.PyNode(obj)
        if obj.type() in ['joint', 'transform', 'camera']:
            cleanObjs.append(obj)

    deleted=[]
    for obj in cleanObjs:
        for ch in pm.listRelatives(obj, c=1):
            if ch.type() in ['parentConstraint', 'pointConstraint', 'orientConstraint', 'aimConstraint', 'scaleConstraint', 'geometryConstraint']:
                try:
                    pm.delete(ch)
                    deleted.append( str(ch) )
                    print '%s >> deleting %s'%(obj, ch)
                except:
                    pass
    for d in deleted:
        print d

#############################################################
# #Delete Unnecessary 'Orig' Nodes
#############################################################
def duplicateClean(obj=None, name=None):
    """
     use for duplicate deformed mesh and and auto delete meshOrig
    """
    #Delete Unnecessary 'Orig' Nodes
    import fnmatch
    #duplicate obj
    if obj is None:
        obj = pm.ls(sl=1)[0]
    if name ==None:name = None
    dup = pm.duplicate(obj, n = name)[0]
    cleanUpAttr(sel=[dup],listAttr=['tx','ty','tz','rx','ry','rz','sx','sy','sz'],l=0,k=1,cb=0)
    nodes = pm.ls(dup,dag=1)
    for obj in nodes:
        if fnmatch.fnmatch(obj.name(),'*Orig*'):
            if len(pm.listConnections(obj))==0:
                pm.delete( obj)
                print 'delete unused node "' +obj+'" from this scene'
    return dup
#############################################################
#directConnect(t=1,r=1,s=0)
#directConnect(['locator1','locator2'],t=1,r=1,s=0)
# connect from sel[0] >> sel[1]
#############################################################
def directConnect(sel=None,t=1,r=1,s=0,rx=0,ry=0,rz=0):
    if sel == None:
        sel = pm.ls(sl=1)
    if not isinstance(sel[0], pm.PyNode):
        sel[0] = pm.PyNode(sel[0])
    if not isinstance(sel[1], pm.PyNode):
        sel[1] = pm.PyNode(sel[1])
    # connect translation
    if t==1: pm.connectAttr(sel[0].t ,sel[1].t,f=1)
    if r==1: pm.connectAttr(sel[0].r ,sel[1].r,f=1)
    if s==1: pm.connectAttr(sel[0].s ,sel[1].s,f=1)
    # connect rotation
    if rx==1: pm.connectAttr(sel[0].rx ,sel[1].rx,f=1)
    if ry==1: pm.connectAttr(sel[0].ry ,sel[1].ry,f=1)
    if rz==1: pm.connectAttr(sel[0].rz ,sel[1].rz,f=1)

#############################################################
#Creates constraint for the middle objects on an array of objs it sets the con Weights for teh objects t
#be equidistant form the ends
#############################################################
def distributeConstraintWeights(start, end, objArray=None, typeCnx='parentConstraint', mo=0, interpType=1):
    if objArray == None:
        objArray = pm.ls(sl=1)

    WA = len(objArray)
    WB = 1
    cons = []

    for obj in objArray:
        if typeCnx =='parentConstraint':
            con=pm.parentConstraint(start, end, obj, mo=mo)
        elif typeCnx=='pointConstraint':
            con=pm.pointConstraint(start, end, obj, mo=mo)
        elif typeCnx=='orientConstraint':
            con=pm.orientConstraint(start, end, obj, mo=mo)
        elif typeCnx=='scaleConstraint':
            con=pm.scaleConstraint(start, end, obj, mo=mo)
        con.attr(start+'W0').set(WA)
        con.attr(end+'W1').set(WB)
        if typeCnx != 'pointConstraint':
            con.attr('interpType').set(interpType)
        WA=WA-1
        WB=WB+1

        cons.append(con)

    return cons


def distributeBlendWeights(start, end, at, objArray=None):
    if objArray == None:objArray = pm.ls(sl=1)
    startAttr='%s.%s'%(start, at)
    endAttr='%s.%s'%(end, at)
    WA=len(objArray)
    WB=1
    i=1
    max=float(len(objArray)+1)
    for obj in objArray:
        bl=pm.createNode('blendTwoAttr', n=obj+'_blnd')
        pm.connectAttr(startAttr, '%s.input[0]'%bl, f=1)
        pm.connectAttr(endAttr, '%s.input[1]'%bl, f=1)
        pm.connectAttr('%s.output'%bl, '%s.%s'%(obj, at), f=1)
        pm.setAttr('%s.attributesBlender'%bl, float(i)/max)
        i=i+1
        ############################################
# toggle jntAxis display
#############################################################
def displayJntAxis(jntArray=None):
    if jntArray is None:jntArray=pm.ls(sl=1, type='joint')
    for x in jntArray:
        if pm.getAttr(x+'.displayLocalAxis')==1:
            pm.setAttr(x+'.displayLocalAxis', 0)
        else:
            pm.setAttr(x+'.displayLocalAxis', 1)
#############################################################
# dynamicParent
#############################################################

def dynamicParent(sel=None):
    """# select ctrl first
    #then select all targets to parentConstrain
    """
    if sel==None:
        sel=pm.ls(sl=1)
    obj=pm.PyNode(sel[0])
    num=len(sel)
    namesAUTO=libName.getName(obj)
    cap=pm.util.capitalize(namesAUTO[2])
    objAUTO=(namesAUTO[0] + "_" + namesAUTO[3] + cap + "_AUTO")
    pm.select(objAUTO)
    parentNames=[]
    if namesAUTO[3] == "arm" or namesAUTO[0] == "LFrt" or namesAUTO[0] == "RFrt" or namesAUTO[1] == "armLo" and num == 6:
        parentNames=["head","chest","main","hip","direction"]
    if namesAUTO[3] == "arm" and num == 3:
        parentNames=["main","arm"]
    if namesAUTO[3] == "leg" or namesAUTO[3] == "legFrnt" or namesAUTO[3] == "legMid" or namesAUTO[3] == "legBack" and num == 3:
        parentNames=["main","hip","direction"]
    if namesAUTO[3] == "leg" and num == 3:
        parentNames=["main","leg","foot"]
    else:
        parentNames = list(sel)
        parentNames.remove(parentNames[0])
    pm.addAttr(obj,ln="parentTo",en="--------------:",at="enum")
    pm.setAttr((obj + ".parentTo"),k=1,e=1,l=1,cb=1)
    for i in range(1,num):
        t=i - 1
        m=str(t)
        if namesAUTO[2] == "pvecCtrl":
            m=str(t+1)
        loc=(obj + "_parentTo" + parentNames[t]+'Loc')
        pm.spaceLocator(p=(0, 0, 0),n=loc)
        pm.setAttr(loc + ".v",0)
        pm.delete(pm.pointConstraint(obj,loc))
        pm.parent(loc,sel[i])
        if parentNames[t] == "leg":
            pm.delete(pm.pointConstraint((namesAUTO[0] + "_leg01_ctrlJnt"),loc))
            pm.parent(loc,("C_direction_ctrl"))
            pm.orientConstraint(sel[2],loc,sk=['x', 'z'],w=1,offset=(0, 0, 0))
        parantCon=pm.parentConstraint(loc,objAUTO,mo=1,weight=1)
        pm.setAttr(parantCon+'.interpType', 2) #setup to shortest
        pm.addAttr(obj,ln=(parentNames[t]),max=1,dv=0,at='double',min=0,k=1)
        pm.connectAttr(obj + "." + parentNames[t],parantCon + "." + loc + "W" + m,f=1)
#########################################################################
def dynamicParentPvec(obj = '',sel=None):
    """# select ctrl first
    #then select all targets to parentConstrain
    """
    if sel==None:
        sel=pm.ls(sl=1)
    obj=pm.PyNode(obj)
    num=len(sel)
    namesAUTO=libName.getName(obj)
    cap=pm.util.capitalize(namesAUTO[2])
    objAUTO=(namesAUTO[0] + "_" + namesAUTO[3] + cap + "_AUTO")
    #pm.select(objAUTO)
    #delete constraint
    pm.delete(objAUTO,cn=1)
    parentNames = sel
    pm.addAttr(obj,ln="parentTo",en="--------------:",at="enum")
    pm.setAttr((obj + ".parentTo"),k=1,e=1,l=1,cb=1)
    for i in range(0,num):
        loc=(obj + "_parentTo" + parentNames[i]+'Loc')
        loc = pm.spaceLocator(n=loc)
        pm.setAttr(loc + ".v",0)
        print loc
        pm.delete(pm.pointConstraint(obj,loc))
        pm.parent(loc,sel[i])
        parantCon=pm.parentConstraint(loc,objAUTO,mo=1,weight=1)
        pm.setAttr(parantCon+'.interpType', 2) #setup to shortest
        #print obj + "." + parentNames[i]
        pm.addAttr(obj,ln=(parentNames[i]),max=1,dv=0,at='double',min=0,k=1)
        pm.connectAttr(obj + "." + parentNames[i],parantCon + "." + loc + "W" + str(i),f=1)
        #print parantCon + "." + loc + "W" + str(i)
    # set default
    pm.setAttr(obj + "." + parentNames[0],1)

#############################################################
#list = pm.ls(sl=1)
# A = dupAndRenameJnt('feathJnt',list)
# B = dupAndRenameJnt('feathJnt',['A','B'])
#############################################################
def dupAndRenameJnt(newSuffix,sel=None):
    """
    return list
    """
    if sel == None:
        sel=pm.ls(sl=1)
    newJnts = []
    for o in sel:
        newJnt=pm.duplicate(o)[0]
        newJnts.append(newJnt)
        selNewJnt=pm.ls(newJnt,dag=1)
        for subItem in selNewJnt:
            #sideName, nodeType = subItem.rsplit("_", 1)
            sideName= subItem.rsplit("_", 1)[0]
            subItem.rename(sideName + '_' + newSuffix)
        pm.select(newJnt)
        #addsuffix "End" to lastJnt
        jnts = getJntArray()
        num=len(jnts)
        pm.select (jnts[num-1])
        libName.addSuffix ("End")
        #print newJnt
    return newJnts
#############################################################
#
#############################################################
def dupAndRenameChildren(obj=None):
    """Get any hierchy of obj and renames it with unique name using 3 tokens if possible
    example:
    -C_obj01_grp
    +-C_child03_geo
    +-+C_childB

    Result
    -C_obj02_grp
    +-C_child04_geo
    +-+C_childB01

    """
    if obj == None:
        obj=pm.ls(sl=1)[0]

    nameArray=libName.nameSplit(obj)

    if len(nameArray[-1])!=1:
        nameArray[-1][1]=nameArray[-1][1]+'%02d'
    else:
        nameArray[-1][1]=nameArray[-1][0]+'%02d'

    newname=libName.numberedName(libName.nameRevertOriginal(nameArray), suffix=False, prefix=False)
    dup=pm.duplicate(obj, n=newname)[0]
    print '>> duplicating as %s'%(newname)

    for c in pm.listRelatives(dup,ad=1):
        if c.type() not in ['mesh']:
            nameArray=libName.nameSplit(c.shortName().split('|')[-1])

            if len(nameArray[-1])!=1:
                nameArray[-1][1]=nameArray[-1][1]+'%02d'
            else:
                nameArray[-1][1]=nameArray[-1][0]+'%02d'

            newname=libName.numberedName(libName.nameRevertOriginal(nameArray), suffix=False, prefix=False)
            pm.rename(c, newname)
            print newname
    return dup
#############################################################
#
#############################################################
def dupAndRenameDetail(detail,obj=None):
    """change  detail name and keep suffix the same
    if detail = 'leg'
    L_arm01_ctrlJnt >> L_leg01_ctrlJnt
    return newJnt
    """
    if obj == None:
        obj=pm.ls(sl=1)[0]
    sideName =libName.getName(obj)[0]
    detailNoNumber =libName.getName(obj)[3]
    nodeType =libName.getName(obj)[2]
    newJnt=pm.duplicate(obj)[0]
    selNewJnt=pm.ls(newJnt,dag=1)
    for i in xrange(len(selNewJnt)):
        num=selNewJnt[i].rsplit(detailNoNumber)[1].rsplit('_')[0]
        selNewJnt[i].rename(sideName + '_'+detail+num +'_'+ nodeType)
        #delete unused constraint
        if selNewJnt[i].nodeType() == 'parentConstraint' or selNewJnt[i].nodeType() == 'pointConstraint' or selNewJnt[i].nodeType() == 'orientConstraint' or selNewJnt[i].nodeType() == 'aimConstraint':
            pm.delete(selNewJnt[i])
    #addsuffix "End" to lastJnt
    jnts = getJntArray(newJnt)
    num=len(jnts)
    pm.select (jnts[num-1])
    libName.addSuffix ("End")
    return newJnt

def dupBS(BS, obj):
    BS=pm.PyNode(BS)
    obj=pm.PyNode(obj)
    numWeights=BS.numWeights()
    i=0
    for attr in BS.weight:
        w=attr.getAlias()
    #         if i>100:
    #             return

        BS.attr('envelope').set(0)

        BS.attr(w).set(1)
        BS.attr('envelope').set(1)

        dup=pm.duplicate(obj, n=w)[0]
        dup.attr('v').set(0)
        BS.attr('envelope').set(0)
        BS.attr('envelope').set(1)
        BS.attr(w).set(0)
        i=i+1


def findCenterByComponent():
    pm.mel.PolySelectConvert(3)
    vtxs = pm.selected(sl=1, flatten=1)

    for vtx in vtxs:
        x,y,z = vtx.getPosition(space='world')
        if vtx == vtxs[0]:
            xMin, yMin, zMin = [x,y,z]
            xMax, yMax, zMax = [x,y,z]
        else:
            if x > xMax:
                xMax = x
            if y > yMax:
                yMax = y
            if z > zMax:
                zMax = z
            if x < xMin:
                xMin = x
            if y < yMin:
                yMin = y
            if z < zMin:
                zMin = z

    return [(xMax+xMin)/2 , (yMax+yMin)/2, (zMax+zMin)/2]

def findShellVtxs(mesh):
    pm.select(mesh)
    numberOfShells = pm.polyEvaluate(pm.selected()[0],  shell=1)
    pm.mel.PolySelectConvert(3)
    vtxs = pm.selected(sl=1, flatten=1)

    shellList = []
    for i in range(0, numberOfShells):
        pm.select(vtxs[0])
        pm.mel.eval('ConvertSelectionToShell;')
        shellVtxs = pm.selected(sl=1, flatten=1)
        shellList.append( shellVtxs )
        for x in shellVtxs:
            vtxs.remove(x)

    print 'number of shells: %s. '%numberOfShells
    print 'returning shells: %s. '%len(shellList)

    return shellList




def createJntByShell(mesh, skin=1):
    bn = "%s"%mesh
    numberOfShells = pm.polyEvaluate(mesh,  shell=1)
    jnts = []
    i=1
    shells = findShellVtxs(mesh)

    for shell in shells:
        for vtx in shell:
            x,y,z = vtx.getPosition(space='world')
            if vtx == shell[0]:
                xMin, yMin, zMin = [x,y,z]
                xMax, yMax, zMax = [x,y,z]
            else:
                if x > xMax:
                    xMax = x
                if y > yMax:
                    yMax = y
                if z > zMax:
                    zMax = z
                if x < xMin:
                    xMin = x
                if y < yMin:
                    yMin = y
                if z < zMin:
                    zMin = z

        pos = [(xMax+xMin)/2 , (yMax+yMin)/2, (zMax+zMin)/2]
        pm.select(cl=1)
        jnt = pm.joint(n ='%s%02d_skinJnt'%(bn, i) )
        jnt.translate.set(pos)
        jnts.append(jnt)

        grpIn('%s_jntGrp'%bn, jnt)
        i = i + 1
    if skin == 1:
        pm.select(jnts, mesh)
        skinCluster = pm.skinCluster(tsb=1, n='%s_skinCluster'%mesh)

        for shell, jnt in zip(shells, jnts):
            for vtx in shell:
                pm.skinPercent(skinCluster, vtx, transformValue=[ [jnt, 1] ], normalize=1)


def createJntForLatticeComponent():
    latticePnts = pm.ls(sl=1, flatten=1)
    for x in latticePnts:
        pm.select(x)
        c = pm.cluster()

        jnt = pm.joint(n='%s_%sjnt' % (x.split('.')[0], x.split('.')[1]))
        snap(c[1], jnt)
        pm.parent(jnt, w=1)
        pm.delete(c)

def skinJntByShell(mesh, jnts):
    bn = "%s"%mesh
    numberOfShells = pm.polyEvaluate(mesh,  shell=1)

    shells = findShellVtxs(mesh)
    centers = []

    for shell in shells:
        for vtx in shell:
            x,y,z = vtx.getPosition(space='world')
            if vtx == shell[0]:
                xMin, yMin, zMin = [x,y,z]
                xMax, yMax, zMax = [x,y,z]
            else:
                if x > xMax:
                    xMax = x
                if y > yMax:
                    yMax = y
                if z > zMax:
                    zMax = z
                if x < xMin:
                    xMin = x
                if y < yMin:
                    yMin = y
                if z < zMin:
                    zMin = z

        pos = dt.Vector( (xMax+xMin)/2 , (yMax+yMin)/2, (zMax+zMin)/2 )
        centers.append( [pos, shell] )

    pm.select(jnts, mesh)
    skinCluster = pm.skinCluster(tsb=1, n='%s_skinCluster'%mesh)

    for jnt in jnts:
        x, y, z = pm.xform (jnt,q=1,ws =1,t=1)
        v1 = dt.Vector( x, y, z )

        minD = 100
        for x in centers:
            v2, shell = x
            d = (v1-v2).length()

            if d < minD:
                minD = d
                shellClosest = shell

        for vtx in shellClosest:
            pm.skinPercent(skinCluster, vtx, transformValue=[ [jnt, 1.0] ], normalize=1)


#############################################################
# cNEEDED for locOnCrvEpsilon()
#############################################################
def findParamDistanceEpsilon(smpCurve, smpArcLD, smpDistance, smpEpsilon):
    u=0.0
    smpMin=pm.getAttr(smpCurve+'.minValue')
    smpMax=pm.getAttr(smpCurve+'.maxValue')
    pm.setAttr(smpArcLD+'.uParamValue', smpMax)
    myArcLength=pm.getAttr(smpArcLD+'.arcLength')
    #start and end of the curve you dont need to calculate
    if smpDistance <=0.0:
        return 0.0
    if smpDistance >=myArcLength:
        return smpMax
    #THIS CALCULATES THE MIDDLE ONES
    smpPass=1
    while(1):
        u=(smpMin+smpMax)/2.0
        pm.setAttr(smpArcLD+'.uParamValue', u)
        myArcLength=pm.getAttr(smpArcLD+'.arcLength')
        if abs(myArcLength-smpDistance)<smpEpsilon:
            break
        if myArcLength>smpDistance:
            smpMax=u
        else:
            smpMin=u
        smpPass=smpPass+1
    return u
#############################################################
# flood skin weight.
# if arg/selection is transform node it floods mesh with weight of a random vertex
# if vertex is selected is floods mesh with it's weight
#############################################################
def floodSkinWeights(mesh = None):
    import random as rand

    if mesh == None:
        mesh = pm.ls(sl=1)[0]
    if isinstance(mesh, pm.nodetypes.Transform):
        #select random vertex
        objShape = mesh.getShape()
        randVertex = rand.randint(1,objShape.numVertices())
        pm.select('%s.vtx[%s]'%(mesh, randVertex))
        print ('Mesh was selected. Copy weight of vertext %s to all vertices'%randVertex)

    elif isinstance(mesh, pm.MeshVertex) == False:
        return False

    pm.mel.eval('artAttrSkinWeightCopy;')
    pm.mel.eval('ConvertSelectionToShell;')
    pm.mel.eval('artAttrSkinWeightPaste;')

    pm.select(mesh)
    return mesh


#############################################################
#add extra 2 node on top of select obj
#############################################################
def groupCtrl (sel=None):
    """
    A = groupCtrl (['pSphere1','pCube1'])[0]
    return list of [grpZERO,grpAUTO, grpObj]
    """
    if sel==None:
        sel = pm.ls(sl =1)
    listGrp = []
    for obj in sel:
        rotOrder = pm.getAttr (obj+'.rotateOrder')
        names = obj.split('_')

        if len(names) > 3:
            auto = obj.replace( names[-1],  '%s_AUTO'%( pm.util.capitalize( names[-1] ) ) )
            zero = obj.replace( names[-1],  '%s_ZERO'%( pm.util.capitalize( names[-1] ) ) )

        elif len(names)==3:
            cap = pm.util.capitalize( names[2] )
            auto = names[0]+'_'+names[1]+cap+'_AUTO'
            zero = names[0]+'_'+names[1]+cap+'_ZERO'

        elif len(names)<=2:
            auto = obj+'_AUTO'
            zero = obj+'_ZERO'

        auto = pm.group (em=1, n=auto )
        pm.setAttr ( auto+'.rotateOrder', rotOrder)

        zero = pm.group (em=1, n=zero )
        pm.setAttr (zero+'.rotateOrder', rotOrder)
        # create  attr Mem
        if pm.objExists(obj+'.AUTO')==0:
            pm.addAttr (obj,ln ='AUTO', dt ='string')

        pm.setAttr (obj+'.AUTO' ,auto ,k=0, l=0, type ='string')

        if pm.objExists(obj+'.ZERO')==0:
            pm.addAttr (obj,ln ='ZERO', dt ='string')

        pm.setAttr (obj+'.ZERO' ,zero ,k=0, l=0, type ='string')
        # ZERO obj
        pm.addAttr (zero,ln ='obj', dt ='string')
        pm.setAttr (zero+'.obj' ,obj ,k=0, l=0, type ='string')
        # AUTO obj
        pm.addAttr (auto,ln ='obj', dt ='string')
        pm.setAttr (auto+'.obj' ,obj ,k=0, l=0, type ='string')
        #check parent of selectObj
        listParent = pm.listRelatives (obj ,p=1,typ='transform')
        #if num==0, do nothing or if num==1 do parent
        if len(listParent)==1 :
            #print 'yes'
            pm.parent (zero , listParent[0] )
        # match positionand rotation
        pm.delete (pm.pointConstraint ( obj , auto))
        pm.delete (pm.orientConstraint ( obj , auto))
        pm.delete (pm.pointConstraint ( obj , zero))
        pm.delete (pm.orientConstraint ( obj , zero))
        pm.parent ( auto , zero)
        pm.parent ( obj , auto )
        # set nonKeyAble
        grp = [zero , auto , obj]
        listGrp.append(grp)
        #print grp
    return listGrp

#############################################################
#makes creates and adds objects to a grp
# libU.grpIn('myGrp', 'objA')
#############################################################
def grpIn(grpName, obj):
    if pm.objExists(grpName):
        grp=grpName
    else:
        grp=pm.createNode( 'transform', n=grpName )

    if len(pm.listRelatives(obj, p=1))!=0:
        if pm.listRelatives(obj, p=1)[0]!=grpName:
            pm.parent(obj, grp)
    else:
        pm.parent(obj, grp)
#############################################################
#
#############################################################
def grpJnt(jnt=None):
    """ use for group top jnt
    """
    if jnt==None:
        jnt=pm.ls(sl=1)[0]
    jnt = pm.PyNode(jnt)
    rotOrder = pm.getAttr (jnt+'.rotateOrder')
    names=libName.getName(jnt)
    grpZERO= pm.group(em=1,n=names[0] + "_" + names[3] + "JntGrp_ZERO")
    grpAUTO= pm.group(em=1,n=names[0] + "_" + names[3] + "JntGrp_AUTO")
    # create  attr Mem
    if pm.objExists(jnt+'.AUTO')==0:
        pm.addAttr (jnt,ln ='AUTO', dt ='string')
    pm.setAttr (jnt+'.AUTO' ,grpAUTO ,k=0, l=0, type ='string')
    if pm.objExists(jnt+'.ZERO')==0:
        pm.addAttr (jnt,ln ='ZERO', dt ='string')
    pm.setAttr (jnt+'.ZERO' ,grpZERO ,k=0, l=0, type ='string')
    # ZERO obj
    pm.addAttr (grpZERO,ln ='obj', dt ='string')
    pm.setAttr (grpZERO+'.obj' ,jnt ,k=0, l=0, type ='string')
    # AUTO obj
    pm.addAttr (grpAUTO,ln ='obj', dt ='string')
    pm.setAttr (grpAUTO+'.obj' ,jnt ,k=0, l=0, type ='string')
    pm.setAttr (grpZERO+'.rotateOrder', rotOrder)
    pm.setAttr (grpAUTO+'.rotateOrder', rotOrder)
    snap(jnt,grpZERO,'parent')
    snap(jnt,grpAUTO,'parent')
    pm.parent(grpAUTO,grpZERO)
    pm.parent(jnt,grpAUTO)
    grp=[grpZERO,grpAUTO,jnt]
    return grp

def getAnimFrameRange(objArray=None):
    if objArray is None:
        objArray = pm.ls(sl=1)
    myFrames=pm.keyframe(objArray, tc=1, q=1)
    if myFrames == []: # no keyframes
        return [0,0]
    myFrames.sort()
    print [myFrames[0], myFrames[-1]]
    return [myFrames[0], myFrames[-1]]


#############################################################
#A = getTopChain()
#B = getTopChain('joint2')
#############################################################
def getTopChain(obj=None):
    if obj == None:
        obj=pm.ls(sl=1)[0]
    pm.select(obj)
    num =1
    while num !=0:
        sel=pm.ls(sl=1)
        jnt=pm.listRelatives(sel[0],ap=1)
        num=len(jnt)
        if num == 1:
            pm.select(jnt[0])
    topNode =pm.ls(sl=1)[0]
    return topNode

#############################################################
# get all joints in that hirarchy and return
#A = getJntArray()
#B = getJntArray('C_root_jnt')
#############################################################
def getJntArray (obj=None):
    if obj==None:
        obj = pm.ls(sl =1)[0]
    obj = pm.PyNode(obj)
    allJnts= []
    jnts = pm.listRelatives (obj, ad =1, typ = "joint")
    allJnts.extend(jnts)
    # add topJnt in list
    allJnts.append(obj)
    # reverse list
    allJnts.reverse()
    return allJnts

#############################################################
# getDictance by select two objects
#E = getDist(['pPlane1','pSphere1'])
#D = getDist()
#############################################################
def getDist (sel=None):
    if sel == None:
        sel=pm.ls(sl=1)
    posOne=sel[0]
    posTwo=sel[1]
    # group
    grp1 = pm.group (em=1, n = posOne+'TempGrp')
    grp2 = pm.group (em=1, n = posTwo+'TempGrp')
    pm.delete (pm.pointConstraint (posOne ,grp1,offset= (0, 0, 0),w =1))
    pm.delete (pm.orientConstraint(posOne ,grp1,offset= (0, 0, 0),w =1))
    pm.delete (pm.pointConstraint (posTwo ,grp2,offset= (0, 0, 0),w =1))
    pm.delete (pm.orientConstraint(posTwo ,grp2,offset= (0, 0, 0),w =1))
    #pos1 = pm.xform (grp1,q=1,ws =1,t=1)
    #pos2 = pm.xform (grp2,q=1,ws =1,t=1)
    v1 = grp1.attr('t').get()
    v2 = grp2.attr('t').get()
    # assign to vector
    #v1 = pm.dt.Vector(pos1)
    #v2 = pm.dt.Vector(pos2)
    #print repr(v1)
    #print repr(v2)
    v3 = v1-v2
    dis = v3.length()
    pm.delete (grp1, grp2)
    return dis


def getClosest(anchor, objArray, minDistance = None):
    if minDistance is None:
        D=getDist(sel=[anchor, objArray[0]])
        closest=objArray[0]
    else:
        D=minDistance
        closest = None

    for obj in objArray[1:]:
        d=getDist(sel=[anchor, obj])
        if d<D:
            D=d
            closest=obj
#        print '%s: %s: %s'%(anchor, obj, d)
    #print '%s closest to %s: dist:%s'%(closest, anchor, D)
    return closest


def getClosestFacesFromMeshComponent(mesh, objArray=None):
    mesh = pm.PyNode(mesh)
    meshShp=mesh.getShape()

    if objArray is None:
        objArray = pm.selected()

    for obj in objArray:
        objShp = obj.getShape()
        setName = '%s_vtxSet'%obj

        if pm.objExists(setName) == 0:
            pm.select(cl=1)
            pm.sets(n = setName)

        fs=[]
        if objShp.type()=='mesh':
            c=1
            for i in range(0, objShp.numVertices()):
                coo=objShp.getPoint(i, space='world')
                x = meshShp.getClosestPoint(coo, space='world')
                f = pm.PyNode( '%s.f[%s]'%(mesh, x[1]) )

                if f not in fs:
                    fs.append(f)
                    pm.select(f)
                    pm.sets(setName, add=pm.selected())


def getClosestVtxFromMeshComponent(mesh, objArray=None):
    """
    import riggTool.lib.libUtil as libUtil
    reload(libUtil)
    libUtil.getClosestVtxFromMeshComponent(mesh, objArray=None)
    """
    mesh = pm.PyNode(mesh)
    meshShp = mesh.getShape()
    mySets = []

    if objArray is None:
        objArray = pm.selected()

    cPnt=pm.createNode('closestPointOnMesh')
    pm.connectAttr (meshShp+'.outMesh', cPnt+'.inMesh')

    pm.select(cl=1)
    for obj in objArray:
        objShp = obj.getShape()
        setName = '%s_vtxSet'%obj

        if pm.objExists(setName):
            pm.delete(setName)

        pm.sets(n = setName)

        vtxs=[]
        if objShp.type()=='mesh':
            c = 1
            for i in range(0, objShp.numVertices()):
                cPnt.inPosition.set( objShp.getPoint(i, space='world')  )

                myVtx = pm.PyNode( '%s.vtx[%s]'%(mesh, cPnt.closestVertexIndex.get()) )

                if myVtx not in vtxs:
                    vtxs.append(myVtx)

                    pm.select(myVtx)
                    pm.sets(setName, add=pm.selected())

    pm.delete(cPnt)

    pm.select(cl=1)
    pm.select(mySets)
#############################################################
#
#############################################################

def getClosestVtxFromComponentList(startSearchComponent=None, searchComponentList=None):

    '''
    Given an startSearchComponent (vtx) and a vertexList, finds the closest
    vertex in the vertexList to starSearchComponent

    eg.
    componentListObjB = pm.PyNode('pSphere1.vtx[180:199]')
    startSearchComponent = pm.PyNode('pSphere2.vtx[194]')
    :param componentObjA:
    :param componentListObjB:
    :return:
    '''
    import maya.OpenMaya as OpenMaya

    # geo = searchComponentList.node()
    #loc = startSearchComponent

    #print 'geo is %s'%geo
    #print 'startSearchComponent is %s' % startSearchComponent

    pos = pm.ls(startSearchComponent, fl=1)[0].getPosition(space='world')

    #print 'faceVerts is %s' % searchComponentList
    faceVerts = pm.ls(searchComponentList, fl=1)


    closestVert = None
    minLength = None
    #print pm.ls(faceVerts, fl=1)

    for v in faceVerts:
        thisLength = (pos - v.getPosition(space='world')).length()

        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v

    pm.select(closestVert)


    return closestVert


def getPosInbetween(numObjs = 5,locator =1,sel=None):
    """select 2 objs
    locator = 1 create locator and aim to obj
    while select all locs
    return vector position
    """
    if sel==None:
        sel = pm.ls(sl=1)
        if len(sel)<2:
            pm.confirmDialog(message = 'need to select 2 objs',
            button = 'ok',defaultButton = 'Yes',
            title = 'Confirm')
            pm.error('need to select 2 objs')
    a = pm.PyNode(sel[0])
    b = pm.PyNode(sel[1])
    pos=[]
    locs=[]
    for i in xrange(numObjs):
        wt = 1.0 / (numObjs + 1) * (i + 1)
        newPos = wt * a.getTranslation(space='world') + (1 - wt) * b.getTranslation(space='world')
        #create locator
        if locator==1:
            m=i+1
            name = ('loc%02d_loc' % m)
            if pm.objExists(name):
                pm.delete(name)
            loc = pm.spaceLocator( name = name)
            loc.attr('localScale').set([0.2,0.2,0.2])
            loc.setTranslation(newPos, space='world')
            pm.delete(pm.aimConstraint(b,loc,
                offset=(0,0,0) ,w= 1,
                aimVector=(0,1,0),
                upVector= (0,0,1) ,
                worldUpType ="vector" ,
                worldUpVector= (0,1,0)))
            locs.append(loc)
        pos.append(newPos)
    pm.select(locs)
    return pos
#############################################################
# list all hidden objects in that grp
# by selection
#A = getHiddenObj ()
#B = getHiddenObj ('pCube1_ZERO')
#############################################################
def getHiddenObj(grp=None):
    if grp == None:
        grp = pm.ls(sl=1)[0]
    grp = pm.PyNode(grp)
    allChildren = grp.listRelatives(ad=True)
    allHidden = [x for x in allChildren if not x.attr('visibility').get()]
    return allHidden

#############################################################

#############################################################
def listAttrKminusL(obj, k=1, l=1):
    X=set(pm.listAttr(obj, k=k))
    Y=set(pm.listAttr(obj, l=l))
    return list(X-Y)

#############################################################

#############################################################
def jntToDisplay():
    """connect allJnt to DISPLAY
    DISPLAY="DISPLAY"
    # check obj exist
    if pm.objExists(DISPLAY) != 1:
        pm.error("no object call DISPLAY")
    jnt=pm.ls("*_skinJnt*",
            "*_ctrlJnt*",
            "*_*Jnt",
            "*_jnt",
            "*_posJnt",
            "*_hlpJnt",
            "*:*_skinJnt*",
            "*:*_hlpJnt",
            type ='joint')
    for obj in jnt:
        pm.setAttr(DISPLAY + ".skeletonDisplay",0)
        pm.delete(obj + ".overrideDisplayType",icn=1)
        pm.setAttr(obj + ".overrideEnabled",1)
        pm.setAttr(obj + ".overrideDisplayType",0)
        pm.connectAttr(DISPLAY + ".skeletonDisplay",obj + ".overrideDisplayType",f=1)
    """
    DISPLAY="DISPLAY"
    # check obj exist
    if pm.objExists(DISPLAY) != 1:
        pm.error("no object call DISPLAY")
    jnt=pm.ls("*_ikJnt*","*_fkJnt*","*_ctrlJnt*",type ='joint')
    for obj in jnt:

        pm.delete(obj + ".overrideDisplayType",icn=1)
        pm.setAttr(obj + ".overrideEnabled",1)
        pm.setAttr(obj + ".overrideDisplayType",0)
        pm.connectAttr(DISPLAY + ".ctrlJntDisplay",obj + ".overrideDisplayType",f=1)
    pm.setAttr(DISPLAY + ".ctrlJntDisplay",0) # set to normal

    jnt=pm.ls("*_skinJnt*","*:*_skinJnt*",type ='joint')
    for obj in jnt:
        pm.delete(obj + ".overrideDisplayType",icn=1)
        pm.setAttr(obj + ".overrideEnabled",1)
        pm.setAttr(obj + ".overrideDisplayType",0)
        pm.connectAttr(DISPLAY + ".skeletonDisplay",obj + ".overrideDisplayType",f=1)
    pm.setAttr(DISPLAY + ".skeletonDisplay",0) # set to normal


    pm.setAttr(DISPLAY + ".geoDisplay",0) # set to normal
    pm.setAttr(("GEO.overrideEnabled"),1)
    pm.setAttr(("GEO.overrideDisplayType"),0)
    pm.delete(("GEO.overrideDisplayType"),icn=1)
    pm.connectAttr((DISPLAY + ".geoDisplay"),("GEO.overrideDisplayType"),f=1)









#############################################################
# create locator on crv
# obj= 'curve1'
# span =2
# num=12
# name = 'C_mouth'
#############################################################

def locOnCrv (num=2,span=1,obj=None,orientation='yes'):
    m = 1/float(num - 1)
    if obj==None:
        obj = pm.ls(sl=1)[0]
    crv = pm.PyNode(obj)
    crvShape = crv.getShape()

    grp=(obj + 'Grp')
    if pm.objExists(grp) == 0:
        grp = pm.group(em=1,n=grp)
        grp.attr('inheritsTransform').set(0)
    # rebuild curve
    # number span fist
    # auto rebuild curve 10 times for make span evenlly
    if span != 1:
        for i in range(0,10):
            pm.rebuildCurve(crv,rt=0,ch=1,end=1,d=3,kr=0,s=span,kcp=0,tol=0.1,kt=0,rpo=1,kep=1)
    if pm.objExists(crv+'.lenght'):
        pm.deleteAttr ( crv, at = 'lenght')
    # add curve lenght
    pm.addAttr(crv,ln='lenght',dv=1,at='double',min=0,k=1)
    crvInfo=pm.createNode('curveInfo',n=(crv + '_info'))
    pm.connectAttr((crvShape + '.worldSpace[0]'),(crvInfo + '.inputCurve'),f=1)
    # get arclen of crv
    arclen=pm.getAttr(crvInfo + '.arcLength')
    mdn=pm.createNode('multiplyDivide',n=(crv + "_md"))
    # set to divide operation
    pm.setAttr((mdn + '.operation'), 2)
    pm.setAttr((mdn + '.input2X'),arclen)
    pm.connectAttr((crvInfo + '.arcLength'),(mdn + '.input1X'),f=1)
    pm.connectAttr((mdn + '.outputX'),(crv + '.lenght'), f=1)
    locator=[]

    for i in range (0,num):
        padding = '%02d' % (i+1)
        par=('parameter' + padding)
        if pm.objExists(crv+'.'+par):
            pm.deleteAttr ( crv, at = par)
        pm.addAttr(crv,ln=par,dv=0,at='double',min=0,max=1,k=1)
        pm.setAttr(crv + "." + par,m * i, e=1,keyable=True)
        locPosInfo=pm.createNode('pointOnCurveInfo',n=(obj + 'Loc_poCrvInfo'+padding))
        loc=pm.spaceLocator(n=(crv + padding))
        loc.attr('localScaleX').set(0.1)
        loc.attr('localScaleY').set(0.1)
        loc.attr('localScaleZ').set(0.1)
        pm.connectAttr((crvShape + '.worldSpace'),(locPosInfo + '.inputCurve'),f=1)
        pm.connectAttr((locPosInfo + '.position'),(loc + '.translate'), f=1)
        pm.setAttr((locPosInfo + '.turnOnPercentage'),1)
        pm.connectAttr((crv + "." + par),(locPosInfo + '.parameter'),f=1)
        pm.parent(loc,grp)
        locator.append(loc)
        if orientation=='yes':
            pm.orientConstraint(crv,loc,mo=1,w=1)
    pm.select(crv)
    return loc

#############################################################
# create locator on crv NO need for spans information
# smpCrv= 'curve1'
# smpEpsilon = 0.0001 (the lower the number the more accurate)
# smpNumberLoc=12
# smpName = 'C_mouth'
#ch=0 (keep attached)
#############################################################

def locOnCrvEpsilon(smpName, smpCrv, smpNumberLoc=10.0, smpEpsilon=0.0001, ch=0,
                    locSet=None, parameterOnLoc=0, nodeType = 'spaceLocator'):


    smpReturnList=[]

    Shp =pm.listRelatives(smpCrv, s=1)[0]
    crvShape=Shp
    i=1
    f=0.0
    #find the mx U number needed
    smpMaxU=pm.getAttr(smpCrv+'.maxValue')

    #find the overallLength of the selected curve
    smpArcLD=pm.arcLengthDimension(smpCrv+'.u['+str(smpMaxU)+']')
    smpArcLength=pm.getAttr(smpArcLD+'.arcLength')


    #finds the distance for each secion
    smpSpan=smpArcLength/(smpNumberLoc-1.0)

    #how close to the actual point is consider good enough
    #smpEpsilon=0.0001

    for i in range(1,smpNumberLoc+1):
        num='%02d'%i

        locPosInfo = pm.createNode('pointOnCurveInfo', n=smpName+num+'_poc')

        if nodeType == 'spaceLocator':
            locPosTemp=pm.spaceLocator(n=smpName+num+'_locAttch')
        elif nodeType == 'polySphere':
            locPosTemp=pm.polySphere(n=smpName+num+'_locAttch',
                                     r = 1, sx=12, sy=12, ax=[0, 1, 0], cuv=2 , ch=0)[0]

        smpReturnList.append(locPosTemp)

        pm.connectAttr(crvShape+".worldSpace", locPosInfo+".inputCurve", f=1)
        pm.connectAttr(locPosInfo+".position", locPosTemp+".translate", f=1)

        if pm.objExists(smpCrv+".parameter"+num):
            pm.deleteAttr(smpCrv+".parameter"+num)

        #NOTE PARAMETERS ARE NOT EVENLY DISTRIBUTED AS IF YOU DIVIDE 1 you need this procedure
        myParam=findParamDistanceEpsilon(smpCrv, smpArcLD, smpSpan*(i-1), smpEpsilon)

        if parameterOnLoc==0:
            pm.addAttr(smpCrv, ln="parameter"+num, at='double', min=0, max=1, dv=i/smpNumberLoc)
            pm.setAttr(smpCrv+".parameter"+num, e=1, keyable=1)
            pm.connectAttr(smpCrv+".parameter"+num, locPosInfo+".parameter", f=1)
            #Put the correctValue
            pm.setAttr(smpCrv+".parameter"+num, myParam/smpMaxU)
        else:
            pm.addAttr(locPosTemp, ln="parameter", at='double', min=0, max=1, dv=i/smpNumberLoc)
            pm.setAttr(locPosTemp+".parameter", e=1, keyable=1)
            pm.connectAttr(locPosTemp+".parameter", locPosInfo+".parameter", f=1)
            #Put the correctValue
            pm.setAttr(locPosTemp+".parameter", myParam/smpMaxU)

        pm.setAttr (locPosInfo+".turnOnPercentage", 1)

        if ch==0:
            pm.disconnectAttr(  pm.connectionInfo(locPosTemp+".translate" , sourceFromDestination=True)    , locPosTemp+".translate")
            pm.delete(locPosInfo)
            if pm.objExists(smpCrv+".parameter"+num):
                pm.deleteAttr(smpCrv+".parameter"+num)
            if pm.objExists(locPosTemp+".parameter"):
                pm.deleteAttr(locPosTemp+".parameter")

    pm.delete(smpArcLD)
    return smpReturnList


def locBetweenPoints():
    vtxArray=pm.ls(sl=1)
    if len(vtxArray) != 2:
        print 'please select two Points'

    locs=[]

    for vtx in vtxArray:
        print vtx.getPosition()
        loc=pm.spaceLocator()
        loc.attr('t').set(vtx.getPosition())
        locs.append(loc)

    mainLoc=pm.spaceLocator()

    pm.delete( pm.pointConstraint(locs[0], locs[1], mainLoc, mo=0))
    pm.delete( pm.aimConstraint(locs[1], mainLoc, aimVector=[1, 0, 0],
                                upVector=[0, 1, 0],
                                worldUpType='scene'))

    pm.delete(locs)

    pm.select(mainLoc)

#############################################################
#
#############################################################
def listAllCtrls ():
    listCtrls = pm.ls ('*Ctrl',
            '*_MOVER',
            '*_ctrl',
            'DIRECTION',
            'MOVER',
            'PLACER',
            '*_fkIkSwitch')
    makeExportable(listCtrls)
    return listCtrls
#############################################################
#
#############################################################
def makeExportable(sel=None, setName = 'ctrlSet'):
    # make attr for export
    if sel==None:
        sel = pm.ls(sl =1)
    for obj in sel:
        if pm.objExists (obj+'.CTRL'):
            pm.setAttr ( (obj+'.CTRL'), l=0)
            pm.deleteAttr ( obj, at = 'CTRL')
        if pm.objExists (obj+'.xprt'):
            pm.setAttr ( (obj+'.xprt'), l=0)
            pm.deleteAttr ( obj, at = 'xprt')
        pm.addAttr (obj,ln ='CTRL', dt ='string')
        pm.setAttr ( (obj+'.CTRL') ,'yes' ,k=0, l=1, type ='string')
        pm.addAttr (obj,ln ='xprt', dt ='string')
        pm.setAttr ( (obj+'.xprt') ,'yes' ,k=0, l=1, type ='string')
        setIn(setName, obj)

#############################################################
#
#############################################################
def makeReference(objArray=None):
    if objArray is None:objArray=pm.ls(sl=1)
    if objArray[0].getShape().attr('overrideDisplayType').get()==0:
        newOverride=1
        newDisplay=2
    else:
        newOverride=0
        newDisplay=0
    for x in objArray:
        x.getShape().attr('overrideEnabled').set(newOverride)
        x.getShape().attr('overrideDisplayType').set(newDisplay)
#############################################################
#movePivot select target first then object that u want to move second
#movePivot(  ['objADriver','objBDriven']  )
#movePivot()
#############################################################
def movePivot (sel=None):
    if sel == None:
        sel = pm.ls(sl =1)
    scr = sel[0]
    tar = sel[1]
    scale = pm.xform (scr, q=1, ws=1, scalePivot=1)
    rotate = pm.xform (scr, q=1, ws=1, rotatePivot=1)

    pm.xform (tar,ws=1, scalePivot=( scale[0],scale[1], scale[2]) )
    pm.xform (tar,ws=1, rotatePivot=( rotate[0],rotate[1], rotate[2]) )
    pm.select (tar, r=1)

def matchPivot (sel=None, axis='xyz'):
    '''

    :param sel: good pivot first
    :param axis:
    :return:
    '''
    if sel == None:
        sel = pm.ls(sl =1)
    elif isinstance(sel, list):
        sel = [sel]

    scr = sel[0]
    targets = sel[1:]

    for tar in targets:
        srcScale = pm.xform (scr, q=1, ws=1, scalePivot=1)
        srcRotate = pm.xform (scr, q=1, ws=1, rotatePivot=1)
        tarScale = pm.xform (tar, q=1, ws=1, scalePivot=1)
        tarRotate = pm.xform (tar, q=1, ws=1, rotatePivot=1)

        if 'x' in axis: scale, rotate = [srcScale[0], tarScale[1], tarScale[2]], [srcRotate[0], tarRotate[1], tarRotate[2]]
        if 'y' in axis: scale, rotate = [tarScale[0], srcScale[1], tarScale[2]], [tarRotate[0], srcRotate[1], tarRotate[2]]
        if 'z' in axis: scale, rotate = [tarScale[0], tarScale[1], srcScale[2]], [tarRotate[0], tarRotate[1], srcRotate[2]]


        pm.xform (tar,ws=1, scalePivot=( scale[0],scale[1], scale[2]) )
        pm.xform (tar,ws=1, rotatePivot=( rotate[0],rotate[1], rotate[2]) )
        pm.select (tar, r=1)



def moveMyChildrenPivots (sel=None):
    if sel == None:
        sel = pm.ls(sl =1)
    srcChilds = sel[0].listRelatives(children=1)
    tarChilds = sel[1].listRelatives(children=1)
    i=0
    for scr in srcChilds:
        scale = pm.xform (scr, q=1, ws=1, scalePivot=1)
        rotate = pm.xform (scr, q=1, ws=1, rotatePivot=1)
        tar = tarChilds[i]

        pm.xform (tar,ws=1, scalePivot=( scale[0],scale[1], scale[2]) )
        pm.xform (tar,ws=1, rotatePivot=( rotate[0],rotate[1], rotate[2]) )
        pm.select (tar, r=1)
        i=i+1

def movePivotMultiple (sel=None):
    if sel == None:
        sel = pm.ls(sl =1)
    scr = sel[-1]
    for obj in sel[:-1]:
        movePivot (sel=[scr, obj])

def movePivotMinY(sel=None, moveTo='minY'):
    if sel == None:
        sel = pm.selected()
    for obj in sel:
        bb = pm.xform(obj, q=1, ws=1, bb=1)
        piv = obj.getPivots(worldSpace=1)[0]

        if moveTo == 'minX': x, y, z = bb[0], piv.y, piv.z
        elif moveTo == 'maxX': x, y, z = bb[3], piv.y, piv.z
        elif moveTo == 'minY': x, y, z = piv.x, bb[1], piv.z
        elif moveTo == 'maxY': x, y, z = piv.x, bb[4], piv.z
        elif moveTo == 'minZ': x, y, z = piv.x, piv.y, bb[2]
        elif moveTo == 'maxZ': x, y, z = piv.x, piv.y, bb[5]

        pm.xform(obj,pivots=(x, y, z), ws=1)


#############################################################
def movePivotToVtx(vtx=None):
    if vtx == None:
        vtx = pm.ls(sl =1)[0]
    coo = vtx.getPosition(space='world')
    print vtx
    print coo

    t=pm.createNode('transform')
    t.attr('tx').set( coo[0]  )
    t.attr('ty').set( coo[1]  )
    t.attr('tz').set( coo[2]  )

    shp=vtx.split('.vtx')[0]
    obj = pm.listRelatives(shp, p=1)
    movePivot(sel=[ t, obj])
    pm.delete(t)

#############################################################
def moveUVs(objArray=None, u=0, v=1):
    if objArray is None:
        objArray = pm.ls(sl=1)

    for obj in objArray:
        shp = pm.listRelatives(obj, s=1)[0]


        if shp.type() == 'mesh':
            print shp
            pm.polyEditUV(shp+'.map[:]', u=u, v=v)
            print 'moving %s to u=%s   v=%s   '%(shp, u, v)




def makeAimLine(sel=None):
    # first select 2 object that u want to create line
    if sel == None:
        sel=pm.ls(sl=1)
    names=sel[0].split('_')
    name=(names[0] +'_'+names[1])
    # find location of 2 selection
    pos01=pm.xform(sel[0],q=1,ws=1,t=1)
    pos02=pm.xform(sel[1],q=1,ws=1,t=1)
    crv=pm.curve(p=[(pos01[0], pos01[1], pos01[2]), (pos02[0], pos02[1], pos02[2])],k=[0,1],d=1,n=(name + "_crv"))
    # create cluster at pos01
    clus01=pm.cluster((crv + ".cv[0]"),n=(name + "01"))
    # create cluster at pos02
    clus02=pm.cluster((crv + ".cv[1]"),n=(name + "02"))
    # pointConstraint cluster to selected object
    pm.pointConstraint(sel[0],clus01[1])
    pm.pointConstraint(sel[1],clus02[1])
    #create groupNode
    Grp=pm.group(em=1,n=(name + "Aim_crv"))
    pm.parent(clus01[1],clus02[1],crv,Grp)
    #cleanup Attr make it unkeyable only
    cleanUpAttr(sel=[clus01[1],clus02[1],crv,Grp],listAttr=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radi'],l=0,k=1,cb=1)
    # hide cluster
    pm.setAttr((clus01[1] + ".v"),0)
    pm.setAttr((clus02[1] + ".v"),0)
    #set curve to templete
    pm.setAttr((crv + ".template"),1)
    #parent to grp
    if pm.objExists('RIG_NONSCALE'):pm.parent(Grp,'RIG_NONSCALE')
    return Grp
#############################################################
#A = 'L_arm01_ctrlJnt'
#A = makePyNode(A)
# convert node to be PyNode
#############################################################
def makePyNode(obj=None):
    if obj==None:
        obj =pm.ls(sl=1)[0]
    if not isinstance(obj, pm.PyNode):
        obj = pm.PyNode(obj)
    return obj


def mirrorJnts(side = 'L'):
    '''
    import riggTool.lib.libUtil as libUtil
    reload(libUtil)
    libUtil.mirrorJnts()
    '''
    joints = pm.ls(regex =  '%s_.*_skinJnt'%side) + pm.ls(regex =  '%s_.*_skinJntEnd'%side)

    for j in joints:
        print j
        prefix, descriptor, suffix = j.split('_')

        if prefix[0] == 'L':
            mj = 'R_%s_%s'%(descriptor, suffix)

        if prefix[0] == 'R':
            mj = 'L_%s_%s'%(descriptor, suffix)

        if pm.objExists(mj):

            tx, ty, tz = j.attr('translate').get()
            rx, ry, rz = j.attr('rotate').get()
            sx, sy, sz = j.attr('scale').get()

            mj = pm.PyNode(mj)
            try:
                mj.attr('translate').set([tx, -ty, tz])
            except:
                pass

            try:
                mj.attr('rotate').set([-rx, ry, -rz])
            except:
                pass

            try:
                mj.attr('scale').set([sx, sy, sz])
            except:
                pass


def movePivotPointToWorldAxis(objArray=None):
    '''moves teh pivot point to the origing'''
    if objArray==None:
        objArray =pm.ls(sl=1)
    loc=pm.spaceLocator(n='worldCeroLoc')
    for obj in objArray:
        movePivot (sel=[loc, obj])
    pm.delete(loc)
#############################################################
#
#############################################################
def nonKeyableObjs(obj=None):
    """make nonKeyable for entry hirarchy
    select topNode
    """
    if obj==None:
        obj=pm.ls(sl=1)[0]
    #a = pm.listAttr(obj,k=1)
    a = pm.listAnimatable(obj)
    for b in a:
        pm.setAttr(b, cb=1,k=0)
    # find all child in this topNode
    listAll=pm.listRelatives(obj, pa=1,ad=1)
    # look for readyOnly node
    listRO=pm.ls(listAll, ro=1)
    listA=[x for x in listAll if x not in listRO]
    listCtrls = pm.ls ('*Ctrl',
            '*_MOVER',
            '*_ctrl',
            'DIRECTION',
            'MOVER',
            'PLACER',
            '*_fkIkSwitch')
    listRemain=[x for x in listA if x not in listCtrls]
    for obj in listRemain:
        attrs=pm.listAttr(obj,k=1)
        attrs=pm.listAnimatable(obj)
        for attr in attrs:
            pm.setAttr(attr,cb=1,k=0)
    pm.select(cl=1)
#############################################################
#pick curve first and  then object
#parentShape()
#parentShape(['objA','objB'])
#############################################################
def parentShape(sel=None):
    if sel == None:
        sel = pm.ls (sl=1)
    obj1 = sel[0]
    obj2 = sel[1]
    pm.parent(obj1, obj2)
    # freeze transform curve first
    pm.makeIdentity (obj1,apply = 1, t=1, r= 1 ,s= 1, n= 0)
    pm.delete (obj1,ch =1)
    shape = pm.listRelatives (obj1,f=1,s=1)

    pm.select (shape[0], obj2)
    pm.parent (s=1,r=1)
    pm.delete (obj1)
#############################################################

#############################################################
def parentConstraintMulObjs(sel=None):
    """
    #parentconstrain multiple object
    #select driver first and then  objects
    """
    if sel== None:
        sel=pm.ls(sl=1)
    if len(sel)>=1: #make sure that len select more than 2
        for i in range(1,len(sel)-1):
            pm.parentConstraint(sel[0],sel[i],w=1,mo=1)
#############################################################
#
#############################################################
def parentProximity(listA, listB):
    "listA constains the objs that are going to be parented to B"

    for objA in listA:
        dupA = pm.duplicate(objA)[0]
        pm.select(cl=1)
        pm.select(dupA)
        pm.xform(cp=1)#pm.CenterPivot()
        minDist = 1000
        for objB in listB:
            #print 'evaluating '+ objB
            dupB = pm.duplicate(objB)[0]
            #pm.delete(pm.listRelatives(dupB, c=1, s=0))
            pm.select(cl=1)
            pm.select(dupB)

            pm.xform(cp=1)#pm.CenterPivot()
            dist = getDist(sel=[dupA, dupB])
            #print "EVAL:", str(dist)+' '+objB
            if dist < minDist:
                minDist = dist
                closestObj = objB

            pm.delete(dupB)
        pm.delete(dupA)
        print '>>> parenting %s to %s'%(objA, closestObj)
        pm.parent(objA, closestObj)

def parentSort(objArray=None):
    if objArray== None:
        objArray=pm.ls(sl=1)

    objArray.sort()

    dad=pm.listRelatives(objArray[0], p=1)[0]
    print dad
    for obj in objArray:
        pm.parent(obj, w=1)
        print 'parenting %s to %s'%(obj, dad)
        pm.parent(obj, dad)



#############################################################
# poseReaderRig(objs,space
# AUTHORS:
#   Michael B. Comet
#   covert to py by Thanapoom Siripopungul
# REQUIRES:
#   poseReader.py - Plugin
#############################################################
def poseReaderRig(objs,space=1,name=None, nameOverride=0):
    """#You must select one or more objects to create a poseReader node for
    # space =1 (world), 2 (local)
    # objs = [array objs]
    """
    if not pm.pluginInfo("poseReader",q=1,loaded=1):
        pm.loadPlugin("poseReader.so")
    if len(objs)<=0:
        pm.error(("poseReaderUI: You must select one or more objects to create a poseReader node for!"),sl=0)
    poses=[]
    # Store created nodes for sel at end
    obj=''
    for obj in objs:
        Obj=pm.util.capitalize(obj)
        # new to maya 6, tho it is a script....
        if name == None:
            pose=pm.createNode("poseReader",n=("poseReader_" + Obj + "Shape#"))
        else:
            if nameOverride==0:
                pose=pm.createNode("poseReader",n=("poseReader_" + Obj+name+'Shape'))
            elif nameOverride==1:
                if name[-5:]=='Shape':
                    pose=pm.createNode("poseReader",n=name)
                else:
                    pose=pm.createNode("poseReader",n=name+'Shape')
        attr="worldMatrix"
        if space == 2:
            attr="matrix"

        pm.connectAttr((obj + "." + attr),(pose + ".worldMatrixLiveIn"),f=1)
        xform=pm.listRelatives(pose,p=1)[0]
        pm.connectAttr((xform + "." + attr),(pose + ".worldMatrixPoseIn"),f=1)
        poses.append(xform)
        # Actually store xform for sel.
        # Make a keyable attr people can actually see and use.
        pm.addAttr(pose,ln="weight",k=1)
        pm.connectAttr((pose + ".outWeight"),(pose + ".weight"),f=1)
        # Parent to same parent that object has.
        #   Very important if using local space.
        parent=pm.listRelatives(obj,p=1)[0]
        if parent != "":
            pm.parent(xform,parent)
        # match rotate order of obj
        rotOrder = pm.getAttr(obj+'.rotateOrder')
        xform.attr('rotateOrder').set(rotOrder)
        # Snap xform to same as obj
        pCons=pm.pointConstraint(obj,xform,w=1)
        oCons=pm.orientConstraint(obj,xform,w=1)
        pm.delete(pCons,oCons)
        # Also make up animCurve for animCurve mode
        animCurve=pm.createNode('animCurveUU')
        pm.setKeyframe(animCurve,itt="flat",v=1.0,ott="flat",f=0.0)
        pm.setKeyframe(animCurve,itt="spline",v=0.85,ott="spline",f=0.25)
        pm.setKeyframe(animCurve,itt="spline",v=0.15,ott="spline",f=0.75)
        pm.setKeyframe(animCurve,itt="flat",v=0.0,ott="flat",f=1.0)
        pm.connectAttr((animCurve + ".message"),(pose + ".msgAnimCurve"),f=1)
        pm.connectAttr((animCurve + ".output"),(pose + ".animCurveOutput"),f=1)

    pm.select(poses,r=1)
    # Now if we have more than one pose...connect them up to a multiTrigger node
    nPoses=len(poses)
    if nPoses>1:
        trig=pm.createNode("multiTrigger")
        # Make a keyable attr people can actually see and use.
        pm.addAttr(trig,ln="weight",k=1)
        pm.connectAttr((trig + ".outWeight"),(trig + ".weight"),f=1)
        i=0
        for i in range(0,nPoses):
            pm.connectAttr((poses[i] + ".weight"),(trig + ".inputValues[" + str(i) + "]"),f=1)
        pm.select(poses,trig,r=1)
    return pose

#############################################################
#reorganizes the children on a grp
#############################################################
def progressiveName(objArray=None, basename='ordered'):
    if objArray is None:objArray=pm.ls(sl=1)

    driver=objArray[-1]
    driven=objArray[:-1]

    #i=1
    filter=[]
    for obj in driven:
        D=getDist (sel=[obj, driver])*1000
        print D


        filter.append(pm.rename(obj, 'Distance_'+str(D)+'__order__'+basename))
    filter.sort()

    for obj in filter:
        grpIn('SORTED', obj)




def quickMirror(objArray=None, upVector=[0,0,1], axis='X'):
    """ mirror two object from L > R or R < L using aim Constraint  """
    if objArray is None:
        objArray=pm.ls(sl=1)
    for obj in objArray:
        nSplit=libName.nameSplit(obj)
        if nSplit[-1][0] == 'L':
            nSplit[-1][0]='R'
        elif nSplit[-1][0] == 'R':
            nSplit[-1][0]='L'
        else:
            print 'obj "%s" has been skipped cause prefix is neither "L" nor "R"'
            break

        mirrorObj=libName.nameRevertOriginal(splitName=nSplit)
        if pm.objExists(mirrorObj) == 0:
            print 'obj %s doesnt Exists. Mirrorring Skipped!!!!'%(mirrorObj)

        else:
            loc=pm.spaceLocator(n=obj+'_tmpLocQuickMirror')
            locUp=pm.spaceLocator(n=obj+'_tmpLocQuickMirrorAim')
            locAim=pm.spaceLocator(n=obj+'_tmpLocQuickMirrorUp')
            mloc=pm.spaceLocator(n=obj+'_tmpLocQuickMirrorMirror')

            snap(driver=obj, driven=loc)
            snap(driver=obj, driven=mloc)
            pm.parent(locUp, locAim, loc)
            locAim.attr('t').set([1,0,0])
            locUp.attr('t').set(upVector)
            grpIn('mirrorGrpTmp', loc)

            pm.setAttr('mirrorGrpTmp.scale'+axis, -1)

            mloc.attr('translate'+axis).set(  mloc.attr('translate'+axis).get() * -1 )

            aimCon=pm.aimConstraint(locAim, mloc, aimVector=[1,0,0], upVector=upVector, worldUpObject=locUp, worldUpType='object', mo=0)
            snap(driver=mloc, driven=mirrorObj)

            pm.delete('mirrorGrpTmp', mloc)

def renameChildren(objArray=None, suffix=None, type=0):

    if objArray is None:
        objArray=pm.ls(sl=1)

    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    errorList = []

    for o in objArray:
        i=1

        bn = o.nodeName()

        if suffix is None:
            suffix = bn.split('_')[-1] #changes the last token

        children = o.listRelatives(c=1, type='transform')
        for ch in children:

            if type == 0:
                x = '%02d'%i
            elif type == 1:
                x = letters[i-1]
            if len(children) < 2:
                newName = '%s_%s'%( bn.rsplit('_', 1)[0], suffix )
            elif len( bn.split('_') ) > 3:
                newName = '%s_%s_%s'%( bn.rsplit('_', 1)[0], x, suffix )
            else:
                newName = '%s%s_%s'%(libName.baseName(o),x, suffix)

            n = pm.rename(ch, newName)

            i = i+1



def renameByParent(objArray=None, suffix='geo', type=0):
    '''
    Rename obj with suffix
    :param objArray:
    :param suffix: don't include the _
    :param type: 0 is number, 1 is letter
    :return:
    '''
    if objArray is None:
        objArray=pm.ls(sl=1)
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    errorList = []
    newNames = ['']
    i=1
    for o in objArray:
        newNames.append('')
        p = pm.listRelatives(o, p=1)[0]
        # MOG fix naming the hierarchy if multiple
        p = p.nodeName()
        # removing already existing suffix
        p = p.replace('_'+suffix, '')
        # removing grp
        p = p.replace('_grp', '')

        print 'renaming %s_%s'%(newNames[i],i)

        # check _geo has children
        if (suffix == 'geo') and (pm.listRelatives(o, children=1)[0].type() == 'transform'):
            pm.warning('Warning. Geo has children %s'%o)

        # numbers
        if type == 0:
            if len( p.split('_') ) > 3:
                newNames[i] = '%s_%02d_%s'%( p.rsplit('_', 1)[0], i, suffix )
            else:
                newNames[i] = '%s%02d_%s'%(libName.baseName(p),i, suffix)
                n = pm.rename(o,'%s%s'%(newNames[i],i))

        # letters
        elif type == 1:
            if len( p.split('_') ) > 3:
                newNames[i] = '%s_%s_%s'%( p.rsplit('_', 1)[0], letters[i-1], suffix )
            else:
                newNames[i] = '%s_%s_%s'%(libName.baseName(p),letters[i-1], suffix)
                n = pm.rename(o, '%s%s'%(newNames[i],i))
        i = i+1

    # run again to fix geo1
    i = 1
    objArray.sort()
    for o in objArray:
        print 'o is %s'%o
        print 'newnane is %s'%newNames[i]
        pm.rename(o, newNames[i])
        if o  != newNames[i]:
            errorList.append( n )
        i = i+1

    if len(errorList) != 0:
        message = 'SOMETHING WENT WRONG!!!\m try run it again: %s'%(errorList)
        pm.confirmDialog(message = message,
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')


def returnDeformers(objArray=None):
    if objArray is None:
        objArray=pm.ls(sl=1)

    allDeformers = []
    for obj in objArray:
        deformers = []
        for n in pm.listHistory(obj):
            types = pm.nodeType(n, inherited=1)
            if types[0] == 'geometryFilter':
                if n not in deformers:
                    deformers.append(n)
        allDeformers.append([obj, deformers])
    return allDeformers

def scaleUVs(objArray=None, scaleU=-1, scaleV=1):
    if objArray is None:
        objArray = pm.ls(sl=1)

    for obj in objArray:
        shp = pm.listRelatives(obj, s=1)[0]

        if shp.type() == 'mesh':
            print shp
            pm.polyEditUV(shp+'.map[:]', pivotV=0.5, pivotU=0.5, scaleU=scaleU, scaleV=scaleV)


###########
#script network allow to select a bunch of connected nodes and the script will try to make it a creation script for the network
##########
def scriptNetwork(findToken='name', variableName='basename'):
    scriptListCreate=[]
    scriptListCnx=[]
    scriptListSetAttr=[]

    exceptionList=['message']
    atExceptionList=[]
    sel=pm.ls(sl=1)
    cnCmd=["""pm.createNode('""",  """' , n=""", """)"""]
    cnAttrCmd=["""pm.connectAttr(""",    variableName+"""+'""",     """', """+variableName+"""+'""",        """')"""]
    setAttrCmd=["""pm.setAttr(""",  """+'.""", """', """ , """)"""]

    for x in sel:
        print x
        t=x.type()
        n=variableName+""" + '"""+x.name().split(findToken)[-1]+"""'"""
        scriptListCreate.append(cnCmd[0]+t+cnCmd[1]+n+cnCmd[2])

        plugsDestination=x.connections(plugs=1, destination=1, source=0, connections=1)
        for p in plugsDestination:
            inputAttr=p[0].split(findToken)[-1]
            outAttr=p[1].split(findToken)[-1]

            if p[0].split('.')[-1] not in exceptionList and pm.PyNode(p[1].split('.')[0]) in sel:
                scriptListCnx.append(    cnAttrCmd[0]  +  cnAttrCmd[1]  +  inputAttr   +  cnAttrCmd[2]  +  outAttr  +  cnAttrCmd[3]  )

        myAttrs=pm.listAttr(x, k=1)
        if x.hasAttr('operation'):
            myAttrs.append('operation')
        print myAttrs

        for at in myAttrs:
            if x.attr(at).isCompound():
                print at + ' compound'
                numC=x.attr(at).numChildren()
                indices=x.attr(at).get(mi=1)
                if numC != 0 and indices is not None:
                    for c in x.attr(at).children():
                        #print c.split('.')[-1]
                        for i in indices:
                            myChildAt=at+'['+str(i)+'].'+c.split('.')[-1]
                            print myChildAt
                            v=x.attr(myChildAt).get()
                            scriptListSetAttr.append( setAttrCmd[0]  + n + setAttrCmd[1]  +  myChildAt  +  setAttrCmd[2]  +  str(v)  +  setAttrCmd[3])


            elif x.attr(at).isChild():

                if pm.objExists(x+'.'+at):
                    print at + ' is child and exists'
                    #v=pm.getAttr(x+'.'+at)
                    v=x.attr(at).get()
                    scriptListSetAttr.append( setAttrCmd[0]  + n + setAttrCmd[1]  +  at  +  setAttrCmd[2]  +  str(v)  +  setAttrCmd[3])


            elif x.attr(at).isArray():
                print at + ' is array'

            else:
                print at +' notCompound'
                #v=pm.getAttr(x+'.'+at)
                v=x.attr(at).get()
                scriptListSetAttr.append( setAttrCmd[0]  + n + setAttrCmd[1]  +  at  +  setAttrCmd[2]  +  str(v)  +  setAttrCmd[3])


    print '#=============================================================================='
    print '#=============================================================================='
    print '#COPY THIS'
    print '#=============================================================================='
    for x in scriptListCreate:
        print x
    for x in scriptListSetAttr:
        print x
    for x in scriptListCnx:
        print x
    print '#=============================================================================='
    print '#=============================================================================='

#############################################################
#reorganizes the children on a grp
#############################################################
def sortChildren(grp):
    grp=pm.PyNode(grp)
    childs=pm.listRelatives(grp, c=1)
    childs.sort()
    for c in childs:
        pm.parent(c, w=1)
        pm.parent(c, grp)
#############################################################
#makes creates and adds objects to a set
# libU.setIn('mySet', 'objA')
#############################################################
def setIn(setName, obj):
    pm.select(cl=True)
    if pm.objExists(setName):
        mySet=setName
        pm.sets(mySet, add=obj)
    else:
        mySet=pm.sets(n=setName)
        pm.sets(mySet, add=obj)
#############################################################
#makes creates and adds objects to a set
# libU.setIn('mySet', 'objA')
#############################################################
def setOut(setName, obj):
    pm.select(cl=True)
    if pm.objExists(setName):
        mySet=setName
        pm.sets(mySet, rm=obj)
#############################################################


def setWireColor(color, objArray=None):
    if objArray is None:
        objArray=pm.selected()


    for geo in objArray:
        geoShape = pm.PyNode(geo).getShape()
        pm.setAttr("%s.overrideEnabled"%geoShape, lock=0)
        pm.setAttr("%s.overrideColor"%geoShape, lock=0)
        pm.setAttr("%s.overrideEnabled"%geoShape, 1)
        pm.setAttr("%s.overrideColor"%geoShape, color)
        pm.setAttr("%s.overrideEnabled"%geoShape, lock=1)
        pm.setAttr("%s.overrideColor"%geoShape, lock=1)

#############################################################

def selectByDistance(objArray = None, anchor=None, select=1):
    if objArray is None:
        objArray=pm.ls(sl=1)[:-1]
    if anchor is None:
        anchor=pm.ls(sl=1)[-1]

    myList=[]
    for obj in objArray:
        myList.append( [ obj, getDist (sel=[obj, anchor])  ]  )
    myList.sort(key=lambda x: x[1])

    selectList=[]
    for obj in myList:
        selectList.append(obj[0])
    if select == 1:
        pm.select(selectList)

    return selectList

def selectJntsInHierarchy():
    jnts = []
    rootJnts = pm.selected()
    for rootJnt in rootJnts:
        for c in pm.listRelatives(rootJnt, ad=1):
            if c.type() == 'joint':
                jnts.append(c)
        if rootJnt.type() == 'joint':
            jnts.append(rootJnt)
    for j in jnts:
        print j
    pm.select(jnts)

def setSDK(attrDrv,attrDrvn,valDrv,valDrvn,typeKey = 'linear',infinity=1,sel = None):
    """
    use for set drivernkey
    valDrv = [[90,-90,0]]  last val is default position
    set driver rotateX 90, then rotateX -90 and then set to 0
    attrDrvn = ['tz'] must be list because u can set many attr as you want
    attrDrv = must be only one attr
    select driver and driven
    libUtil.setSDK(attrDrv = 'rx',attrDrvn = ['tz'],valDrv = [[90,-90,0]],valDrvn = [[-1,-1,0]],sel=None)
    """
    if sel==None:
        sel = pm.ls(sl=1)
    driver = sel[0]
    driven = sel[1]
    for i in range(0,len(attrDrvn)):
        for a in range (0,len(valDrv[i])):
            pm.setDrivenKeyframe(driven,cd = (driver + '.'+attrDrv),at = attrDrvn[i],v = valDrvn[i][a],dv = valDrv[i][a],itt = typeKey,ott = typeKey)
        #pm.setDrivenKeyframe(driven,cd = (driver + '.'+attrDrv),at = attrDrvn[i],v = valDrv[i][-1],dv = valDrv[i][-1],itt = typeKey,ott = typeKey)
    #set infinity
    if infinity==1:
        for i in range(0,len(attrDrvn)):
            #convert attr from short name to long name
            attr = attrDrvn[i]
            if attrDrvn[i]=='tx':attr = 'translateX'
            if attrDrvn[i]=='ty':attr = 'translateY'
            if attrDrvn[i]=='tz':attr = 'translateZ'
            if attrDrvn[i]=='rx':attr = 'rotateX'
            if attrDrvn[i]=='ry':attr = 'rotateY'
            if attrDrvn[i]=='rz':attr = 'rotateZ'
            if attrDrvn[i]=='sx':attr = 'scaleX'
            if attrDrvn[i]=='sy':attr = 'scaleY'
            if attrDrvn[i]=='sz':attr = 'scaleZ'
            if attrDrvn[i]=='v':attr = 'visibility'
            #add infinity key
            pm.selectKey(driven + '_' + attr,add=1,k=1)
            pm.keyTangent (itt= 'spline', ott= 'spline')
            pm.setInfinity(poi='linear',pri='linear')


def separateUdims(mesh=None, moveUvs=True):
    '''
        Given a mesh will seperate into into multiple meshes, one for each udim tile.
        With the ability to shift all these new meshes uvs back to 0-1 with the moveUvs flag
    '''

    if mesh is None:
        mesh=pm.ls(sl=1)[0].getShape()

    m = pm.PyNode(mesh)
    uvIds = m.numUVs()
    uList, vList = m.getUVs()
    uMax= int(max(uList))
    vMax = int(max(vList))

    for uValue in range(uMax+1):
        for vValue in range(vMax+1):
            #print uValue, vValue
            print 'udim 10%d%d'%(vValue, uValue)
            #pm.select(clear=True)
            selectUVs = []
            for i in range(uvIds):
                u,v = m.getUV(i)
                #print i
                if u>uValue and u<(uValue+1) and v>vValue and v<(vValue+1):
                    #print 'first shell'
                    selectUVs.append(m.map[i])
                    #pm.select(m.map[i], add=True)

            if selectUVs:
                #pm.select(selectUVs, r=True)
                udimFaces = pm.polyListComponentConversion(selectUVs, fromUV=True, toFace=True)
            print udimFaces

            if udimFaces:
                print 'chip'
                pm.polyChipOff(udimFaces, ch=True, kft=True, dup=0, off=0, name='tile_10%d%d'%(vValue, uValue))
            else:
                print 'no uvs in udim %d %d'%(uValue, vValue)

    sepMeshes = pm.polySeparate(m, ch=False)
    for s in sepMeshes:
        u,v = s.getUV(0)
        num = s.numUVs()

        s.rename('tile_10%d%d_geo'%(int(v), int(u+1)) )

        if moveUvs:
            pm.polyMoveUV(s.map[0:(num-1)], translate=[ (int(u)*-1) , (int(v)*-1) ])

    return sepMeshes

def separateGeoByAllShells(obj=None):
    if obj is None:
        obj = pm.ls(sl=1)[0]

    extraObjs = []
    for i in range(1, 100):
        chip, residual = separateSelectedShell(obj)
        obj = residual[0]
        if len(residual) > 1:
            for x in residual:
                extraObjs.append(x)


    pm.select(extraObjs)




def separateSelectedShell(obj, index=0):
    shp = obj.getShape()

    pm.select('%s.map[%s]'%(shp, index))

    pm.mel.polySelectBorderShell(0)
    pm.mel.PolySelectConvert(1)

    pm.polyChipOff(ch=0, kft=1 ,dup=0, off=0)

    chips = pm.polySeparate(obj, ch=0)
    chip = chips[0]
    grpIn('chipsGrp', chip)
    residual = chips[1:]
    print chip, residual

    return [chip, residual]



#############################################################
#snaps objects and skips locked attributes to prevent errors...
#also this doesnt uses constraints to snap..
#so The target objet could have keys if it is needed
# libUtil.snap('cube', 'target' , typeCnx='parent')
#############################################################
def snap(driver, driven, typeCnx='parent', extraDrivers=(), skip=[]):

    drivers = [driver]
    drivers.extend(extraDrivers)

    for i, driver in enumerate(drivers):
        if not isinstance(driver, pm.PyNode):
            drivers[i] = pm.PyNode(driver)
    if not isinstance(driven, pm.PyNode):
        driven = pm.PyNode(driven)
    # skip memory
    skipMemory=[]
    for s in skip:
        skipMemory.append(driven.attr(s).get())

    dummy=pm.duplicate(driven, n=driven+'dummy', parentOnly=1)[0]
    for attr in ('t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz','s','sx','sy','sz'):
        dummy.attr(attr).unlock()

    con = pm.parentConstraint(mo=0, *(drivers + [dummy]) )
    con.interpType.set(2)
    pm.delete(con)
    #pm.delete(pm.parentConstraint(mo=0, *(drivers + [dummy]) ))
    pm.delete(pm.scaleConstraint(mo=0, *(drivers + [dummy]) ))
    #pm.delete( pm.parentConstraint(drivers, dummy, mo=0,))


    t= pm.getAttr(dummy+'.translate')
    r= pm.getAttr(dummy+'.rotate')
    s= pm.getAttr(dummy+'.scale')
    pm.delete(dummy)

    #PARENT
    if typeCnx in ['parent','parentCon',1, 'p', 'P']:
        i=0
        for at in ['tx', 'ty', 'tz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(t[i])
            i=i+1
        i=0
        for at in ['rx', 'ry', 'rz']:
            try:
                driven.attr(at).set(r[i])
            except:
                pass
            i=i+1
    #ROTATE ONLY
    elif typeCnx in ['orient', 'rotate', 2, 'r', 'R']:
        i=0
        for at in ['rx', 'ry', 'rz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(r[i])
            i=i+1
    #TRANSLATE ONLY
    elif typeCnx in ['point', 'translate', 3, 't', 'T']:
        i=0
        for at in ['tx', 'ty', 'tz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(t[i])
            i=i+1
    #SCALE ONLY
    elif typeCnx in ['scale', 'Scale', 4, 's', 'S']:
        i=0
        for at in ['sx', 'sy', 'sz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(s[i])
            i=i+1
    #ALL
    elif typeCnx in ['all','All',5, 'a', 'A']:
        i=0
        for at in ['tx', 'ty', 'tz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(t[i])
            i=i+1
        i=0
        for at in ['rx', 'ry', 'rz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(r[i])
            i=i+1
        i=0
        for at in ['sx', 'sy', 'sz']:
            if driven.attr(at).isLocked() ==0:
                driven.attr(at).set(s[i])
            i=i+1
    # skip memory
    i=0
    for s in skip:
        driven.attr(s).set(skipMemory[i])
        i=i+1
    pm.select(driven)

###############################################################
def snapToMesh(driver, objArray=None):
    if objArray is None:
        objArray=pm.ls(sl=1)
    dup=pm.duplicate(driver)[0]

    if len(pm.listRelatives(dup, p=1))!=0:
        pm.parent(dup, w=1)

    for at in dup.listAttr(l=1, k=1):
        at.set(l=0)

    pm.makeIdentity(dup, apply=1, t=1, r=1, s=1, n=0)

    for obj in objArray:
        objCoo=pm.xform(obj, ws=True, rp=True, q=True)
        coo= dup.getShape().getClosestPoint(objCoo)
        pm.move(obj,coo[0], ws=1)
    pm.delete(dup)

def snapOrientationToMesh( driver, objArray=None, aimVector=[1,0,0], upVector=[0,1,0], worldVector = [0,1,0] ):
    if objArray is None:
        objArray=pm.ls(sl=1)

    dup=pm.duplicate(driver)[0]

    if len(pm.listRelatives(dup, p=1))!=0:
        pm.parent(dup, w=1)

    for at in dup.listAttr(l=1, k=1):
        at.set(l=0)

    pm.makeIdentity(dup, apply=1, t=1, r=1, s=1, n=0)

    # loc = pm.spaceLocator()
    # locAim = pm.spaceLocator()
    # pm.parent(locAim, loc)
    cleanTransforms(objArray)

    for obj in objArray:
        #ox = pm.getAttr('%s.rotateX'%obj)
        #oy = pm.getAttr('%s.rotateY'%obj)
        pm.delete( pm.normalConstraint(dup, obj, weight=1, aimVector=aimVector, upVector=upVector, worldUpType="scene") )
        #pm.setAttr('%s.rotateX'%obj, ox)
        #pm.setAttr('%s.rotateY'%obj, oy)

        # objCoo=pm.xform(obj, ws=True, rp=True, q=True)
        # coo= dup.getShape().getClosestPoint(objCoo)
        # pm.move(loc,coo[0], ws=1)

    pm.delete(dup)


#############################################################
# snaps objects with same topology but different pivot points.
# specify 3 vertices to use for the snap (or it auto selects first, middle and last)
# libUtil.snap('cube', 'target' , typeCnx='parent')
#############################################################
def snapWithVertices(driver=None, driven=None, vertices=None):

    if driver is None:
        driver = pm.ls(sl=1)[0]
    driverS = driver.getShape()

    if driven is None:
        driven = pm.ls(sl=1)[1]
    drivenS = driven.getShape()

    dvr = 0
    for geo in drivenS, driverS:
        print geo
        if dvr == 0:
            name = 'driven'
        else:
            name = 'driver'
        if vertices is None:
            cv1 = geo.vtx[0]
            cv2 = geo.vtx[geo.numVertices()  /2]
            cv3 = geo.vtx[geo.numVertices()  -1]
            cvs = [cv1, cv2, cv3]
        else:
            cvs = vertices
        print cvs

        i=1
        for cv in cvs:
            loc = pm.spaceLocator(n='%sLoc%s'%(name,i))
            loc.setPosition(cv.getPosition(space='world'))
            i=i+1
        pm.aimConstraint('%sLoc2'%name, '%sLoc1'%name, weight=1, upVector=(0, 1, 0), mo=1, worldUpObject='%sLoc3'%name, worldUpType="object", aimVector=(1, 0, 0))
        dvr = 1

    constGeo = pm.parentConstraint('drivenLoc1', driven, mo=1)
    snap('driverLoc1' , 'drivenLoc1', typeCnx='parent')
    snap('driverLoc2' ,'drivenLoc2',  typeCnx='parent')
    snap('driverLoc3' ,'drivenLoc3',  typeCnx='parent')

    pm.delete(constGeo)
    pm.delete('driverLoc1' , 'drivenLoc1', 'driverLoc2' , 'drivenLoc2', 'driverLoc3' , 'drivenLoc3')

def scaleConnect(objArray=None):
    if objArray is None:
        objArray=pm.ls(sl=1)
    for obj in objArray:
        pm.connectAttr('%s.sx'%obj, '%s.sy'%obj)
        pm.connectAttr('%s.sx'%obj, '%s.sz'%obj)

        pm.setAttr('%s.sy'%obj, l=1)
        pm.setAttr('%s.sz'%obj, l=1)

def skinClusterNameGet(objArray=None):
    objArray=pm.ls(sl=1)
    print '############################################'
    print '['
    for obj in objArray:
        shp=obj.getShape()
        links=pm.listHistory(shp,pdo=0,il=1)
        skinClusterName=pm.ls(links,typ="skinCluster")[0].split(':')[-1]
        myReturn='["%s","%s"],'%(shp.split(':')[-1], skinClusterName.split(':')[-1])
        print myReturn
    print ']'
    print '############################################'

def skinClusterNameApply(nameArray):
    for x in nameArray:
        shp, newName = x
        if pm.objExists(shp) == 0:
            print '%s doesnt Exists'%shp
            break
        links=pm.listHistory(shp,pdo=0,il=1)
        skinClusters=pm.ls(links,typ="skinCluster")
        if len(skinClusters) == 0:
            print 'no skinCLuster found in "%s"'%shp
            break
        pm.rename(skinClusters[0], skinClusters[0]+'_tmpSkinClusterName')

    for x in nameArray:
        shp, newName = x
        if pm.objExists(shp) == 0:
            print '%s doesnt Exists'%shp
            break
        links=pm.listHistory(shp,pdo=0,il=1)
        skinClusters=pm.ls(links,typ="skinCluster")
        if len(skinClusters) == 0:
            print 'no skinCLuster found in "%s"'%shp
            break
        pm.rename(skinClusters[0], newName)

#############################################################
# use to transfer attributes from one object to another obj(controler)
#############################################################
def transferAttr(driven, ctrl, attrArray=None, header=None):
    driven=pm.PyNode(driven)
    ctrl=pm.PyNode(ctrl)

    if attrArray is None:
        print 'WARNING: transfering all attributes'
        attrArray=pm.listAttr(driven, k=1, l=0)
    for at in attrArray:
        print 'transfering ',at
        if header is not None:
            atName=header+pm.util.capitalize(at)
        else:
            atName=libName.baseName(driven)+pm.util.capitalize(at)
        if pm.objExists(ctrl+'.'+atName)==0:
            #v=driven.attr(at).get()
            pm.addAttr(ctrl, ln=atName, k=1, at=driven.attr(at).get(type=1), dv=driven.attr(at).get())
        pm.connectAttr(ctrl+'.'+atName, driven+'.'+at)

def transferSkinWeightsCrvToPoly(crv=None, obj=None):
    if crv is None:
        crv = pm.selected()[0]
    else:
        crv = pm.PyNode(crv)

    if obj is None:
        obj = pm.selected()[1]
    else:
        obj = pm.PyNode(obj)

    mesh = obj.getShape()
    nurbShp = crv.getShape()

    links=pm.listHistory(crv,pdo=0,il=1)
    skin=pm.ls(links,typ="skinCluster")

    sknCl=skin[0]
    influences=pm.skinCluster(sknCl,query=True,inf=True)

    pm.select(influences, obj)
    polySkinCluster=pm.skinCluster()


    for v in range(0, mesh.numVertices()):
        v_coo = mesh.getPoint(v, space='world')

        D = 100
        for u in range(0, nurbShp.numCVs() ):
            u_coo = nurbShp.getCV(index=u, space='world')

            v3 = v_coo - u_coo
            d = v3.length()

            if d<D:
                D=d
                closest = u

        transformValue=[]
        for jnt in influences:
            transformValue.append((jnt, pm.skinPercent(sknCl, '%s.cv[%s]'%(crv, closest), transform=jnt, q=1)))

        pm.skinPercent(polySkinCluster, '%s.vtx[%s]'%(obj , v), transformValue=transformValue)

def TransferSkinWeightsPolyToPoly(source, targets):

    # source = pm.selected()[0]
    # targets = pm.selected()[1:]
    # TransferSkinWeightsPolyToPoly(source, targets)

    influences=pm.skinCluster(source,query=True,inf=True)
    for target in targets:
        try: pm.skinCluster(target, e=1, ub=1)
        except: pass
        pm.select(influences, target)
        targetSknCl=pm.skinCluster()
    pm.select(source, targets[0])
    pm.mel.eval('copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation oneToOne -influenceAssociation name;')




def transferSkinWeightsPolyToNurb(poly, nurb):
    poly=pm.PyNode(poly)
    nurb=pm.PyNode(nurb)

    polyShp=poly.getShape()
    nurbShp=nurb.getShape()

    if polyShp.type() != 'mesh' or nurbShp.type() != 'nurbsSurface':
        pm.confirmDialog(message = 'please make sure you select one poly and one nurb ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('please make sure you select one poly and one nurb ')

    links=pm.listHistory(nurbShp,pdo=0,il=1)
    skin=pm.ls(links,typ="skinCluster")
    if len(skin)!=0:
        pm.confirmDialog(message = 'please remove any other skin cluster from ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('please remove any other skin cluster from nurb')

    links=pm.listHistory(polyShp,pdo=0,il=1)
    skin=pm.ls(links,typ="skinCluster")
    if len(skin)==0:
        pm.confirmDialog(message = 'polygon doesnt have a skin cluster ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('polygon doesnt have a skin cluster ')

    sknCl=skin[0]

    cPnt=pm.createNode('closestPointOnMesh', n=(poly+'_cpom'))
    pm.connectAttr (polyShp+'.outMesh', cPnt+'.inMesh')

    influences=pm.skinCluster(sknCl,query=True,inf=True)
    pm.select(influences, nurb)
    nurbSknCl=pm.skinCluster()

    for u in range(0, nurbShp.numCVsInU() ):
        for v in range (0, nurbShp.numCVsInV() ):
            myCV = '%s.cv[%1d][%1d]'%(nurbShp, u, v)
            coo=nurbShp.getCV(indexU=u, indexV=v, space='world')

#             myPnt, vtxIndex = polyShp.getClosestPoint(coo, space='world')
#

            pm.setAttr(cPnt+'.inPositionX', coo[0])
            pm.setAttr(cPnt+'.inPositionY', coo[1])
            pm.setAttr(cPnt+'.inPositionZ', coo[2])

            cVtxIndex=cPnt.attr('closestVertexIndex').get()
            myVtx = '%s.vtx[%1d]'%(polyShp,cVtxIndex)

            #print '%s >>> %s >>> %s '%(myCV, coo, myVtx)

            transformValue=[]
            for jnt in influences:
                transformValue.append((jnt, pm.skinPercent(sknCl, myVtx, transform=jnt, q=1)))

            pm.skinPercent(nurbSknCl, myCV, transformValue=transformValue)

    pm.delete(cPnt)
    print 'transfer Finished'


def transferSkinWeightsPolyToCrv(poly, nurb):
    poly=pm.PyNode(poly)
    nurb=pm.PyNode(nurb)

    polyShp=poly.getShape()
    nurbShp=nurb.getShape()

    if polyShp.type() != 'mesh':
        pm.confirmDialog(message = 'please make sure you select one poly and one nurb ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('please make sure you select one poly and one nurb ')

    links=pm.listHistory(nurbShp,pdo=0,il=1)
    skin=pm.ls(links,typ="skinCluster")
    if len(skin)!=0:
        pm.confirmDialog(message = 'please remove any other skin cluster from ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('please remove any other skin cluster from nurb')

    links=pm.listHistory(polyShp,pdo=0,il=1)
    skin=pm.ls(links,typ="skinCluster")
    if len(skin)==0:
        pm.confirmDialog(message = 'polygon doesnt have a skin cluster ',
        button = 'ok',defaultButton = 'Yes',
        title = 'Confirm')
        pm.error('polygon doesnt have a skin cluster ')

    sknCl=skin[0]

    cPnt=pm.createNode('closestPointOnMesh', n=(poly+'_cpom'))
    pm.connectAttr (polyShp+'.outMesh', cPnt+'.inMesh')

    influences=pm.skinCluster(sknCl,query=True,inf=True)
    pm.select(influences, nurb)
    nurbSknCl=pm.skinCluster()

    for u in range(0, nurbShp.numCVs() ):

        myCV = '%s.cv[%1d]'%(nurbShp, u)
        coo=nurbShp.getCV(index=u, space='world')

        pm.setAttr(cPnt+'.inPositionX', coo[0])
        pm.setAttr(cPnt+'.inPositionY', coo[1])
        pm.setAttr(cPnt+'.inPositionZ', coo[2])

        cVtxIndex=cPnt.attr('closestVertexIndex').get()
        myVtx = '%s.vtx[%1d]'%(polyShp,cVtxIndex)

        #print '%s >>> %s >>> %s '%(myCV, coo, myVtx)

        transformValue=[]
        for jnt in influences:
            transformValue.append((jnt, pm.skinPercent(sknCl, myVtx, transform=jnt, q=1)))

        pm.skinPercent(nurbSknCl, myCV, transformValue=transformValue)

    pm.delete(cPnt)
    print 'transfer Finished'


def transferSkinWeightsFromSeparateToCombined(drivenMesh='polySurface1'):
    drivenShape=pm.PyNode(drivenMesh).getShape()
    myD={}
    for x in shp.vtx[:]:
        myD[str(x)]=x.getPosition()

    for obj in pm.ls(sl=1):
        print obj
        shp=obj.getShape()
        for x in shp.vtx[:]:
            for key in myD.keys():
                if myD[key] == x.getPosition():
                    print 'foundMatch'
                    break

#############################################################
# used for update deform mesh without redo deform
#############################################################
def updateDefMesh(sel = None,uv=1,blend=1, tc=0, useColor=0, backUp=0):
    # used for update deform mesh without redo deform
    # select new mesh first and then def mesh
    if sel== None:
        sel = pm.ls(sl=1)
    newMesh = pm.PyNode(sel[0])
    oldMesh = pm.PyNode(sel[1])
    # find origShape
    oldShape = oldMesh.getShape()

    if backUp==1:
        grpIn('backUpMeshGrp', pm.duplicate(oldMesh, n='%s_bckup'%oldMesh)[0])
        pm.setAttr('backUpMeshGrp.visibility', 0)

    if pm.objExists(oldShape+'Orig'):
        origShape = pm.PyNode(oldShape+'Orig')
        #turn off for fixShape
        origShape.attr('intermediateObject').set(0)
    else:
        origShape = oldMesh
    #blenshape
    if blend ==1:
        try:
            blendName = pm.blendShape(newMesh,origShape,n='tempBlend',tc=tc)[0]
            pm.setAttr (blendName+"." +newMesh, 1)
            #delete history
            pm.delete(origShape,ch=1)

        except:
            if useColor == 1:
                newMesh.useOutlinerColor.set(True)
                newMesh.outlinerColor.set(.9, .3, .25)

            print 'ERROR not the same topology %s  %s '%(newMesh, oldMesh)
            return
    #transfer UV
    #spa=1 model space (local)
    if uv==1:
        pm.transferAttributes (newMesh,origShape,
                        pos= 0,nml= 0,uvs= 2,col= 1,
                        spa= 1 ,
                        sus= "map1",tus= "map1",
                        sm= 3,flipUVs =0 ,clb= 1)
        pm.delete(origShape,ch=1)
    if pm.objExists(oldShape+'Orig'):
        origShape.attr('intermediateObject').set(1)

    if useColor == 1:
        oldMesh.useOutlinerColor.set(True)
        oldMesh.outlinerColor.set(.9, .9, .5)

    print 'defMesh has been updated'
#############################################################
# used for update blendShape
#############################################################
def updateBlendShape(sel = None):
    # used for update bledShape
    # select new mesh first and then old mesh
    if sel== None:
        sel = pm.ls(sl=1)
    newMesh = pm.PyNode(sel[0])
    oldMesh = pm.PyNode(sel[1])
    #blenshape
    blendName = pm.blendShape(newMesh,oldMesh,n='tempBlend',tc=0)[0]
    pm.setAttr (blendName+"." +newMesh, 1)
    #delete history
    pm.delete(oldMesh,ch=1)
    print 'oldMesh has been updated iojoi'

def updateClosestPointOnMesh(old, new):
    cps = pm.ls(type = 'closestPointOnMesh')
    new = pm.PyNode(new)
    old = pm.PyNode(old)

    for cp in cps:
        mesh = cp.inMesh.inputs()[0]
        print cp, mesh, old
        if str(mesh) == str(old):
            'print switching %s: %s to %s'%(cp, old, new)
            pm.connectAttr( '%s.worldMatrix[0]'%new.getShape(), '%s.inputMatrix'%cp , f=1)
            pm.connectAttr( '%s.worldMesh[0]'%new.getShape(), '%s.inMesh'%cp , f=1)



