import pymel.core as pm
import maya.OpenMaya as om
import maya.cmds as cmds
import mo_Utils.mo_mathUtils as mathUtils

reload(mathUtils)

import math
import time


# duplicateTransformHierarchy(grp, geoProxy=False)

def getVertexOm2(mesh=None):
	"""
	Using Maya Python API 2.0

	"""
	# ___________Selection___________
	# 1 # Query the selection list
	if mesh == None:
		selectionLs = om.MGlobal.getActiveSelectionList()
	else:
		selectionLs = om.MGlobal.getActiveSelectionList()

	# 2 # Get the dag path of the first item in the selection list
	selObj = selectionLs.getDagPath(0)

	# ___________Query vertex position ___________
	# create a Mesh functionset from our dag object
	mfnObject = om.MFnMesh(selObj)

	return mfnObject.getPoints()


def getFaceCount(obj=None):
	if obj == None:
		obj = pm.selected()[-1]
	else:
		obj = pm.ls(obj)[-1]
	return pm.polyEvaluate(obj, face=True)


def duplicateTransformHierarchy(grp, geoProxy=False):
	'''

	@param grp: the group to duplicate >>  suffixed 'Dup' parent to world
	@param geoProxy: create dummy plaholder spheres for meshes
	@return:
	'''

	def duplicateTransformHierarchyRec(origNode, parentToNode, geoProxy=False):
		origChildren = origNode.getChildren(type='transform')

		if len(origChildren) == 0: return 'Finished'

		for origChild in origChildren:
			origShape = origChild.getShape()
			if origShape is not None:  # shape
				if geoProxy is not False:
					print 'duplicating mesh'
					proxySphere = pm.polySphere(name='temp', sx=4, sy=6)[0]
					pm.matchTransform(proxySphere, origChild)
					pm.parent(proxySphere, parentToNode)
					proxySphere.rename(origChild)
			else:
				dup = origChild.duplicate(n='temp', po=1)[0]
				pm.parent(dup, parentToNode)
				dup.rename(origChild)
				duplicateTransformHierarchyRec(origChild, dup, geoProxy)

	origGrp = pm.PyNode(grp)
	parentToNode = origGrp.duplicate(n=origGrp.nodeName() + 'Dup', po=1)
	pm.parent(parentToNode, w=1)
	duplicateTransformHierarchyRec(origGrp, parentToNode, geoProxy)


# bakePartialHistory(*args, **kwargs)
''''This command is used to bake sections of the construction history of a shape node when possible.'''

import pymel.core as pm


def curveAlongCenter(surf):
	# make live curve on surface down the middle of nurbs surface
	curvMaker = pm.createNode('curveFromSurfaceIso', n=surf + "CurveIso")
	pm.setAttr(curvMaker + ".isoparmValue", 0.5)
	pm.setAttr(curvMaker + ".isoparmDirection", 1)
	pm.connectAttr(surf + ".worldSpace[0]", curvMaker + ".inputSurface")

	offsetCrvShp = pm.createNode("nurbsCurve", n=crv + "_driverSurfCrvShape")
	offsetCrv = pm.listRelatives(p=1)[0]
	offsetCrv = pm.rename(offsetCrv, crv + "_driverSurfCrv")
	pm.connectAttr(curvMaker + ".outputCurve", offsetCrvShp + ".create")
	pm.parent(offsetCrv, hiddenStuff)


def snapToClosestPoint(ptList, targetGeo, threshold=0.0001):
	'''
	Snap a list of points to the closest point component of a target geometry
	@param ptList: List of points to snap to target geometry. Can be transforms or components.
	@type ptList: list
	@param targetGeo: Target mesh to snap points to
	@type targetGeo: str
	@param threshold: If a point is closer to the target mesh than this distance, it will snap point.
	@type threshold: float
	'''
	# Check target mesh
	if not cmds.objExists(targetGeo):
		raise Exception('Target geoemetry "' + targetGeo + '" does not exist!!')

	# Get target point array
	targetPtArray = glTools.utils.base.getMPointArray(targetGeo)

	# Flatten input point list
	ptList = cmds.ls(ptList, fl=True)

	# Iterate through input points
	for pt in ptList:

		# Initialize distance values
		dist = 0
		minDist = 99999

		# Initialize point values
		mPt = glTools.utils.base.getMPoint(pt)
		tPt = mPt

		# Find closest point
		for i in range(targetPtArray.length()):

			# Get distance to point
			dist = (mPt - targetPtArray[i]).length()
			if dist < minDist:
				minDist = dist
				tPt = targetPtArray[i]

			# Check thrshold distance
			if (threshold > 0.0) and (dist < threshold): break

		# Move to target point


