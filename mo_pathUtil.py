class Path():
    # C_curve
    # C_curve01_clusterHandle
    def __init__(self, **kwargs):
        self.curve =  kwargs.get('curve',[])
        self.clusters =  kwargs.get('clusters',[])
        self.ctrls = kwargs.get('controls',[])
        self.name = kwargs.get('name',[])
            
    def hasClusters(self):
        print (True, False)[self.clusters == []]
        
    def addClusters(self):
        for numCV in range(self.curve.numCVs()):  
            pm.select(newPath.curve.cv[numCV])
            c = pm.cluster(n='%s%02d_cluster'%(newPath.name, numCV))
            self.clusters.append(c[0])
    def getClusters(self):
        return self.clusters
             
    def deleteClusters(self, deleteCurveHistory=1):
        if deleteCurveHistory==1:
            pm.delete(self.curve, ch=1)
            pm.select(self.curve)
        else:
            if self.clusters!=[]:
                pm.delete(self.clusters)
            else:
                pm.delete(pm.ls(regex=('%s.*_cluster'%self.name)))
            self.clusters=[]
            
    def addCtrls(self):
        for clr in self.getClusters():
            nr = int((clr.split('_cluster')[0])[-2:])
            newCtrl = self.createCtrl(self.name, nr)
            print newCtrl
            print clr
            pm.delete(pm.parentConstraint('%sHandle'%clr, newCtrl.replace('_ctrl', '_ZERO')))
            pm.parent('%sHandle'%clr, newCtrl)
            self.ctrls.append(newCtrl)
        
    def createCtrl(self, name, nr):
        print name
        print nr
        c= pm.circle(n='%s%02d_ctrl'%(name, nr))
        cAuto = pm.group(c, n='%s%02d_AUTO'%(name, nr))
        cZero = pm.group(cAuto, n='%s%02d_ZERO'%(name, nr))
        return c
        
    def reconnectCtrlToCluster(self):
        print self.ctrls
        
        
def definePath(obj=None):
    if obj == None:
        obj = pm.ls(sl=1)[0]
    else:
        obj = pm.PyNode(obj)
    if obj.__class__.__name__ == 'NurbsCurve':
        pathobj = Path(curve=obj, name=obj.getParent().name())
    else:
        try:
            shape = obj.getShape()
            if shape is not  None:
                pathobj = Path(curve=shape, name=obj.name())
        except:
            return None
    #existing clusters and ctrls
    print obj.name()
    clusters = pm.ls(regex=('%s.*_cluster'%pathobj.name), type='cluster')
    print clusters
    pathobj.clusters = clusters
    ctrls = pm.ls(regex=('%s.*_ctrl'%obj.name))
    pathobj.ctrls = ctrls
    return pathobj    













'''
import pymel.core as pm


newPath = definePath(obj)
newPath.addClusters()
newPath.deleteClusters()


class Path():
    def __init__(self, **kwargs):
        self.curve =  kwargs.get('curve',[])
        self.clusters =  kwargs.get('clusters',[])
        self.controls = kwargs.get('controls',[])
        self.name = kwargs.get('name',[])
            
    def hasClusters(self):
        print (True, False)[self.clusters == []]

    def addClusters(self):
        # CREATE CLUSTER FOR EACH CV
        for numCV in range(self.curve.numCVs()):  
            pm.select(newPath.curve.cv[numCV])
            c = pm.cluster(n='%s_cv%s_cluster'%(newPath.name, numCV))
            self.clusters.append(c)
        # GROUP

    def deleteClusters(self):
        print 'deleting %s'%pm.ls(regex=('%s_cv.*_cluster'%self.name))
        if self.clusters!=[]:
            pm.delete(self.clusters)
        else:
            pm.delete(pm.ls(regex=('%s_cv.*_cluster'%self.name)))

#DEFINE
def definePath(obj):
    obj = pm.PyNode(obj)
    if obj.__class__.__name__ == 'NurbsCurve':
        pathobj = Path(curve=obj, name=obj.getParent().name())
    else:
        try:
            shape = obj.getShape()
            if shape is not  None:
                pathobj = Path(curve=shape, name=obj.name())
        except:
            return None
    return pathobj'''