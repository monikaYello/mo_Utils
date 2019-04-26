import pymel.core as pm
import logging
import mo_Utils.mo_curveLib as mo_curveLib
import mo_Utils.mo_mathUtils as mathUtils
import mo_stringUtils as mo_stringUtils

reload(mo_curveLib)

_logger = logging.getLogger(__name__)

'''
import sys
sys.path.append('D:/Google Drive/PythonScripting/scripts')
import mo_Utils.mo_riggUtils as mo_riggUtils
reload(mo_riggUtils)
mo_riggUtils.createCvControls(curves='curve2', ctrl='cluster')
'''


def getTransformations(t=True, r=False, world=1):
	sel = pm.ls(sl=True)
	if (len(sel) < 1):
		print ("Error. Select objects you want to get translation values from")
		return False
	i = 1
	tList = []
	tPrint = ""
	rList = []
	rPrint = ""

	for each in sel:
		position = pm.xform(each, q=1, ws=world, rp=1)
		tList.append(position)
		tPrint = tPrint + "pos%s = %s\n" % (i, position)
		if (r == True):
			rList.append(each.getRotation())
			rPrint = rPrint + "rot%s = %s\n" % (i, each.getRotation())
		i = i + 1
	print tPrint
	print rPrint
	return tList, rList


###############################
##create ikSpline solver
###############################
def createIKSpline(startJoint, endJoint, curve, name='ikSplineIKSolver'):
	return pm.ikHandle(startJoint=startJoint, ee=endJoint, curve=curve, ccv=False, solver='ikSplineSolver', name=name)


###############################

###############################
def createJointsAtPos(targetObjects, chain=False, constrain=False, name=None, suffix='ctrlJnt'):
	'''
   Create joints (floating or chain) at position of each targetPos objects
	Args:
		targetPos: List[] of target objects
		chain: Bool, if True will parent joints and reoorient
		constrain: True will parentConstrain taretObjects to joints
		name: if None will get get name of targetObject and add Suffix
		suffix:

	Returns: List of joints created

	'''
	# get selection if targetPos False
	if targetObjects == False:
		targetPos = pm.ls(sl=1)

	pm.select(clear=True)
	i = 0
	rootjoint = None
	# run through all target positions
	for each in targetPos:

		position = pm.xform(each, q=1, ws=1, rp=1)

		if (chain == False):
			pm.select(clear=True)
		if name == None:
			name = each
		j1 = pm.joint(n='%s_%s' % (name, suffix))
		if (i == 0):
			rootjoint = j1
		j1.setTranslation(position, ws=True)

		# align via parenting
		# pm.parent(j1, each)
		# if(i==0):
		#    rootjoint = j1
		# j1.setTranslation([0,0,0])
		# pm.parent(j1,world=True)

		# constrain
		if constrain == True:
			pm.parentConstraint(each, j1)
		i = i + 1
	# reorient
	if (chain == True):
		pm.select(rootjoint, hi=True)
		pm.joint(zso=1, ch=1, e=1, oj='xyz', secondaryAxisOrient='ydown')




###############################
## scale shape node by factor
###############################
def scaleShape(factor, objs=None):
	if objs == None:
		if len(pm.ls(sl=1)) < 1:
			return False
		objs = pm.ls(sl=1)
	for obj in objs:
		if obj.type() == 'transform':
			shapenode = obj.getShape()
		else:
			shapenode = obj
		pm.select(shapenode.cv[0:shapenode.numCVs() - 1])
		pm.scale(factor, factor, factor)
	pm.select(objs)