def unparentShapes():
	for s in pm.selected()[0].getShapes():
		nt = pm.createNode('transform')
		pm.parent(s, nt, shape=1)


# -*- coding: utf-8 -*-
from math import sqrt


def timeit(method):
	"""
	Decorator to time function evaluation.
	Prints "method (args, kwargs) time.sec"
	"""

	def timed(*args, **kwargs):
		ts = time.time()
		result = method(*args, **kwargs)
		te = time.time()

		print '%r (%r, %r) %2.2f sec' % \
			  (method.__name__, args, kwargs, te - ts)
		return result

	return timed


class OBB(object):
	"""
	:class:`OBB` Oriented Bounding Box Class.

	Requires an input meshName.
	"""
	meshName = None

	def __init__(self, meshName=None, method=0):
		import time
		if not meshName:
			raise RuntimeError("No mesh set in class.")

		self.shapeName = self.getShape(meshName)
		self.fnMesh = self.getMFnMesh(self.shapeName)

		# Get data we need to calculate OBB.
		self.points = self.getPoints(self.fnMesh)
		self.triangles = self.getTriangles(self.fnMesh)

		if method == 0:
			eigenVectors, center, obb_extents = self.build_from_points()

		elif method == 1:
			eigenVectors, center, obb_extents = self.build_from_triangles()

		elif method == 2:
			eigenVectors, center, obb_extents = self.build_from_hull()

		else:
			raise RuntimeError("Method unsupported! Please use 0(from_points),"
							   " 1(from_triangles), or 2(from_hull).")

		# Naturally aligned axis for x, y, z.
		self.eigenVectors = eigenVectors

		# Center point.
		self._center = center

		# Extents (length) of the bounding in x, y, z.
		self._obb_extents = obb_extents

		self.boundPoints = self.get_bounding_points()

		self._width = (self.boundPoints[1] - self.boundPoints[0]).length()
		self._height = (self.boundPoints[2] - self.boundPoints[0]).length()
		self._depth = (self.boundPoints[6] - self.boundPoints[0]).length()
		self._matrix = self.getMatrix()

	@property
	def width(self):
		"""
		Property width of the bounding box.
		"""
		return self._width

	@property
	def height(self):
		"""
		Property height of the bounding box.
		"""
		return self._height

	@property
	def depth(self):
		"""
		Property depth of the bounding box.
		"""
		return self._depth

	@property
	def volume(self):
		"""
		Property volume of bounding box.
		"""
		return self._width * self._height * self._depth

	@property
	def matrix(self):
		"""
		Property matrix of the bounding box.
		"""
		return self._matrix

	@property
	def center(self):
		"""
		Property center of the bounding box.

		Returns:
			(om.MVector)
		"""
		return self._center

	@classmethod
	def from_points(cls, meshName=None):
		"""
		Bounding box algorithm using vertex points.

		Raises:
			None

		Returns:
			(OBB Instance)
		"""
		return cls(meshName=meshName, method=0)

	@classmethod
	def from_triangles(cls, meshName=None):
		"""
		Bounding box algorithm using triangles points.

		Raises:
			None

		Returns:
			(OBB Instance)
		"""
		return cls(meshName=meshName, method=1)

	@classmethod
	def from_hull(cls, meshName=None):
		"""
		Bounding box algorithm using triangles points.

		Raises:
			None

		Returns:
			(OBB Instance)
		"""
		if not hullMethod:
			raise RuntimeError(
				"From hull method unavailable because scipy cannot be imported."
				"Please install it if you need it.")
		return cls(meshName=meshName, method=2)

	def create_bounding_box(self, meshName="bounding_GEO"):
		"""
		Create the bounding box mesh.

		:param meshName(string): Name of created mesh.

		Raises:
			None

		Returns:
			(string) Cube Transform
		"""
		obbCube = cmds.polyCube(constructionHistory=False, name="obb_GEO")[0]

		for ind, pnt in enumerate(self.boundPoints):
			cmds.xform("%s.vtx[%s]" % (obbCube, ind),
					   translation=[pnt.x, pnt.y, pnt.z])

		return obbCube

	def getMatrix(self):
		"""
		Gets the matrix representing the transformation of the bounding box.

		Raises:
			None

		Returns:
			(list of floats) Matrix
		"""
		m = [(self.eigenVectors[1].x * self._obb_extents.y * 2),
			 (self.eigenVectors[1].y * self._obb_extents.y * 2),
			 (self.eigenVectors[1].z * self._obb_extents.y * 2),
			 0.0,
			 (self.eigenVectors[2].x * self._obb_extents.z * 2),
			 (self.eigenVectors[2].y * self._obb_extents.z * 2),
			 (self.eigenVectors[2].z * self._obb_extents.z * 2),
			 0.0,
			 (self.eigenVectors[0].x * self._obb_extents.x * 2),
			 (self.eigenVectors[0].y * self._obb_extents.x * 2),
			 (self.eigenVectors[0].z * self._obb_extents.x * 2),
			 0.0,
			 self._center.x,
			 self._center.y,
			 self._center.z,
			 1.0]

		# Get the scale.
		mMat = om.MMatrix()
		om.MScriptUtil.createMatrixFromList(m, mMat)

		if mMat.det4x4() < 0:
			m[8] *= -1
			m[9] *= -1
			m[10] *= -1

		return m

	def get_bounding_points(self):
		"""
		Gets the bounding box points from the build.

		Raises:
			None

		Returns:
			(list of MVectors) Bounding box points.
		"""
		boundPoints = [(self._center - self.eigenVectors[0] *
						self._obb_extents.x + self.eigenVectors[1] *
						self._obb_extents.y + self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center - self.eigenVectors[0] *
						self._obb_extents.x + self.eigenVectors[1] *
						self._obb_extents.y - self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center + self.eigenVectors[0] *
						self._obb_extents.x + self.eigenVectors[1] *
						self._obb_extents.y + self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center + self.eigenVectors[0] *
						self._obb_extents.x + self.eigenVectors[1] *
						self._obb_extents.y - self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center + self.eigenVectors[0] *
						self._obb_extents.x - self.eigenVectors[1] *
						self._obb_extents.y + self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center + self.eigenVectors[0] *
						self._obb_extents.x - self.eigenVectors[1] *
						self._obb_extents.y - self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center - self.eigenVectors[0] *
						self._obb_extents.x - self.eigenVectors[1] *
						self._obb_extents.y + self.eigenVectors[2] *
						self._obb_extents.z),
					   (self._center - self.eigenVectors[0] *
						self._obb_extents.x - self.eigenVectors[1] *
						self._obb_extents.y - self.eigenVectors[2] *
						self._obb_extents.z)]

		return boundPoints

	def build_from_hull(self):
		"""
		Test oriented bounding box algorithm using convex hull points.

		Raises:
			None

		Returns:
			EigenVectors(om.MVector)
			CenterPoint(om.MVector)
			BoundingExtents(om.MVector)
		"""
		npPointList = [[self.points[i].x, self.points[i].y, self.points[i].z]
					   for i in xrange(self.points.length())]

		try:
			hull = ConvexHull(npPointList)
		except NameError:
			raise RuntimeError(
				"From hull method unavailable because"
				" scipy cannot be imported."
				"Please install it if you need it.")

		indices = hull.simplices
		vertices = npPointList[indices]
		hullPoints = list(vertices.flatten())
		hullTriPoints = list(indices.flatten())

		hullArray = om.MVectorArray()
		for ind in xrange(0, len(hullPoints), 3):
			hullArray.append(
				om.MVector(
					hullPoints[ind], hullPoints[ind + 1], hullPoints[ind + 2]))

		triPoints = om.MIntArray()
		for tri in xrange(len(hullTriPoints)):
			triPoints.append(tri)

		return self.build_from_triangles(points=hullArray, triangles=triPoints)

	def build_from_triangles(self, points=None, triangles=None):
		"""
		Test oriented bounding box algorithm using triangles.

		:param points(om.MVectorArray): points to represent geometry.
		:param triangles(om.MIntArray): points to represent geometry.

		Raises:
			None

		Returns:
			EigenVectors(om.MVector)
			CenterPoint(om.MVector)
			BoundingExtents(om.MVector)
		"""
		if not points:
			points = self.points

		if not triangles:
			triangles = self.triangles

		mu = om.MVector(0.0, 0.0, 0.0)
		mui = om.MVector(0.0, 0.0, 0.0)

		Am, Ai = 0.0, 0.0
		cxx, cxy, cxz, cyy, cyz, czz = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

		for tInd in xrange(0, triangles.length(), 3):
			p = points[triangles[tInd]]
			q = points[triangles[tInd + 1]]
			r = points[triangles[tInd + 2]]

			mui = (p + q + r) / 3.0
			Ai = ((q - p) ^ (r - p)).length() * 0.5

			mu += mui * Ai
			Am += Ai

			# these bits set the c terms to Am*E[xx], Am*E[xy], Am*E[xz]....
			cxx += ((9.0 * mui.x * mui.x + p.x * p.x + q.x * q.x + r.x * r.x) *
					(Ai / 12.0))
			cxy += ((9.0 * mui.x * mui.y + p.x * p.y + q.x * q.y + r.x * r.y) *
					(Ai / 12.0))
			cxz += ((9.0 * mui.x * mui.z + p.x * p.z + q.x * q.z + r.x * r.z) *
					(Ai / 12.0))
			cyy += ((9.0 * mui.y * mui.y + p.y * p.y + q.y * q.y + r.y * r.y) *
					(Ai / 12.0))
			cyz += ((9.0 * mui.y * mui.z + p.y * p.z + q.y * q.z + r.y * r.z) *
					(Ai / 12.0))

		mu /= Am

		cxx /= Am
		cxy /= Am
		cxz /= Am
		cyy /= Am
		cyz /= Am
		czz /= Am

		cxx -= mu.x * mu.x
		cxy -= mu.x * mu.y
		cxz -= mu.x * mu.z
		cyy -= mu.y * mu.y
		cyz -= mu.y * mu.z
		czz -= mu.z * mu.z

		# Covariance Matrix
		C = [[cxx, cxy, cxz],
			 [cxy, cyy, cyz],
			 [cxz, cyz, czz]]

		return self.build_from_covariance_matrix(
			cvMatrix=C)

	def build_from_points(self):
		"""
		Bounding box algorithm using vertex points.

		Raises:
			None

		Returns:
			EigenVectors(om.MVector)
			CenterPoint(om.MVector)
			BoundingExtents(om.MVector)
		"""
		pointSize = float(self.points.length())

		mu = om.MVector(0.0, 0.0, 0.0)
		# Calculate the average position of points.
		for p in xrange(int(pointSize)):
			mu += self.points[p] / pointSize

		cxx, cxy, cxz, cyy, cyz, czz = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
		for p in xrange(int(pointSize)):
			p = self.points[p]
			cxx += p.x * p.x - mu.x * mu.x
			cxy += p.x * p.y - mu.x * mu.y
			cxz += p.x * p.z - mu.x * mu.z
			cyy += p.y * p.y - mu.y * mu.y
			cyz += p.y * p.z - mu.y * mu.z
			czz += p.z * p.z - mu.z * mu.z

		# Covariance Matrix
		C = [[cxx, cxy, cxz],
			 [cxy, cyy, cyz],
			 [cxz, cyz, czz]]

		return self.build_from_covariance_matrix(
			cvMatrix=C)

	def build_from_covariance_matrix(self, cvMatrix=None):
		"""
		Build eigen vectors from covariance matrix.

		:param matrix(list of lists): covariance matrix

		Raises:
			None

		Returns:
			None
		"""
		# Calculate the natural axes by getting the eigen vectors.
		eigenValues, eigVec = mathUtils.eigh(cvMatrix)

		r = om.MVector(eigVec[0][0], eigVec[1][0], eigVec[2][0])
		r.normalize()

		u = om.MVector(eigVec[0][1], eigVec[1][1], eigVec[2][1])
		u.normalize()

		f = om.MVector(eigVec[0][2], eigVec[1][2], eigVec[2][2])
		f.normalize()

		minim = om.MVector(1e10, 1e10, 1e10)
		maxim = om.MVector(-1e10, -1e10, -1e10)

		for i in xrange(self.points.length()):
			pnt = self.points[i]

			p_prime = om.MVector(
				r * pnt, u * pnt, f * pnt)

			minim = om.MVector(
				min(minim.x, p_prime.x),
				min(minim.y, p_prime.y),
				min(minim.z, p_prime.z))
			maxim = om.MVector(
				max(maxim.x, p_prime.x),
				max(maxim.y, p_prime.y),
				max(maxim.z, p_prime.z))

		centerPoint = (maxim + minim) * .5
		m_ext = (maxim - minim) * .5

		R = om.MVector(r.x, u.x, f.x)
		U = om.MVector(r.y, u.y, f.y)
		F = om.MVector(r.z, u.z, f.z)

		m_pos = om.MVector(
			R * centerPoint, U * centerPoint, F * centerPoint)

		return [r, u, f], m_pos, m_ext

	def getTriangles(self, fnMesh):
		"""
		Get the triangles indices.

		:param fnMesh (om.MFnMesh): mesh function set.

		Raises:
			None

		Returns:
			(om.MIntArray) indices of triangles.
		"""
		triangleCounts = om.MIntArray()
		triangleVertices = om.MIntArray()

		fnMesh.getTriangles(triangleCounts, triangleVertices)

		return triangleVertices

	def getPoints(self, fnMesh):
		"""
		Get the points of each vertex.

		:param fnMesh (om.MFnMesh): mesh function set.

		Raises:
			None

		Returns:
			(om.MVectorArray) list of points.
		"""
		mPoints = om.MPointArray()
		fnMesh.getPoints(mPoints, om.MSpace.kWorld)

		mVecPoints = om.MVectorArray()
		[mVecPoints.append(om.MVector(mPoints[x]))
		 for x in xrange(mPoints.length())]

		return mVecPoints

	def getMFnMesh(self, mesh):
		"""
		Gets the MFnMesh of the input mesh.

		:param mesh (str): string name of input mesh.

		Raises:
			`RuntimeError` if not a mesh.
		Returns:
			(om.MFnMesh) MFnMesh mesh object.
		"""
		mSel = om.MSelectionList()
		mSel.add(mesh)

		mDagMesh = om.MDagPath()
		print 'test'
		print mDagMesh
		mSel.getDagPath(0, mDagMesh)

		try:
			fnMesh = om.MFnMesh(mDagMesh)
		except:
			raise RuntimeError("%s is not a mesh.")

		return fnMesh

	def getShape(self, node):
		"""
		Gets the shape node from the input node.

		:param node (str): string name of input node

		Raises:
			`RuntimeError` if no shape node.
		Returns:
			(str) shape node name
		"""
		if cmds.nodeType(node) == 'transform':
			shapes = cmds.listRelatives(node, shapes=True)

			if not shapes:
				raise RuntimeError('%s has no shape' % node)

			return shapes[0]

		elif cmds.nodeType(node) == "mesh":
			return node


