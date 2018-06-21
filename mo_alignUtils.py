import pymel.core as pm
import maya.cmds as cmds
import pymel.tools.mel2py as mel2py
import logging

# CREATE A LOGGER
_logger = logging.getLogger(__name__)

def placeHolderLoc(ctx=0):
    '''
    create locator at position of each selected object
    @param ctx: 0- just snap, 1-constrain selection to loc, 2-constrain loc to selection
    @return:
    '''
    sel = pm.selected()
    for s in sel:
        l = pm.spaceLocator(n=s.nodeName() + '_placeholderLoc')
        if ctx == 1:
            pm.parentConstraint(s,l, mo=0)
        elif ctx ==2:
            pm.parentConstraint(l,s, mo=0)
        else:
            pm.matchTransform(l,s)


def alignPos_constrain():
	""" Align with Parent Constrain 
	Select Master first. Also works with frozen position"""
	selLast=pm.ls(hd=1,sl=1)
	ptC=pm.pointConstraint(mo=False)
	pm.delete(ptC)
	pm.select(selLast)


def align_constrain():
	"""Align with Parent Constrain 
	Select Master first. Also works with frozen position"""
	selLast=pm.ls(hd=1,sl=1)
	ptC=pm.parentConstraint(mo=False)
	pm.delete(ptC)
	pm.select(selLast)



def alignPos_rotationPivot():
	""" Align with RotPivot
		Select Master first.""" 
	snp=cmds.ls(sl=1)
    
	pos=cmds.xform(snp[1],q=1,ws=1,t=1)
	rpB=cmds.xform(snp[1],q=1,rp=1)#rotate pivot a
	rpA=cmds.xform(snp[0],q=1,rp=1)#rotate pivot b 
	
	pm.xform(ws=1,t=((pos[0] + rpA[0] - rpB[0]), (pos[1] + rpA[1] - rpB[1]), (pos[2] + rpA[2] - rpB[2])))


def align_centerOfComponents(type="locator"):
    """ Align to Center position of selected Edge/Edge Loop/Vertice
    
    	if a object to transform is selected moves to center of component(edges, vertices, faces) selection
    	if no object to transform selected,  create and align locator """
    	
    sel = pm.selected(flatten=True)

    #HOLDERS
    verts = []
    edges = []
    tfms = []
    
    #SORT
    for s in sel:
        sortMe = s.__class__.__name__
        
        if sortMe == "Joint" or sortMe == "Transform":
            tfms.append(s)
            
        if sortMe == "MeshVertex":
            verts.append(s)
            
        if sortMe == "MeshEdge":
            edges.append(s)
        
    # CONVERT EDGES TO VERTS   
    if edges:
        # list comprehension
        edgeVerts = list(set(sum( [   list(e.connectedVertices())    for e in edges       ], [])))
        verts = verts + edgeVerts
   
    _logger.debug("verts = %s" % verts)
    _logger.debug("tfms = %s" % tfms)
   
   
    # CLUSTER
    clusDef, clusTfm = pm.cluster(verts)

    if not tfms:
	   if (type=="joint"):
		   jnt = pm.joint() 
		   print(jnt)
		   tfms.append(jnt)
	   else:
		   loc = pm.spaceLocator() 
		   tfms.append(loc)

    # LOOP THROUGH TFMS
    for tfm in tfms:
        
        # HIERARCHY ISSUES PREPPED
        parent=tfm.getParent()
        children = tfm.getChildren(type="transform")
        
        if parent:
            tfm.setParent(world=True)
        _logger.debug("children = %s"%children)
        for child in children:
            child.setParent(world=True)
            
        
        # POINT CONSTRAINT
        pm.delete( pm.pointConstraint(clusTfm, tfm, mo=False))

        for child in children:
            child.setParent(tfm)    
        if parent:
            tfm.setParent(parent)

    # CLEAR THE CLUSTER
    pm.delete(clusTfm)
    _logger.debug("DONE")