###############################
## create control for each cv on cuve, skin if True
## return list of ctrl shape
###############################
def createCvClusters(curves=None, ctrl='joint', suffix='skinJnt', skin=False):
	if curves == None:
		curves = pm.ls(sl=1)
	if not isinstance(curves, list):
		curves = [curves]
	jointList = []
	for curve1 in curves:
		if isinstance(curve1, pm.nodetypes.Transform):
			curve1 = curve1.getShape()
		if isinstance(curve1, str):
			curve1 = pm.PyNode(curve1).getShape()
		print curve1

		curvePoints = curve1.numCVs()

		for curvePoint in range(curvePoints):
			# select matching cvs on both curves
			pm.select(clear=1)
			# cluster
			if ctrl == 'cluster':
				pm.select(curve1.cv[curvePoint])
				cl = pm.cluster(n='%s_cluster' % curve1.name())
				jointList.append(cl)

			# joint
			else:

				cl = pm.joint(n='%s%s_%s' % (curve1.name(), curvePoint, suffix))
				print cl
				cl.setTranslation(curve1.getCV(curvePoint), ws=1)
				jointList.append(cl)

			# ctrl
			c = pm.circle(n='%s%s_ctrl' % (curve1.name(), curvePoint))
			pm.delete(pm.parentConstraint(cl, c, mo=0))
			pm.makeIdentity(c, apply=1)
			pm.parentConstraint(c, cl, mo=0)

	if skin == True:
		print 'skinning'
		pm.skinCluster(jointList, curve1, tsb=True, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
	return jointList


def alignJ(jnt1=None, jnt2=None, jnt3=None, viz=True):
	# align any 3 joints
	jnt1 = jnt1 or pm.selected()[0]
	jnt2 = jnt2 or pm.selected()[1]
	jnt3 = jnt3 or pm.selected()[2]

	# unparent
	jnt1P = jnt1.getParent()
	jnt1C = jnt1.getChildren()
	jnt2P = jnt2.getParent()
	jnt2C = jnt2.getChildren()
	jnt3P = jnt3.getParent()
	jnt3C = jnt3.getChildren()

	jnt1.setParent(world=True)
	jnt2.setParent(world=True)
	jnt3.setParent(world=True)

	allChildren = jnt1C + jnt2C + jnt3C
	for ch in allChildren:
		ch.setParent(world=True)

	jnt1pos = jnt1.getTranslation()
	jnt2pos = jnt2.getTranslation()
	jnt3pos = jnt3.getTranslation()

	# obtain xVec
	xVec = jnt3pos - jnt2pos
	if viz:
		vecViz(xVec, jnt2, name="xvec")

	oppVec = jnt1pos - jnt2pos  # vector pointing from jnt2 to up to jnt1
	if viz:
		vecViz(oppVec, jnt2, name="oppvec")

	zVec = oppVec.cross(xVec)  # cross producat
	if viz:
		vecViz(zVec, jnt2, name="zVec")

	yVec = xVec.cross(zVec)  # orthonormal basis
	if viz:
		vecViz(yVec, jnt2, name="yVec")

	# SHOULDER/Joint1
	xVec2 = jnt2pos - jnt1pos
	if viz:
		vecViz(xVec2, jnt1, name="xVec")
		# zVecs should be pointing in same direction since aligned
		vecViz(zVec, jnt1, "zVec")

	yVec2 = xVec2.cross(zVec)
	if viz:
		vecViz(yVec2, jnt1, name="yVec")

	# Matrix for proper joint alignment of ellbow
	# we used unnormalized matrices, which will cause problems when parenting
	# Homogenize - normalizes vectors

	jnt1M = pm.dt.Matrix(xVec2, yVec2, zVec, jnt1pos).homogenize()  # shoulder/joint1 Matrix

	jnt2M = pm.dt.Matrix(xVec, yVec, zVec, jnt2pos).homogenize()  # ellbow/joint2 Matrix

	jnt3M = pm.dt.Matrix(xVec, yVec, zVec, jnt3pos).homogenize()  # wrist same as ellbow

	jnt1.setMatrix(jnt1M)
	jnt2.setMatrix(jnt2M)
	jnt3.setMatrix(jnt3M)

	# set back into hierarcy
	# all joints have rotations now, we need to freeze rotations in order for them to function properly

	jnt1.setParent(jnt1P)
	pm.makeIdentity(jnt1, apply=True, t=False, r=True, s=False, n=False)
	jnt2.setParent(jnt2P)
	pm.makeIdentity(jnt2, apply=True, t=False, r=True, s=False, n=False)
	jnt3.setParent(jnt3P)
	pm.makeIdentity(jnt3, apply=True, t=False, r=True, s=False, n=False)

	for child in jnt1C:
		try:
			child.setParent(jnt1)
		except:
			_logger.debug("jnt 1 child no children to parent back in %s" % child)

	for child in jnt2C:
		try:
			child.setParent(jnt2)
		except:
			_logger.debug("jnt 1 child no children to parent back in %s" % child)

	for child in jnt3C:
		try:
			child.setParent(jnt3)
		except:
			_logger.debug("jnt 1 child no children to parent back in %s" % child)


# crates cone represenatation of vector based from tfm point
def vecViz(vector, tfm, name="vectorPoint"):
	"""Visual aid for Vectors"""
	vec = pm.dt.Vector(vector)
	grp = pm.group(em=True)
	loc = pm.spaceLocator()

	# cone for visulization
	pointer = pm.cone(name=name, esw=360, ch=1, d=1, hr=20, ut=0, ssw=0, s=3, r=0.25, tol=0.01, nsp=1, ax=(1, 0, 0))[0]

	# put locator and cone into group
	loc.setParent(grp)
	pointer.setParent(grp)

	# move locator to vetor
	loc.setTranslation(vec)

	# aim constrain cone to look at locator
	pm.delete(pm.aimConstraint(loc, pointer, aimVector=(1, 0, 0)))

	# pivot of cone is in center. for nicer look we shift it 2.5 to start right at the target. We have to move it in direction of the vector
	# so we get normalized vector (1 in lenth) and multiply it by 2.2
	vecNorm = vec.normal()
	pointer.translate.set(vecNorm * (2.5, 2.5, 2.5))

	# move cone to target position and clean up
	pm.delete(pm.pointConstraint(tfm, grp, mo=False))
	pointer.setParent(world=True)
	pm.delete(grp)

def vecVizObjects(objList,  name='vectorPoint'):
	'''
	need two objects, 1 for vector, 2 for baase
	'''
	if len(objList) == 0:
		return 'need at least 2 objects'
	vector = objList[0].getTranslation()
	return vecViz(vector, tfm=objList[1], name=name)



def jointOrDeleteHirarchy(node):
	children = pm.listRelatives(node, c=1, ni=1)
	for child in children:
		jointOrDeleteHirarchy(child)
	if not isinstance(node, pm.nodetypes.Joint) and len(children) is 0:
		pm.delete(node)
	else:
		print 'joint %s paretn %s' % (type(node), pm.listRelatives(node, p=1))
		p1 = pm.listRelatives(node, p=1, ni=1)
		if len(p1) is not 0 and not isinstance(p1[0], pm.nodetypes.Joint):
			p2 = pm.listRelatives(p1, p=1)
			if len(p2) is not 0:
				pm.parent(node, p2)


def getSkinInfluenceJoints():
	'''
	#Select skin influences of selected object
	Returns: skinJoints
	'''
	selGeo = pm.ls(sl=1)
	getSkin = pm.mel.findRelatedSkinCluster(selGeo[0])
	skinJoints = pm.listConnections(getSkin, type='joint')
	pm.select(skinJoints)
	return skinJoints


def addSkinAndBlendshape(objList=None):
	skingeoList = []
	if objList == None:
		objList = pm.ls(sl=1)
	for obj in objList:
		skingeo = pm.duplicate(obj, name='%s_skinGeo' % obj.name())
		skingeoList.append(skingeo)
		bs = pm.blendShape(obj, skingeo, n='%s_defBS' % obj.name(), foc=1)
		pm.blendShape(bs, e=1, w=(0, 1))

		jnt = pm.joint(n='%s_skinJnt' % obj.name(), radius=0.1)
		pm.parent(jnt, 'RIGG')  # grpIn
		pm.bindSkin(jnt, skingeo)
	return skingeoList


def cleanUpAttr(sel=None, listAttr=['sx', 'sy', 'sz', 'v'], l=1, k=1, cb=0):
	'''
	Args:
		sel:
		listAttr: ['sx', 'sy', 'sz', 'v']
		l: 1 lock attr , l=0 unlock attr
		k: 1  show attr ,k= 0 hide attr
		cb: 1 nonkeyable ,cb =0 make atte keyable
	Returns:
	riggUtil.cleanUpAttr(sel=[obj],listAttr=['sx', 'sy', 'sz', 'v'],l=0,k=0,cb=0)
	'''
	if sel == None:
		sel = pm.ls(sl=1)
	sel = pm.ls(sel)
	for obj in sel:
		# make pynode
		obj = pm.PyNode(obj)
		for attr in listAttr:
			if pm.objExists(obj + '.' + attr):
				obj.attr(attr).set(l=l, k=k, cb=cb)


def cleanTransforms(objArray=None):
	'''
	CutKey and delete Constraint
	Args:
		objArray:
	Returns:
	'''
	if objArray is None:
		objArray = pm.selected()

	for obj in objArray:
		try:
			pm.cutKey(obj)
		except:
			pass
	deleteChildrenConstraints(objArray)


def deleteChildrenConstraints(objList=None, allhierarchy=0):
	if objList == None:
		objList = pm.selected()
	if allhierarchy == 1:
		objList.append(pm.listRelatives(children=1, ad=1, type='transform'))
	pm.delete(pm.listConnections(objList, type='constraint'))


def connectScaleX(objArray=None):
	if objArray == None:
		objArray = pm.ls(sl=1)

	for obj in objArray:
		pm.connectAttr('%s.sx' % obj, '%s.sy' % obj)
		pm.connectAttr('%s.sx' % obj, '%s.sz' % obj)

	cleanUpAttr(sel=objArray, listAttr=['sy', 'sz'], l=1, k=1, cb=0)


def constrainAuto():
	c1 = pm.ls(sl=1)[0:-1]
	slave = pm.ls(sl=1)[-1].listRelatives(parent=1)
	pm.parentConstraint(c1, slave)

###############################
## create control at targetPos, constrain target if set to True
###############################
def createCtrl(targetPos=False, constrain=False, shape='box', size=1, color=None, suffix='ctrl'):
	if targetPos == False:
		targetPos = pm.ls(sl=1)
	for each in targetPos:
		name = '%s_%s'%(each.name(), suffix)
		controller = mo_curveLib.createShapeCtrl(shape, name, scale=size)
		#controller = pm.curve(p=[(size, size, size), (size, size, -size), (-size, size, -size), (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size), (-size, size, size), (size, size, size), (size, -size, size), (size, -size, -size), (-size, -size, -size), (-size, -size, size), (size, -size, size), (-size, -size, size), (-size, size, size)],k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],d=1,name=name)
		localgrp = pm.group(controller, n='%s_%s'%(each.name(), 'LOCAL'))
		zerogrp = pm.group(localgrp, n='%s_%s'%(each.name(), 'ZERO'))
		position = pm.xform(each,q=1,ws=1,rp=1)
		
		zerogrp.setTranslation(position, ws=True)
		pm.delete(pm.orientConstraint(each, zerogrp, weight=1, offset=(0, 0, 0)))
		
		if constrain == True:
				pm.parentConstraint(controller, each)
				
		if color is not None:
			 mo_curveLib.colorOverride(controller, color)




###############################
## create control for each cv on cuve
## create joint and skin if True
## return list of ctrl shape
###############################
def createCvControls(curves=None, shape='sphere', size=1, addNode='joint', suffix='skinJnt', skin=False, everyXCv=1):
	cvSpecific = None
	if curves == None:
		curves = pm.ls(sl=1)

	if not isinstance(curves, list):
		curves = [curves]
	if isinstance(curves[0], pm.NurbsCurveCV):
		cvSpecific = pm.ls(curves, fl=1)
		curvename = curves[0].split('.')[0]

	jointList = []
	ctrlZeroList = []
	print curves
	for curve1 in curves:
		if isinstance(curve1, pm.nodetypes.Transform):
			curve1 = curve1.getShape()
		if isinstance(curve1, str):
			curve1 = pm.PyNode(curve1)
			if isinstance(curve1, pm.nodetypes.Transform):
				curve1 = curve1.getShape()
		if isinstance(curve1, pm.NurbsCurveCV):
			curve1 = pm.PyNode(curvename)
		if cvSpecific is not None:
			curvePoints = len(cvSpecific)
		else:
			curvePoints = curve1.numCVs()
			curvename = pm.listRelatives(curve1, parent=1, type='transform')[0].name()

		for curvePoint in range(curvePoints):
			# skip
			if curvePoint % everyXCv is not 0:
				continue
			if cvSpecific is not None:
				curvePoint = int(cvSpecific[curvePoint].split('.')[1][3:-1])
				print 'this is point of corresponding cv %s' % curvePoint
			print 'creating cluster for cv %s' % curvePoint
			# select matching cv
			pm.select(clear=1)

			# joint
			if addNode == 'joint':
				cl = pm.joint(n='%s%s_%s' % (curvename, curvePoint, suffix))
				cl.setTranslation(curve1.getCV(curvePoint), ws=1)
				jointList.append(cl)

			# cluster
			else:
				pm.select(curve1.cv[curvePoint])
				cl = pm.cluster(n='%s_cluster' % curvename)

			# ctrl
			c = mo_curveLib.createShapeCtrl(shape, name='%s%2d_ctrl' % (curvename, curvePoint), scale=size)
			# c= pm.circle(n='%s%2d_ctrl'%(curvename, curvePoint))

			cAuto = pm.group(c, n='%s%2d_AUTO' % (curvename, curvePoint))
			cZero = pm.group(cAuto, n='%s%2d_ZERO' % (curvename, curvePoint))
			ctrlZeroList.append(cZero)

			pm.delete(pm.parentConstraint(cl, cZero, mo=0))
			if (addNode is None):
				pm.delete(cl)
			else:
				pm.parent(cl, c)

		if skin == True:
			print 'skinning'
			pm.skinCluster(jointList, curve1, tsb=True, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
		return ctrlZeroList
		'''
	sys.path.append('/run/media/monikadell/Data/My3DWork/PythonScripting/scripts/')
	import mo_Utils.mo_riggUtils as mo_riggUtils
	reload(mo_riggUtils)
	mo_riggUtils.createCvControls(curves='curve2', ctrl='cluster')
	'''


def createJointOnComponent(components=None, skin=False, suffix='jnt'):
	if components == None:
		components = pm.ls(sl=1, fl=1)
	cvSpecific = None
	jointList = []
	nodename = components[0].split('.')[0]
	i = 0
	for component in components:
		pm.select(clear=1)
		pm.select(component)
		temp = pm.cluster()
		pm.select(clear=1)
		# joint
		cl = pm.joint(n='%s%s_%s' % (nodename, i, suffix))
		pm.delete(pm.parentConstraint(temp, cl))
		jointList.append(cl)
		pm.delete(temp)
		i = i + 1
	if skin == True:
		print 'skinning'
		pm.skinCluster(jointList, nodename, tsb=True, maximumInfluences=4, normalizeWeights=1, obeyMaxInfluences=True)
	return jointList


def getChildJoint(joint=None, allDescendents=False):
	if joint == None:
		joint = pm.ls(sl=1)
	elif type(joint) == str:
		joint - [joint]
	tmp = []
	tmp = pm.listRelatives(joint, c=(not allDescendents), ad=allDescendents, type='joint', f=1)
	return (tmp)


def getJointAxis(child):
	print child.name()
	axis = ""
	t = [0.0] * (0)
	t = pm.getAttr("%s.t" % child.name())
	# get the translation values of the $child joint
	# now check and see which one is greater than 0.  We should have a tolerance value just in case
	tol = 0.0001
	for x in range(0, 2 + 1):
		if (t[x] > tol) or (t[x] < (-1 * tol)):
			if x == 0:
				axis = "x"
			elif x == 1:
				axis = "y"
			elif x == 2:
				axis = "z"
	if axis == "":
		pm.pm.mel.error(
			"The child joint is too close to the parent joint. Cannot determine the proper axis to segment.")

	return axis


def getTransformations(t=True, r=False, world=1):
	sel = pm.ls(sl=True)
	if (len(sel) < 1):
		print ("Error. Select objects you want to get translation values from")
		return False
	i = 1
	tList = []
	tPrint = ""
	rList = []
	rPrint = ""

	for each in sel:
		position = pm.xform(each, q=1, ws=world, rp=1)
		tList.append(position)
		tPrint = tPrint + "pos%s = %s\n" % (i, position)
		if (r == True):
			rList.append(each.getRotation())
			rPrint = rPrint + "rot%s = %s\n" % (i, each.getRotation())
		i = i + 1
	print tPrint
	print rPrint
	return tList, rList


# Select skin influences of selected object
def getSkinInfluenceJoints(select=True):
	selGeo = pm.ls(sl=1)
	getSkin = pm.mel.findRelatedSkinCluster(selGeo[0])
	skinJoints = pm.listConnections(getSkin, type='joint')
	if select: pm.select(skinJoints)
	return skinJoints
	'''sys.path.append('/run/media/monikadell/Data/My3DWork/PythonScripting/scripts/mo_Utils/')
	import mo_riggUtils as riggUtils
	reload(riggUtils)
	riggUtils.getSkinInfluenceJoints()'''


def getJointChain(startJoint=None, endJoint=None):
	'''
	Return the all the joints in the chain using start/end
	@param startJoint: start of chain
	@param endJoint: end of chain
	@return Return the all the joints in the chain using start/end
	'''
	if startJoint == None:
		startJoint = pm.ls(sl=1)[0]
	if endJoint == None:
		endJoint = pm.ls(sl=1)[1]

	startJntLP = pm.ls(startJoint, long=True)[0]
	endJntParentsList = [endJoint]
	endJntParent = endJoint

	while (endJntParent != None):
		endJntParent = pm.listRelatives(endJntParent, parent=True, fullPath=True)[0]
		if endJntParent:
			endJntParentsList.append(endJntParent)
		if endJntParent == startJntLP:
			break
	if not startJntLP in endJntParentsList:
		print("%s is not a parent of %s" % (startJntLP, endJoint))
	else:
		endJntParentsList.reverse()
		return endJntParentsList


def getRotOrderString(joint):
	return_ = ""
	ro = 0
	ro = int(pm.getAttr("%s.ro" % joint))
	if ro == 0:
		return_ = "xyz"
	elif ro == 1:
		return_ = "yzx"
	elif ro == 2:
		return_ = "zxy"
	elif ro == 3:
		return_ = "xzy"
	elif ro == 4:
		return_ = "yxz"
	elif ro == 5:
		return_ = "zyx"
	return return_


#
def grpIn(grpName, obj):
	'''
	makes creates and adds objects to a grp
	riggUtils.grpIn('myGrp', 'objA')
	Args:
		grpName:
		obj:

	Returns:

	'''
	if pm.objExists(grpName):
		grp = grpName
	else:
		grp = pm.createNode('transform', n=grpName)

	if len(pm.listRelatives(obj, p=1)) != 0:
		if pm.listRelatives(obj, p=1)[0] != grpName:
			pm.parent(obj, grp)
	else:
		pm.parent(obj, grp)


def lockGrpCtrl(ctrl=None, lock=1, hide=1):
	if ctrl == None:
		ctrl = pm.ls(sl=1)[0]
	ctrl = pm.ls(ctrl)[0]
	if lock:
		for node in ['ZERO', 'AUTO']:
			pm.PyNode(ctrl.attr(node).get()).t.lock()
			pm.PyNode(ctrl.attr(node).get()).r.lock()
			pm.PyNode(ctrl.attr(node).get()).s.lock()

	if hide:
		for node in ['ZERO', 'AUTO']:
			pm.PyNode(ctrl.attr(node).get()).t.setKeyable(0)
			pm.PyNode(ctrl.attr(node).get()).t.showInChannelBox(0)
			pm.PyNode(ctrl.attr(node).get()).r.setKeyable(0)
			pm.PyNode(ctrl.attr(node).get()).r.showInChannelBox(0)
			pm.PyNode(ctrl.attr(node).get()).s.setKeyable(0)
			pm.PyNode(ctrl.attr(node).get()).s.showInChannelBox(0)


def addGimbal(ctrl=None):
	"""
	Creates an offset child ctrl by duplicating ctrl
	Connect visibility to attribute gimal_vis
	Args:
		ctrl:
	"""
	ctrl = pm.ls(ctrl)[-1]
	_logger.debug( 'Adding gimbal to %s'%ctrl)

	# duplicate ctrl and delete children  or connect vis
	gimbalCtrl = pm.duplicate(ctrl, n=ctrl.replace('Ctrl', '') + 'GimbalCtrl')[0]

	pm.addAttr(ctrl, ln='gimbal_vis', at='bool', k=1)

	for child in gimbalCtrl.getChildren():
		if type(child) != pm.nodetypes.NurbsCurve: pm.delete(child)
		else: ctrl.gimbal_vis >> child.visibility

	pm.parent(gimbalCtrl, ctrl)

	# scale
	pm.xform('%s.cv[0:]' % gimbalCtrl.getShape(), s=(.8, .8, .8), r=1)

	# add memory
	pm.addAttr(ctrl, ln='gimbal', dt='string')
	ctrl.attr('gimbal').set('%s' % gimbalCtrl, k=0, l=0, type='string')

	return gimbalCtrl


def grpCtrl(ctrl=None, sdk=0):

	if ctrl == None:
		ctrl = pm.ls(sl=1)[0]
	ctrl = pm.ls(ctrl)[0]

	_logger.info('grpCtrl: %s'%ctrl)

	rotOrder = ctrl.attr('rotateOrder').get()
	nameSplit = ctrl.split('_')

	if nameSplit[-1] == 'ctrl':
		auto = '_'.join(nameSplit[:-1]) + '_AUTO'
		zero = '_'.join(nameSplit[:-1]) + '_ZERO'
	else:
		auto = '%s_AUTO' % ctrl
		zero = '%s_ZERO' % ctrl

	cAuto = pm.createNode('transform', n=auto)
	cAuto.attr('rotateOrder').set(rotOrder)

	cZero = pm.createNode('transform', n=zero)
	cZero.attr('rotateOrder').set(rotOrder)

	# create  attr Memory
	# pm.addAttr(cZero, ln='ctrl', dt='message')
	# pm.addAttr(cAuto, ln='ctrl', dt='message')
	# pm.addAttr(ctrl, ln='auto', dt='message')
	# pm.addAttr(ctrl, ln='ZERO', dt='message')
	# cZero.ctrl >> ctrl.zero

	# ZERO obj
	pm.addAttr(zero, ln='obj', dt='string')
	cZero.attr('obj').set('%s' % ctrl, k=0, l=0, type='string')
	# AUTO obj
	pm.addAttr(auto, ln='obj', dt='string')
	cAuto.attr('obj').set('%s' % ctrl, k=0, l=0, type='string')
	# obj
	pm.addAttr(ctrl, ln='ZERO', dt='string')
	pm.addAttr(ctrl, ln='AUTO', dt='string')
	ctrl.attr('ZERO').set('%s' % cZero, k=0, l=0, type='string')
	ctrl.attr('AUTO').set('%s' % cAuto, k=0, l=0, type='string')

	# parent

	listParent = pm.listRelatives(ctrl, p=1, typ='transform')

	if len(listParent) > 0:
		pm.parent(zero, listParent[0])

	# snap

	pm.delete(pm.parentConstraint(ctrl, auto))
	pm.delete(pm.parentConstraint(ctrl, zero))
	pm.parent(auto, zero)
	pm.parent(ctrl, auto)

	if sdk == 1:
		_logger.info('creting sdk')
		sdk = pm.duplicate(auto, n=auto.replace('_AUTO', '_SDK'), po=1)[0]
		pm.parent(sdk, auto)
		pm.parent(ctrl, sdk)

	# set nonKeyAble
	grp = [zero, auto, ctrl]
	return cZero


def jointOrDeleteHirarchy(node=None):
	if node == None:
		node = pm.ls(sl=1)[0]
	children = pm.listRelatives(node, c=1, ni=1)
	for child in children:
		jointOrDeleteHirarchy(child)
	if not isinstance(node, pm.nodetypes.Joint) and len(children) is 0:
		pm.delete(node)
	else:
		print 'joint %s paretn %s' % (type(node), pm.listRelatives(node, p=1))
		p1 = pm.listRelatives(node, p=1, ni=1)
		if len(p1) is not 0 and not isinstance(p1[0], pm.nodetypes.Joint):
			p2 = pm.listRelatives(p1, p=1)
			if len(p2) is not 0:
				pm.parent(node, p2)


def latticeRigg3():
	objList = pm.ls(sl=1)
	for obj in objList:
		name = obj.name()
		pm.select(obj)
		lattic = pm.lattice(divisions=(3, 2, 3), cp=1, ldv=(3, 2, 3), objectCentered=True, n='%s_lattice' % name)
		x = 0
		for x in range(3):
			pm.select(clear=1)
			y = 0;
			for y in range(3):
				pm.select('%s.pt[%s][0:1][%s]' % (lattic[1], x, y))
				cl = pm.cluster(n='%s%02d%02d_cluster' % (name, x, y))
				mo_riggUtils.createCtrl([cl[1]], connect='parent')  # createCtrl
		return lattic


def orientJointWarning(joint, rotationOrder, axis, firstChar):
	message = ("Warning!!!!\n\n")
	message += ("The rotation order and joint orient for " + joint + " do not match up.\n")
	message += ("The rotation order is: " + rotationOrder + "\n")
	message += ("The axis aiming down the joint is: " + axis + "\n\n")
	message += ("Either change axis that aims down the joint to " + firstChar + ", or switch the rotation order to ")
	if axis == "x":
		message += ("xyz or xzy.\n")
	elif axis == "y":
		message += ("yxz or yzx.\n")
	elif axis == "z":
		message += ("zxy or zyx.\n")
	message += ("\nSkipping Joint: " + joint + "...\n")
	pm.confirmDialog(ma="left", m=message)
	pm.warning(message)


###############################
## scale shape node by factor
###############################
def scaleShape(factor, objs=None, axis='XYZ'):
	if objs == None:
		if len(pm.ls(sl=1)) < 1:
			return False
		objs = pm.ls(sl=1)
	factors = [factor, factor, factor]
	print 'Scaling: Axis is %s'%axis
	if axis != 'XYZ':
		if 'X' not in axis:
			factors[1] = 1
		if 'Y' not in axis:
			factors[2] = 1
		if 'Z' not in axis:
			factors[0] = 1
	for obj in objs:
		if obj.type() == 'transform':
			shapenode = obj.getShape()
		else:
			shapenode = obj
		pm.select(shapenode.cv[0:shapenode.numCVs() - 1])
		pm.scale(factors[0], factors[1], factors[2])
	pm.select(objs)


###############################
##   create ikSpline solver
###############################
def splineIK(startJoint=None, endJoint=None, curve=None, name=None):
	if startJoint == None:
		startJoint = pm.ls(sl=1)[0]
	if endJoint == None:
		endJoint = pm.ls(sl=1)[1]
	if curve == None and len(pm.ls(sl=1)) > 2:
		curve = pm.ls(sl=1)[2]
	else:
		return pm.ikHandle(startJoint=startJoint, ee=endJoint, ccv=True, solver='ikSplineSolver',
						   name=startJoint.name())
	if name == None:
		name = '%s_ikSpline' % curve.name()
	return pm.ikHandle(startJoint=startJoint, ee=endJoint, curve=curve, ccv=False, solver='ikSplineSolver', name=name)


###############################
## adds twist, roll and reverseTwist to spline IK
###############################
def splineIKTwistCtrls(ctrl=None, ikSpline=None, attr=['ik_twist', 'ik_revTwist', 'ik_roll']):
	if ctrl == None:
		ctrl = pm.ls(sl=1)[0]
	if ikSpline == None:
		ikSpline = pm.ls(sl=1)[1]

	attr_twist = attr[0]
	attr_revTwist = attr[1]
	attr_roll = attr[2]

	pm.addAttr(ctrl, ln=attr_twist, sn='twist', k=1)
	pm.addAttr(ctrl, ln=attr_revTwist, sn='revTwist', k=1)
	pm.addAttr(ctrl, ln=attr_roll, sn='roll', k=1)

	pma_twist_rev = pm.shadingNode('plusMinusAverage', n='twistRev_pma', asUtility=1)
	pma_roll_rev = pm.shadingNode('plusMinusAverage', n='rollRev_pma', asUtility=1)
	mpd_rev = pm.shadingNode('multiplyDivide', n='multRev_mpd', asUtility=1)

	# twist - multiplydivide - reverse value
	pm.setAttr('%s.input2X' % mpd_rev, -1)
	pm.connectAttr('%s.%s' % (ctrl, attr_revTwist), '%s.input1X' % mpd_rev)

	pm.connectAttr('%s.%s' % (ctrl, attr_twist), '%s.input1D[0]' % pma_twist_rev)
	pm.connectAttr('%s.outputX' % mpd_rev, '%s.input1D[1]' % pma_twist_rev)

	# roll
	pm.connectAttr('%s.%s' % (ctrl, attr_roll), '%s.input1D[0]' % pma_roll_rev)
	pm.connectAttr('%s.%s' % (ctrl, attr_revTwist), '%s.input1D[1]' % pma_roll_rev)

	# connect to ikSpline
	pm.connectAttr('%s.output1D' % pma_twist_rev, '%s.twist' % ikSpline)
	pm.connectAttr('%s.output1D' % pma_roll_rev, '%s.roll' % ikSpline)
	pm.connectAttr('%s.%s' % (ctrl, attr_roll), '%s.roll' % ikSpline)


###############################
##   splineIKScaleJoints
##   Desc:    Scales the joints of a splineIK
###############################
def splineIKScaleJoints(curve, axis, joints):
	# get the shape of the curve
	curveShape = pm.listRelatives(curve, s=1, f=1)[0]
	# create curveInfo and connect curve
	curveInfo = str(pm.createNode('curveInfo', name=("nodeCurveInfo_" + curve + "Info")))
	pm.connectAttr((curveShape + ".worldSpace[0]"), (curveInfo + ".inputCurve"))
	# getting arc length
	arcLength = float(pm.getAttr(curveInfo + ".arcLength"))
	# multiplyDivide node, opearation divide
	curveScale = str(pm.createNode('multiplyDivide', name=("nodeMultiplyDiv_" + curve + "Scale")))
	pm.setAttr((curveScale + ".operation"), 2)
	# connect input1X to  arcLength
	pm.connectAttr((curveInfo + ".arcLength"), (curveScale + ".input1X"))
	# set original arcLength
	pm.setAttr((curveScale + ".input2X"), arcLength)
	# create a multiplyDivide for each joint and scale the length of them
	for joint in joints:
		# current length of the bone
		length = float(pm.getAttr(joint + "." + axis))
		# create the multiply divide node
		jointScale = str(pm.createNode('multiplyDivide', name=("nodeMultiplyDiv_" + joint + "Scale")))
		# connect $curveScale.outputX to $jointScale.input1X;
		pm.connectAttr((curveScale + ".outputX"), (jointScale + ".input1X"))
		# set the $jointScale.input2X to the current length
		pm.setAttr((jointScale + ".input2X"), length)
		# connect the $jointScale.outputX to the length of the $joint;
		pm.connectAttr((jointScale + ".outputX"), (joint + "." + axis), f=1)


###############################
## Splits the selected joint into the specified number of segments
###############################
def splitJnt(numSegments, joints=None):
	if numSegments < 2:
		pm.error("The number of segments has to be greater than 1.. ")

	# for all selected joints
	joint = None
	if joints == None:
		joints = pm.ls(sl=1, type='joint')
	print joints
	for joint in joints:

		prevJoint = joint
		child = getChildJoint(joint)
		if child == []:
			print("Joint: " + str(joint) + " has no children joints.\n")
			continue

		else:
			child = child[0]
			# axis
			radius = pm.getAttr("%s.radius" % joint)
			axis = getJointAxis(child)

			# make sure the rotation order on $joint is correct.
			rotOrderIndex = int(pm.getAttr("%s.rotateOrder" % joint))

			# calculate spacing
			attr = ("t" + axis)
			childT = pm.getAttr("%s.%s" % (child, attr))
			print 'childT is %s' % childT
			space = childT / numSegments

			# create a series of locators along the joint based on the number of segments.
			locators = []
			for x in range(0, (numSegments - 1)):
				# align locator to joint

				locator = pm.spaceLocator()
				locators.append(locator)

				pm.parent(locator, joint)

				pm.setAttr("%s.t" % locator, (0, 0, 0))
				# offset
				pm.setAttr("%s.%s" % (locator, attr), (space * (x + 1)))
				# insert a joint
				newJoint = pm.PyNode(pm.insertJoint(prevJoint))
				# get the position of the locator
				position = pm.xform(locator, q=1, rp=1, ws=1)
				print  position
				# move the joint there
				pm.move(position, ws=1, pcp=1)
				print radius
				print axis

				pm.setAttr("%s.radius" % newJoint, radius)
				pm.setAttr("%s.rotateOrder" % newJoint, rotOrderIndex)

				prevJoint = newJoint
				pm.delete(locator)
			pm.select(joint)
			mo_stringUtils.renameHierarchy()
		return


def stretchyIK(chain, startDrv, endDrv, poleVec=None):
	sys.path.append('/run/media/monikadell/Data/My3DWork/PythonScripting/scripts/thirdParty/')
	import nVec
	# declaring initial vectors
	startV = nVec.NVec("%s.worldPosition" % startDrv, "sStretch")
	endV = nVec.NVec("%s.worldPosition" % endDrv, "eStretch")
	stretchV = nVec.NScalar("%s.stretch" % endDrv, "stretch")

	pm.addAttr('end_drv', ln='stretch', at='double', min=0, max=1, k=1)

	# computing the length between the end and the start of the chain
	distV = endV - startV
	length = distV.length()

	# getting initial chain length and converting into vectors
	upLen = cmds.getAttr(chain[1] + '.tx')
	lowLen = cmds.getAttr(chain[2] + '.tx')

	# here we create two working vector from static values
	# the static value will be hardcoded in a transfomr channel
	# and a NScalar instance will be returned
	upLenV = nVec.NScalar.from_value(upLen, "upLen")
	lowLenV = nVec.NScalar.from_value(lowLen, "lowLen")

	# getting total length chain (this can be easily multiplied by the global scale)
	initLen = upLenV + lowLenV

	# finding theratio
	ratio = length / initLen

	# calculating scaled length
	scaledUp = upLenV * ratio
	scaledlow = lowLenV * ratio

	# computing final blended stretch
	finalScaledUp = upLenV.blend(scaledUp, stretchV)
	finalScaledLow = lowLenV.blend(scaledlow, stretchV)

	# condition node (old school)
	cnd = cmds.createNode("condition")
	ratio.connect_to(cnd + '.firstTerm')
	cmds.setAttr(cnd + '.secondTerm', 1)
	cmds.setAttr(cnd + '.operation', 3)

	# connecting our final calculaded stretch node to the cnd colors
	finalScaledUp.connect_to(cnd + '.colorIfTrueR')
	upLenV.connect_to(cnd + '.colorIfFalseR')
	finalScaledLow.connect_to(cnd + '.colorIfTrueG')
	lowLenV.connect_to(cnd + '.colorIfFalseG')

	if poleVec == None:
		cmds.connectAttr(cnd + '.outColorR', chain[1] + '.tx')
		cmds.connectAttr(cnd + '.outColorG', chain[2] + '.tx')
		return True
	else:
		# compute the pole vector lock
		pm.addAttr(endDrv, ln='lock', at='double', min=0, max=1)

		poleV = nVec.NVec("poleVec_drv.worldPosition", "pStretch")
		lockV = nVec.NScalar("end_drv.lock", "lock")

		# get polevec vectors
		upPoleVec = poleV - startV
		lowPoleVec = poleV - endV

		# computing the length
		upPoleLen = upPoleVec.length()
		lowPoleLen = lowPoleVec.length()

		# blending default length with poleVec vectors
		upPoleBlen = upLenV.blend(upPoleLen, lockV)
		lowPoleBlen = lowLenV.blend(lowPoleLen, lockV)

		# connecting a NScalar to the output of the node
		finalStrUp = nVec.NScalar(cnd + '.outColorR')
		finalStrLow = nVec.NScalar(cnd + '.outColorG')

		# blending the stretch and lock lengths
		resUp = finalStrUp.blend(upPoleBlen, lockV)
		resLow = finalStrLow.blend(lowPoleBlen, lockV)

		# connect final result
		resUp.connect_to(chain[1] + '.tx')
		resLow.connect_to(chain[2] + '.tx')
		return True


class Ctrl():
	def __init__(self):
		print 'Creating control'
		self.name = ''
		self.auto = ''
		self.zero = ''
		self.basename = ''
		self.gimbal = None
		self.size = ''
		self.color = ''
		self.target = ''

	def define(self, ctrl):
		ctrl = pm.ls(ctrl)[-1]  # pynode

		self.name = ctrl.name()

		try:
			self.auto = ctrl.att('AUTO')
		except:
			self.auto = ctrl.getParent()

		try:
			self.zero = ctrl.att('ZER0')
		except:
			self.zero = self.auto.getParent()

		try:
			self.gimbal = ctrl.att('gimbal')
		except:
			children = ctrl.getChildren(type='transform')
			for child in children:
				if child.split('_')[-1] == 'gimbalCtrl':
					gimbal = child.name()
					

	def createOnObj(self, obj=False, constrain=False, shape='box', size=1, color=(), suffix='ctrl'):
		if obj == False:
			obj = pm.ls(sl=1)[-1]
		name = '%s_%s' % (obj.name(), suffix)
		controller = mo_curveLib.createShapeCtrl(shape, name, scale=size)
		# controller = pm.curve(p=[(size, size, size), (size, size, -size), (-size, size, -size), (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size), (-size, size, size), (size, size, size), (size, -size, size), (size, -size, -size), (-size, -size, -size), (-size, -size, size), (size, -size, size), (-size, -size, size), (-size, size, size)],k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],d=1,name=name)
		localgrp = pm.group(controller, n='%s_%s' % (obj.name(), 'LOCAL'))
		zerogrp = pm.group(localgrp, n='%s_%s' % (obj.name(), 'ZERO'))
		position = pm.xform(obj, q=1, ws=1, rp=1)

		zerogrp.setTranslation(position, ws=True)
		pm.delete(pm.orientConstraint(obj, zerogrp, weight=1, offset=(0, 0, 0)))

		if constrain == True:
			pm.parentConstraint(controller, obj, n=name+'_parentConst', mo=1)
			pm.scaleConstraint(controller, obj, n=name+'_scaleConst', mo=1)
		print('color is %s'%color)
		if len(color)>0:
			controller = pm.PyNode(controller)
			print('controller is %s'%controller)
			mo_curveLib.setRGBColor(controller.getShape(), color)

	def connect(self):
		target = self.name.replace('_ctrl', '')
		controller = self.name
		if pm.objExists(target):
			pm.parentConstraint(controller, target, n=self.name+'_parentConst', mo=1)
			pm.scaleConstraint(controller, target, n=self.name+'_scaleConst', mo=1)
		else:
			print 'Error conencting. Target object not found'
	def disconnect(self):
		target = self.name.replace('_ctrl', '')
		controller = self.name
		if pm.objExists(target):
			deleteChildrenConstraints(target)
		else:
			print 'Error diconencting. Target object not found'
	def group(self, ctrl=None):
		cZero = grpCtrl(ctrl)
		return cZero


def makeExportable(sel=None, setName='ctrlSet'):
	# make attr for export
	if sel == None:
		sel = pm.ls(sl=1)
	for obj in sel:
		if pm.objExists(obj + '.CTRL'):
			pm.setAttr((obj + '.CTRL'), l=0)
			pm.deleteAttr(obj, at='CTRL')
		if pm.objExists(obj + '.xprt'):
			pm.setAttr((obj + '.xprt'), l=0)
			pm.deleteAttr(obj, at='xprt')
		pm.addAttr(obj, ln='CTRL', dt='string')
		pm.setAttr((obj + '.CTRL'), 'yes', k=0, l=1, type='string')
		pm.addAttr(obj, ln='xprt', dt='string')
		pm.setAttr((obj + '.xprt'), 'yes', k=0, l=1, type='string')
		setIn(setName, obj)


def movePivot(scr=None, tar=None):
	if scr == None:
		sel = pm.ls(sl=1)
		scr = sel[0]
		tar = sel[1]
	scale = pm.xform(scr, q=1, ws=1, scalePivot=1)
	rotate = pm.xform(scr, q=1, ws=1, rotatePivot=1)

	pm.xform(tar, ws=1, scalePivot=(scale[0], scale[1], scale[2]))
	pm.xform(tar, ws=1, rotatePivot=(rotate[0], rotate[1], rotate[2]))
	pm.select(tar, r=1)


def setIn(setName, obj):
	'''
	makes and adds object to set
	'''
	pm.select(cl=True)
	if pm.objExists(setName):
		mySet = setName
		pm.sets(mySet, add=obj)
	else:
		mySet = pm.sets(n=setName)
		pm.sets(mySet, add=obj)


def setOut(setName, obj):
	pm.select(cl=True)
	if pm.objExists(setName):
		mySet = setName
		pm.sets(mySet, rm=obj)


def disableAndStoreConstraintWeights(object):
	'''
	If constraints exist, turn off and return constrainList and weights
	Args:
		object:

	Returns:

	'''
	constraints = pm.listConnections(object, type='constraint')
	constList = []
	weightSaver = []
	for constraint in constraints:
		if constraint not in constList:
			constList.append(constraint)
			weights = constraint.getWeightAliasList()
			for weight in weights:
				weightSaver.append(weight.get())
				weight.set(0)

	return constList, weightSaver


def restoreConstraintWeights(object, constList, weightSaver):
	for constraint in constList:
		weights = constraint.getWeightAliasList()
		for weight in weights:
			weight.set(weightSaver.pop())


def duplicateLimbLimited(upperArmJnt, lowerArmJnt, wristJnt, hingelimit=(1, 178), constrainToOriginal=1):
	'''
	Duplicate joints with rotation limits
	Args:
		upperArmJnt:
		lowerArmJnt:
		wristJnt:
		hingelimit:
		constrainToOriginal:

	Returns:

	'''

	upperArmPoleJnt = pm.duplicate(upperArmJnt, n=upperArmJnt + 'Pole', po=1)[0]
	pm.parent(upperArmPoleJnt, w=1)
	lowerArmPoleJnt = pm.duplicate(lowerArmJnt, n=lowerArmJnt + 'Pole', po=1)[0]
	pm.parent(lowerArmPoleJnt, upperArmPoleJnt)
	wristPoleJnt = pm.duplicate(wristJnt, n=wristJnt + 'Pole', po=1)[0]
	pm.parent(wristPoleJnt, lowerArmPoleJnt)

	# set limits
	print lowerArmPoleJnt
	jointOrient = pm.getAttr("%s.jointOrientY" % lowerArmJnt)
	pm.transformLimits(lowerArmPoleJnt, ry=(hingelimit[0] + jointOrient, hingelimit[1] + jointOrient), ery=(1, 1))

	if constrainToOriginal:
		pm.parentConstraint(upperArmJnt, upperArmPoleJnt, mo=0)
		pm.parentConstraint(lowerArmJnt, lowerArmPoleJnt, mo=0)
		pm.parentConstraint(wristJnt, wristPoleJnt, mo=0)

	return [upperArmPoleJnt, lowerArmPoleJnt, wristPoleJnt]


def distanceNode(pt1,
				 pt2,
				 prefix=None):
	'''
	Build distance node between 2 specified transforms.
	@param pt1: Transform 1 in distance calculation
	@type pt1: str
	@param pt2: Transform 2 in distance calculation
	@type pt2: str
	'''
	# ==========
	# - Checks -
	# ==========

	if not pm.objExists(pt1): raise Exception('Point 1 "' + pt1 + '" does not exist!')
	# if not glTools.utils.transform.isTransform(pt1):raise Exception('Point 1 "'+pt1+'" is not a valid tranform!')
	if not pm.objExists(pt2): raise Exception('Point 2 "' + pt2 + '" does not exist!')
	# if not glTools.utils.transform.isTransform(pt2):raise Exception('Point 2 "'+pt2+'" is not a valid tranform!')

	# ========================
	# - Build Distance Setup -
	# ========================

	distNode = pm.createNode('distanceBetween', n=prefix + '_distanceBetween')
	pm.connectAttr(pt1 + '.worldMatrix[0]', distNode + '.inMatrix1', f=True)
	pm.connectAttr(pt2 + '.worldMatrix[0]', distNode + '.inMatrix2', f=True)

	# =================
	# - Return Result -
	# =================

	return distNode


def poleVectorPositionMvector(helpers, poleVectorDistance=5.0):
	'''

	makeIkPlaneSetup(cmds.ls(sl=True))
	Args:
		helpers: shoulder, ellbow and wrist joint
		poleVectorDistance:

	Returns:

	'''
	from maya import cmds
	import maya.api.OpenMaya as om

	if len(helpers) != 3:
		raise Exception(
			'makeIkPlaneSetup input error, you need objects to pull positions from there were %s inputs\n' % len(
				helpers))

	shld = om.MVector(cmds.xform(helpers[0], q=True, ws=True, t=True))
	elbow = om.MVector(cmds.xform(helpers[1], q=True, ws=True, t=True))
	wrist = om.MVector(cmds.xform(helpers[2], q=True, ws=True, t=True))

	# figure out the upNode (plane direction)
	planeX = wrist - shld
	planeXL = planeX.length()

	armDis = (elbow - shld).length()
	foreArmDis = (wrist - elbow).length()
	fraction = armDis / (foreArmDis + armDis)
	planeP = shld + (planeX.normalize() * (planeXL * fraction))
	upNode = (elbow - planeP).normalize()

	pvPos = shld + (upNode * poleVectorDistance)

	# shoulder orintation matrix
	shdXAxis = (elbow - shld).normalize()
	shdYAxis = (upNode ^ shdXAxis).normalize()  # cross product a noramalize....
	shdZAxis = (shdXAxis ^ shdYAxis).normalize()  # cross product a noramalize....

	shldM = om.MMatrix([[shdXAxis.x, shdXAxis.y, shdXAxis.z, 0],
						[shdYAxis.x, shdYAxis.y, shdYAxis.z, 0],
						[shdZAxis.x, shdZAxis.y, shdZAxis.z, 0],
						[shld.x, shld.y, shld.z, 1]])

	elbowXAxis = (wrist - elbow).normalize()
	elbowYAxis = shdYAxis
	elbowZAxis = (elbowXAxis ^ elbowYAxis).normalize()

	elbowM = om.MMatrix([[elbowXAxis.x, elbowXAxis.y, elbowXAxis.z, 0],
						 [elbowYAxis.x, elbowYAxis.y, elbowYAxis.z, 0],
						 [elbowZAxis.x, elbowZAxis.y, elbowZAxis.z, 0],
						 [elbow.x, elbow.y, elbow.z, 1]])

	wristM = om.MMatrix([[elbowXAxis.x, elbowXAxis.y, elbowXAxis.z, 0],
						 [elbowYAxis.x, elbowYAxis.y, elbowYAxis.z, 0],
						 [elbowZAxis.x, elbowZAxis.y, elbowZAxis.z, 0],
						 [wrist.x, wrist.y, wrist.z, 1]])

	pvM = om.MMatrix([[shdXAxis.x, shdXAxis.y, shdXAxis.z, 0],
					  [shdYAxis.x, shdYAxis.y, shdYAxis.z, 0],
					  [shdZAxis.x, shdZAxis.y, shdZAxis.z, 0],
					  [pvPos.x, pvPos.y, pvPos.z, 1]])

	# convert matrix values to list for xform input
	shldML = [v for v in shldM]
	elbowML = [v for v in elbowM]
	wristML = [v for v in wristM]
	pvML = [v for v in pvM]

	# make pole vector point
	pv = cmds.spaceLocator()
	cmds.select(
		clear=True)  # we'll keep joints parented to avoid rotation offset which maya creates when parenting joints post creation

	shldJ = cmds.joint()
	elbowJ = cmds.joint()
	wristJ = cmds.joint()

	cmds.xform(shldJ, ws=True, m=shldML)
	cmds.xform(elbowJ, ws=True, m=elbowML)
	cmds.xform(wristJ, ws=True, m=wristML)
	cmds.xform(pv, ws=True, m=pvML)


def poleVectorPosition(startJnt, midJnt, endJnt, length=12, createLoc=0, createViz=0):
	
	import maya.api.OpenMaya as om

	start = pm.xform(startJnt, q=1, ws=1, t=1)
	mid = pm.xform(midJnt, q=1, ws=1, t=1)
	end = pm.xform(endJnt, q=1, ws=1, t=1)
	startV = om.MVector(start[0], start[1], start[2])
	midV = om.MVector(mid[0], mid[1], mid[2])
	endV = om.MVector(end[0], end[1], end[2])

	startEnd = endV - startV
	startMid = midV - startV
	if createViz: mathUtils.vecViz(startEnd, name='startEnd')
	if createViz: mathUtils.vecViz(startMid, name='startMid')

	# projection vector is vecA projected onto vecB
	# it is calculated by dot product if one vector normalized

	# proj= vecA * vecB.normalized (dot product result is scalar)
	proj = startMid * startEnd.normal()

	# multiply proj scalar with normalized startEndVector to project it onto vector
	startEndN = startEnd.normal()
	projV = startEndN * proj
	if createViz: mathUtils.vecViz(projV, name='projV')

	arrowV = startMid - projV
	mathUtils.vecViz(arrowV, name='arrowV')
	arrowVN = arrowV.normal()

	# scale up to length and offset to midV
	finalV = arrowVN * length + midV

	if createViz: mathUtils.vecViz(finalV, name='finalV')

	if createLoc:
		loc = pm.spaceLocator(n='polePos')
		pm.xform(loc, ws=1, t=(finalV.x, finalV.y, finalV.z))

	return finalV


def keyPolePositionRange(startJnt, midJnt, endJnt, startFrame=None, endFrame=None, hingelimit=[0, 179], aimLoc=1,
						 loc=None):
	if loc == None:
		if pm.objExists(midJnt + '_poleVecPosition'):
			loc = pm.PyNode(midJnt + '_poleVecPosition')
		else:
			loc = pm.spaceLocator(n=midJnt + '_poleVecPosition')

	if startFrame == None:
		startFrame = pm.playbackOptions(q=1, min=1)
	if endFrame == None:
		endFrame = pm.playbackOptions(q=1, max=1)

	# pm.transformLimits(midJnt, ry=(hingelimit[0], hingelimit[1]), ery=(1,1))

	polepos = None
	prevPole = None
	for f in range(int(startFrame), int(endFrame)):
		pm.currentTime(f)
		if mathUtils.normalizedDotEllbow(startJnt, midJnt, endJnt) > 0.98:
			print 'Warning angle too straight %s' % f
			continue
		# check with prev pole pos

		polepos = poleVectorPosition(startJnt, midJnt, endJnt, createLoc=0)
		# check difference to prev pole vector calculation
		if prevPole is not None:

			differeFromPrev = mathUtils.normalizedDot(vec1=prevPole, vec2=polepos,
													  startPos=pm.xform(midJnt, q=1, t=1, ws=1))
			print differeFromPrev

			if differeFromPrev < 0.02:
				print 'Warning difference between PoleVectors too large %s. Frame %s' % (differeFromPrev, f)
				continue
		print 'Snapping pole vector to %s' % polepos

		pm.xform(loc, ws=1, t=(polepos.x, polepos.y, polepos.z))
		pm.setKeyframe(loc, t=f)

		prevPole = polepos

	# pm.transformLimits(midJnt, ry=(hingelimit[0], hingelimit[1]), ery=(0,0))


def zeroOut(*args):
	sel = pm.ls(sl=True, tr=True, r=True)
	for each in sel:
		loc = pm.spaceLocator(n='tmpLocator')
		zero = pm.spaceLocator(n='zeroLocator')
		pcon = pm.parentConstraint(each, loc, mo=False)
		pm.delete(pcon)
		zcon = pm.parentConstraint(zero, each, mo=False)
		pm.delete(zcon)
		pm.delete(zero)
		pm.makeIdentity(each, apply=True, t=True, n=False)
		pcon = pm.parentConstraint(loc, each, mo=False)
		pm.delete(pcon)
		pm.delete(loc)


def snap(driver, driven, typeCnx='parent', extraDrivers=(), skip=[]):
	'''
	snaps objects and skips locked attributes to prevent errors...
	also this doesnt uses constraints to snap..
	so The target objet could have keys if it is needed

	libUtil.snap('cube', 'target' , typeCnx='parent')

	Args:
		 driver:
		 driven:
		 typeCnx:
		 	['parent', 'parentCon', 1, 'p', 'P']
		 	['point', 'translate', 3, 't', 'T']
		 	['orient', 'rotate', 2, 'r', 'R']
		 	['scale', 'Scale', 4, 's', 'S']
		 extraDrivers:
		 skip:

	Returns:
	'''

	drivers = [driver]
	drivers.extend(extraDrivers)

	for i, driver in enumerate(drivers):
		if not isinstance(driver, pm.PyNode):
			drivers[i] = pm.PyNode(driver)
	if not isinstance(driven, pm.PyNode):
		driven = pm.PyNode(driven)
	# skip memory
	skipMemory = []
	for s in skip:
		skipMemory.append(driven.attr(s).get())

	dummy = pm.duplicate(driven, n=driven + 'dummy', parentOnly=1)[0]
	for attr in ('t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz', 's', 'sx', 'sy', 'sz'):
		dummy.attr(attr).unlock()

	con = pm.parentConstraint(mo=0, *(drivers + [dummy]))
	con.interpType.set(2)
	pm.delete(con)
	# pm.delete(pm.parentConstraint(mo=0, *(drivers + [dummy]) ))
	pm.delete(pm.scaleConstraint(mo=0, *(drivers + [dummy])))
	# pm.delete( pm.parentConstraint(drivers, dummy, mo=0,))


	t = pm.getAttr(dummy + '.translate')
	r = pm.getAttr(dummy + '.rotate')
	s = pm.getAttr(dummy + '.scale')
	pm.delete(dummy)

	# PARENT
	if typeCnx in ['parent', 'parentCon', 1, 'p', 'P']:
		i = 0
		for at in ['tx', 'ty', 'tz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(t[i])
			i = i + 1
		i = 0
		for at in ['rx', 'ry', 'rz']:
			try:
				driven.attr(at).set(r[i])
			except:
				pass
			i = i + 1
	# ROTATE ONLY
	elif typeCnx in ['orient', 'rotate', 2, 'r', 'R']:
		i = 0
		for at in ['rx', 'ry', 'rz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(r[i])
			i = i + 1
	# TRANSLATE ONLY
	elif typeCnx in ['point', 'translate', 3, 't', 'T']:
		i = 0
		for at in ['tx', 'ty', 'tz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(t[i])
			i = i + 1
	# SCALE ONLY
	elif typeCnx in ['scale', 'Scale', 4, 's', 'S']:
		i = 0
		for at in ['sx', 'sy', 'sz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(s[i])
			i = i + 1
	# ALL
	elif typeCnx in ['all', 'All', 5, 'a', 'A']:
		i = 0
		for at in ['tx', 'ty', 'tz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(t[i])
			i = i + 1
		i = 0
		for at in ['rx', 'ry', 'rz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(r[i])
			i = i + 1
		i = 0
		for at in ['sx', 'sy', 'sz']:
			if driven.attr(at).isLocked() == 0:
				driven.attr(at).set(s[i])
			i = i + 1
	# skip memory
	i = 0
	for s in skip:
		driven.attr(s).set(skipMemory[i])
		i = i + 1
	pm.select(driven)

def replaceParentConstraintWithSkin():

	objList = pm.selected()
	jointList = []
	pm.select(clear=1)
	if pm.objExists('jointGroup') == 0:
		pm.group(n='jointGroup', empty=1)
	for o in objList:
		jntname = o.nodeName().split(':')[-1] + 'JTN'
	jointList.append(pm.joint(n=o.jntname))
	
	#pm.parent(jointList[-1])
	#pm.parentConstraint(o, jnt, mo=0)



def create_pivot_bone():
	"""
	Create a bone from the customPivot context
	In component mode of a mesh:
	Press "D" or "Insert" to go into custom pivot context
	  If you click on edges verts or faces the pivot will auto align
	  If you want to aim an axis click on the axis and Ctrl+Shift on another vert/edge/face to aim it
	  When you have the pivot you want run this to create the joint with that pivot
	*Arguments:*
		* ``None`` 
	*Keyword Arguments:*
		* ``None`` 
	*Returns:*
		* ``None`` 
	*Author:*
	* randall.hess, randall.hess@gmail.com, 9/3/2017 5:17:19 PM
	"""

	# get these values	
	loc_xform = None
	loc_rp    = None
	
	# Get manipulator pos and orient	
	manip_pin = cmds.manipPivot(pinPivot=True)
	manip_pos = cmds.manipPivot(q=True, p=True)[0]
	manip_rot = cmds.manipPivot(q=True, o=True)[0]	
	
	# delete existing temp objs
	temp_joint = None
	temp_loc   = None
	temp_cluster= None
	temp_joint_name = 'temp_joint'
	temp_loc_name = 'temp_loc'
	temp_cluster_name = 'temp_cluster'
	temp_objs = [temp_joint_name, temp_loc_name]	
			
	# get the selectMode
	sel_mode_obj       = cmds.selectMode(q=True, o=True)
	sel_mode_component = cmds.selectMode(q=True, co=True)		

	# store and clear selection
	selection = cmds.ls(sl=True)
	py_selection = pymel.ls(sl=True)
	if len(selection) == 0:
		cmds.warning('You must have a selection!')
		return
	
	
	if len(selection) > 0:
		
		sel = selection[0]
		py_sel = py_selection[0]
	
		# create temp joint and set pos/rot
		cmds.select(cl=True)
		temp_joint= pymel.joint(n=temp_joint_name)
		temp_loc = pymel.spaceLocator(n=temp_loc_name)
		
		# get transform from the selected object
		if type(py_sel) == pymel.nodetypes.Transform:
			# snap loc to position			
			const = pymel.pointConstraint(sel, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
			const = pymel.orientConstraint(sel, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
		else:
			# get transform from parent object
			if type(py_sel.node()) == pymel.nodetypes.Mesh:
				parent = py_sel.node().getParent()
				if parent:
					const = pymel.pointConstraint(parent, temp_loc, mo=False, w=1.0)
					pymel.delete(const)
					const = pymel.orientConstraint(parent, temp_loc, mo=False, w=1.0)
					pymel.delete(const)
					
					# get the transforms
					loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
					loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)					

		# rotate the temp_loc if manip rot has been modified
		if not manip_rot == (0.0,0.0,0.0):				
			pymel.rotate(temp_loc, manip_rot)
			
		# move position to the cluster position
		if not manip_pos == (0.0,0.0,0.0):		
			pymel.xform(temp_loc, ws=True, t=manip_pos)
			
		# get the transforms
		loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
		loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)		
			
		# get the position from the component selection			
		if not type(py_sel) == pymel.nodetypes.Transform:
			cmds.select(selection, r=True)
			cmds.ConvertSelectionToVertices()
			try:
				cluster = cmds.cluster(n=temp_cluster_name)[1]
			except:
				cmds.warning('You must select a mesh object!')
				pymel.delete(temp_joint)
				pymel.delete(temp_loc)
				return
			
			# get the cluster position
			cmds.select(cl=True)		
			pos = cmds.xform(cluster, q=True, ws=True, rp=True)				
			
			# snap to the cluster
			const = pymel.pointConstraint(cluster, temp_loc, mo=False, w=1.0)
			pymel.delete(const)
			
			cmds.delete(cluster)
			
			# rotate the temp_loc if manip rot has been modified
			if not manip_rot == (0.0,0.0,0.0):				
				pymel.rotate(temp_loc, manip_rot)
				
			# move position to the cluster position
			if not manip_pos == (0.0,0.0,0.0):		
				pymel.xform(temp_loc, ws=True, t=manip_pos)				
					
			# get the transforms
			loc_xform = pymel.xform(temp_loc, q=True, m=True, ws=True)
			loc_rp = pymel.xform(temp_loc, q=True, ws=True, rp=True)	
		
		# remove temp loc
		pymel.delete(temp_loc)

	# modify the joint and stu
	if temp_joint:		
		if loc_xform and loc_rp:
			pymel.xform(temp_joint, m=loc_xform, ws=True)
			pymel.xform(temp_joint, piv=loc_rp, ws=True)			
		
		# freeze orient	
		pymel.select(temp_joint)	
		pymel.makeIdentity( apply=True, translate=True, rotate=True, scale=True, n=False )

	# unpin pivot
	cmds.manipPivot(pinPivot=False)