def orientedBoundingbox(mesh=None):
	'''
	import  mo_Utils.mo_meshUtils as meshUtils
	reload(meshUtils)
	meshUtils.orientedBoundingbox()
	Args:
	    mesh:

	Returns:

	'''
	try:
		from scipy.spatial import ConvexHull
		hullMethod = True
	except:
		RuntimeWarning("Unable to load scipy."
					   "The from_hull method will not be available.")
		hullMethod = False

	if mesh == None: mesh = cmds.ls(selection=True)

	if len(mesh) == 0:
		raise RuntimeError("Nothing selected!")

	obbBoundBoxPnts = OBB.from_points(mesh)
	obbCube = cmds.polyCube(
		constructionHistory=False, name="pointMethod_GEO")[0]
	cmds.xform(obbCube, matrix=obbBoundBoxPnts.matrix)
	print(obbBoundBoxPnts.volume)

	obbBoundBoxTris = OBB.from_triangles(mesh)
	obbCube = cmds.polyCube(
		constructionHistory=False, name="triangleMethod_GEO")[0]
	cmds.xform(obbCube, matrix=obbBoundBoxTris.matrix)
	print(obbBoundBoxTris.volume)

	obbBoundBoxHull = OBB.from_hull(mesh)
	obbCube = cmds.polyCube(
		constructionHistory=False, name="hullMethod_GEO")[0]
	cmds.xform(obbCube, matrix=obbBoundBoxHull.matrix)
	print(obbBoundBoxHull.volume)


# gets the XYZ positions of each face center
def getFaceInfo(object):
	# select the object
	cmds.select(object, replace=True)

	faceInfo = []

	# get the number of faces as an int
	faceCount = cmds.polyEvaluate(face=True)

	# iterate over faces and get associated verts
	for i in range(faceCount):

		# select the face
		cmds.select(object + '.f[' + str(i) + ']', replace=True)

		# get the associated verts - output needs to be formatted
		rawVerts = cmds.polyInfo(fv=True)
		rawVerts = rawVerts[0].split(' ')

		verts = []

		# if output is a digit, save it in verts list
		for item in rawVerts:
			if item.isdigit() == True:
				verts.append(item)

		xPos = 0
		yPos = 0
		zPos = 0

		# get xyz of each vert on face
		for i in range(len(verts)):
			# select each vert
			cmds.select(object + '.vtx[' + verts[i] + ']', replace=True)

			# get the xyz position
			pos = cmds.pointPosition()

			xPos += pos[0]
			yPos += pos[1]
			zPos += pos[2]

		# get average xyz values
		xPos = xPos / len(verts)
		yPos = yPos / len(verts)
		zPos = zPos / len(verts)

		# add values to list
		faceCenter = [xPos, yPos, zPos]

		# append values list to main list
		faceInfo.append(faceCenter)

	# after all faces have been analyzed, return main list
	return faceInfo


# get distance between two points
def getDistance(a, b):
	dist = math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2) + math.pow(a[2] - b[2], 2))
	return dist


def findMissingFaces():
	# get time at start of function
	start = time.time()

	# get name of the selected object
	sel = cmds.ls(sl=True)

	# confirm two objects are selected
	if len(sel) != 2:
		cmds.confirmDialog(title='asdf', message='Please select 2 objects', button=['ok'], defaultButton='Yes',
						   cancelButton='No', dismissString='No')

	# get names of selected objects
	objectA = sel[0]
	objectB = sel[1]

	# get face center info for each object
	infoA = getFaceInfo(objectA)
	infoB = getFaceInfo(objectB)

	# create empty list to store face names with no match
	killList = []

	# work with the object that has more faces
	if (len(infoA) > len(infoB)):

		# start with the first object
		for i in range(len(infoA)):

			# create empty list to hold face distances
			faceDistanceList = []

			for j in range(len(infoB)):
				# get distances between each face of first object and all faces on second object
				faceDistanceList.append(getDistance(infoA[i], infoB[j]))

			# once face has been analyzed, store distances between it and all faces on the smaller mesh
			# if no value of 0.0, face doesn't have a match
			if min(faceDistanceList) != 0.0:
				# add face to the kill list
				killList.append(objectA + '.f[' + str(i) + ']')

	if (len(infoA) < len(infoB)):

		for i in range(len(infoB)):

			faceDistanceList = []

			for j in range(len(infoA)):
				# get distances
				faceDistanceList.append(getDistance(infoB[i], infoA[j]))

			if min(faceDistanceList) != 0.0:
				# add face to the kill list
				killList.append(objectB + '.f[' + str(i) + ']')

	# deselect anything that happens to be selected
	cmds.select(deselect=True)

	# select all faces in killList
	for item in killList:
		cmds.select(item, toggle=True)

	# delete selected faces
	cmds.delete()

	end = time.time()

	# print duration of process
	print 'This took ' + str(end - start) + ' seconds'
