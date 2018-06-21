import pymel.core as pm

def createShapeCtrl(type, name='C_test_ctrl', scale=1, color='yellow'):
    """
    import mo_Utils.mo_curveLib as curveLib
    reload(curveLib)
    curveLib.createShapeCtrl('crossPaddle')

    Returns:
        object: 
    """
    print 'create Shape Ctrl'
    controller = ""
    if(type == "locator"):
        controller=str(pm.curve(p=[(0, 2, 0), (0, -2, 0), (0, 0, 0), (0, 0, 2), (0, 0, -2), (0, 0, 0), (2, 0, 0), (-2, 0, 0)],k=[0, 1, 2, 3, 4, 5, 6, 7],d=1,name=name))
    elif(type == "centricArrows"):
        controller=str(pm.curve(p=[(0, 0, 0), (32, 0, -5.333333), (32, 0, 5.333333), (0, 0, 0), (-32, 0, -5.333333), (-32, 0, 5.333333), (0, 0, 0), (-5.333333, 32, 0), (5.333333, 32, 0), (0, 0, 0), (-5.333333, -32, 0), (5.333333, -32, 0), (0, 0, 0), (0, 32, 5.333333), (0, 32, -5.333333), (0, 0, 0), (0, -32, 5.333333), (0, -32, -5.333333), (0, 0, 0), (32, 5.333333, 0), (32, -5.333333, 0), (0, 0, 0), (-32, 5.333333, 0), (-32, -5.333333, 0), (0, 0, 0), (-5.333333, 0, -32), (5.333333, 0, -32), (0, 0, 0), (-5.333333, 0, 32), (5.333333, 0, 32), (0, 0, 0), (0, 5.333333, -32), (0, -5.333333, -32), (0, 0, 0), (0, 5.333333, 32), (0, -5.333333, 32), (0, 0, 0)],k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],d=1,name=name))    
    elif(type == "box") or (type == "cube"):
        pointPosList = [(0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5)]
        controller=pm.curve(p=pointPosList, d=1,name=name, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    elif(type == "jack"):
        pointPosList = [(0, 0, 0), (0.75, 0, 0), (1, 0.25, 0), (1.25, 0, 0), (1, -0.25, 0), (0.75, 0, 0), (1, 0, 0.25), (1.25, 0, 0), (1, 0, -0.25), (1, 0.25, 0), (1, 0, 0.25), (1, -0.25, 0), (1, 0, -0.25), (0.75, 0, 0), (0, 0, 0), (-0.75, 0, 0), (-1, 0.25, 0), (-1.25, 0, 0), (-1, -0.25, 0), (-0.75, 0, 0), (-1, 0, 0.25), (-1.25, 0, 0), (-1, 0, -0.25), (-1, 0.25, 0), (-1, 0, 0.25), (-1, -0.25, 0), (-1, 0, -0.25), (-0.75, 0, 0), (0, 0, 0), (0, 0.75, 0), (0, 1, -0.25), (0, 1.25, 0), (0, 1, 0.25), (0, 0.75, 0), (-0.25, 1, 0), (0, 1.25, 0), (0.25, 1, 0), (0, 1, 0.25), (-0.25, 1, 0), (0, 1, -0.25), (0.25, 1, 0), (0, 0.75, 0), (0, 0, 0), (0, -0.75, 0), (0, -1, -0.25), (0, -1.25, 0), (0, -1, 0.25), (0, -0.75, 0), (-0.25, -1, 0), (0, -1.25, 0), (0.25, -1, 0), (0, -1, -0.25), (-0.25, -1, 0), (0, -1, 0.25), (0.25, -1, 0), (0, -0.75, 0), (0, 0, 0), (0, 0, -0.75), (0, 0.25, -1), (0, 0, -1.25), (0, -0.25, -1), (0, 0, -0.75), (-0.25, 0, -1), (0, 0, -1.25), (0.25, 0, -1), (0, 0.25, -1), (-0.25, 0, -1), (0, -0.25, -1), (0.25, 0, -1), (0, 0, -0.75), (0, 0, 0), (0, 0, 0.75), (0, 0.25, 1), (0, 0, 1.25), (0, -0.25, 1), (0, 0, 0.75), (-0.25, 0, 1), (0, 0, 1.25), (0.25, 0, 1), (0, 0.25, 1), (-0.25, 0, 1), (0, -0.25, 1), (0.25, 0, 1), (0, 0, 0.75)]
        controller=pm.curve(p=pointPosList, d=1,n=name, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83])
    elif(type == "sphere"):
        pointPosList =  [(0, 0, 1), (0, 0.5, 0.866025), (0, 0.866025, 0.5), (0, 1, 0), (0, 0.866025, -0.5), (0, 0.5, -0.866025), (0, 0, -1), (0, -0.5, -0.866025), (0, -0.866025, -0.5), (0, -1, 0), (0, -0.866025, 0.5), (0, -0.5, 0.866025), (0, 0, 1), (0.707107, 0, 0.707107), (1, 0, 0), (0.707107, 0, -0.707107), (0, 0, -1), (-0.707107, 0, -0.707107), (-1, 0, 0), (-0.866025, 0.5, 0), (-0.5, 0.866025, 0), (0, 1, 0), (0.5, 0.866025, 0), (0.866025, 0.5, 0), (1, 0, 0), (0.866025, -0.5, 0), (0.5, -0.866025, 0), (0, -1, 0), (-0.5, -0.866025, 0), (-0.866025, -0.5, 0), (-1, 0, 0), (-0.707107, 0, 0.707107), (0, 0, 1)]
        controller=str(pm.curve(p=pointPosList, d=1,n=name, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]))
    elif(type == "circle"):
        controller=pm.circle(r=scale, n=name, nrx=1, nry=0, nrz=0)[0]
        pm.delete(controller, ch=1)
    elif(type == "crossAxis"):
        controller=Shapes().poleCross(name)
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == 'crossPaddle'):
        pointPosList = [(0, 0, 0), (0, 0, 0), (0, 1.26, 0), (0, 1.45, 0.45), (0, 1.89, 0.62), (0, 2.35, 0.45), (0, 2.53, -0.013), (0, 2.35, -0.45), (0, 1.90, -0.64), (0, 1.45, -0.45), (0, 1.26, 0), (0, 1.45, 0.45), (0, 2.35, -0.45), (0, 1.90, -0.64), (0, 1.45, -0.45), (0, 2.35, 0.45)]
        controller= pm.curve(p=pointPosList, n=name, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], d=1)
        pm.xform(controller, sp=[0,0,0], rp=[0,0,0], piv=[0,0,0], ws=1) # pivot
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == "arrow"):
        controller=Shapes().arrow(name)
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == "PLACER"):
        controller=Shapes().placer()
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == "MOVER"):
        pointPosList =[pm.dt.Point([-3.360645, 0.0, -3.360645]), pm.dt.Point([-3.37686, 0.0, -3.34443]), pm.dt.Point([-4.247985, 0.0, -2.45985]), pm.dt.Point([-5.257455, 0.0, 0.023115]), pm.dt.Point([-3.724275, 0.0, 3.724275]), pm.dt.Point([0.0, 0.0, 5.267115]), pm.dt.Point([3.724275, 0.0, 3.724275]), pm.dt.Point([5.258145, 0.0, 0.02139]), pm.dt.Point([4.247295, 0.0, -2.461575]), pm.dt.Point([3.375825, 0.0, -3.345465]), pm.dt.Point([3.360645, 0.0, -3.360645]), pm.dt.Point([3.349605, 0.0, -3.349605]), pm.dt.Point([3.186765, 0.0, -3.18711]), pm.dt.Point([3.014265, 0.0, -3.0153]), pm.dt.Point([2.85315, 0.0, -2.85453]), pm.dt.Point([2.84349, 0.0, -2.84487]), pm.dt.Point([2.85315, 0.0, -2.834865]), pm.dt.Point([3.59076, 0.0, -2.08656]), pm.dt.Point([4.45188, 0.0, 0.014145]), pm.dt.Point([3.150885, 0.0, 3.150885]), pm.dt.Point([0.0, 0.0, 4.45671]), pm.dt.Point([-3.150885, 0.0, 3.150885]), pm.dt.Point([-4.448775, 0.0, 0.021735]), pm.dt.Point([-3.593865, 0.0, -2.07897]), pm.dt.Point([-2.85867, 0.0, -2.829345]), pm.dt.Point([-2.84349, 0.0, -2.84487]), pm.dt.Point([-2.853495, 0.0, -2.854875]), pm.dt.Point([-3.013575, 0.0, -3.014265]), pm.dt.Point([-3.18573, 0.0, -3.18642]), pm.dt.Point([-3.348225, 0.0, -3.348225])]
        controller = pm.curve(p=pointPosList, name=name, d=3)
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == "DIRECTION"):
        pointPosList = [pm.dt.Point([-2.4, 0.0, -2.4]), pm.dt.Point([2.4, 0.0, -2.4]), pm.dt.Point([2.4, 0.0, 2.4]), pm.dt.Point([0.0, 0.0, 3.6]), pm.dt.Point([-2.4, 0.0, 2.4])]
        controller = pm.curve(p=pointPosList, name=name, d=1)
        pm.closeCurve(name, ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    elif(type == "squareAxis45"):
        pointPosList = [pm.dt.Point([-0.0183221732195, 0.0220372618933, -0.0490237893162]),
          pm.dt.Point([6.98167782678, 7.02203726189, -0.0490237893162]),
          pm.dt.Point([6.98167782678, 10.0220372619, -0.0490237893162]),
          pm.dt.Point([9.98167782678, 10.0220372619, -0.0490237893162]),
          pm.dt.Point([9.98167782678, 7.02203726189, -0.0490237893162]),
          pm.dt.Point([6.98167782678, 7.02203726189, -0.0490237893162])]
        controller = pm.curve(p=pointPosList, name=name, d=1)
        #pm.closeCurve(name, ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        pm.xform('%s.cv[0:]'%controller, s=(scale, scale, scale), r=1)
    else:
        pm.warning('No type %s found. Doing nothing.'%type)
        return None
    colorOverride(color, [controller])
    return pm.PyNode(controller)
 
def createTextCtrl(text, name, font="Utopia-Regular", size=1, color='yellow'):
    textG = pm.textCurves(ch=0, t=text, f=font)
    textS = pm.listRelatives(textG, c=1, ad=1, shapes=1)
    textT = pm.listRelatives(textS, type='transform', p=1)
    #unparent, center pivot, rename
    pm.parent(textT, world=1)
    pm.xform(textT, cp=1)
    pm.xform(textT, s=(size,size,size))

    if len(textS) > 1: # more than one shape combine them under one transform
        i = 1
        for txtS in textS[1:]:
            print txtS
            pm.parent(txtS, textT[0], s=1)
            pm.rename(txtS, '%sShape%s'%(textT[0], i))
            pm.delete(textT[i])
            textT.pop(i)
            textS.pop(i)
            i=i+1


    pm.makeIdentity(textT, apply=1)
    pm.rename(textT, name)
    pm.rename(textS, name + 'Shape')
    pm.delete(textG)

    colorOverride(color, textT)
    
    return textT

def colorOverride(color, objs=None):
    if objs is None:
        objs=pm.ls(sl=1)
    else: objs = pm.ls(objs)
        
    if color is 'black':
        colorid = 2
    elif color is 'blue':
        colorid = 6
    elif color is 'darkgreen':
        colorid = 7
    elif color is 'violet':
        colorid = 8
    elif color is 'pink':
        colorid = 9
    elif color is 'brown':
        colorid = 10
    elif color is 'darkbrown':
        colorid = 11
    elif color is 'redbrown':
        colorid = 12
    elif color is 'red':
        colorid = 13
    elif color is 'green':
        colorid = 14
    elif color is 'white':
        colorid = 16
    elif color is 'yellow':
        colorid = 17
    elif color is 'skyblue':
        colorid = 18
    elif color is 'turqoise':
        colorid = 19
    elif color is 'baby':
        colorid = 20
    elif color is 'skin':
        colorid = 21
    elif color is 'tulip':
        colorid = 31

    for obj in objs:
        if pm.objExists(obj) is False:
            print 'Error colorOverride. %s does not exist'%obj
            return False
        
        obj = pm.PyNode(obj)
        
        obj.overrideEnabled.set(True)
        obj.overrideColor.set(colorid)
        obj.getShape().overrideEnabled.set(True)
        obj.getShape().overrideColor.set(colorid)
    
def createBoundingBox(name, sel = None):
    if sel == None:
         sel = pm.selected()
    if len(sel)<1:
         return
    pm.select(sel, r=True)
    
    bb = pm.exactWorldBoundingBox()
    S = bb[0:3]
    E = bb[3:6]

    bbBox=pm.curve(p=[
        (S[0], S[1], S[2]), 
        (E[0], S[1], S[2]), 
        (E[0], S[1], E[2]), 
        (S[0], S[1], E[2]),
        (S[0], S[1], S[2]),
        (S[0], E[1], S[2]), 
        (E[0], E[1], S[2]), 
        (E[0], S[1], S[2]), 
        (E[0], E[1], S[2]), 
        (E[0], E[1], E[2]), 
        (E[0], S[1], E[2]),
        (E[0], E[1], E[2]),
        (S[0], E[1], E[2]),
        (S[0], S[1], E[2]),
        (S[0], E[1], E[2]),
        (S[0], E[1], S[2]),
        (S[0], S[1], S[2])],
        k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],d=1,name=name)
    return bb





class Shapes():
    def arrow(self, name):
        return pm.curve( p =[(-1.0, 0.0, 0.0), (-1.0, 0.0, 2.0), (1.0, 0.0, 2.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 0.0, -2.0), (-2.0, 0.0, 0.0), (-1.0, 0.0, 0.0)],per = False, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7],
                         n=name)
    def poleCross(self, name):
        return pm.curve( p =[(0.5698271508338371, 4.091121663662989e-09, -2.132883735050939e-05), (0.4208952391731131, 0.1488873944517639, -1.5755096100633637e-05), (0.2720931419242101, 4.073556049855043e-05, -1.0184545420344193e-05), (0.4209398007112384, -0.1487613617926744, -1.5755096101521815e-05), (0.5698271508338371, 4.091121663662989e-09, -2.132883735050939e-05), (0.42091194939155674, 6.301549556786412e-05, -0.1488401347819135), (0.2720931419242101, 4.073556049855043e-05, -1.0184545420344193e-05), (0.42092309049279564, 6.301716352297149e-05, 0.14880862458971134), (0.5698271508338371, 4.091121663662989e-09, -2.132883735050939e-05), (0.4208952391731131, 0.1488873944517639, -1.5755096100633637e-05), (0.2720931419242101, 4.073556049855043e-05, -1.0184545420344193e-05), (-0.2720931291529265, -0.0001260413294232876, 1.0184545417679658e-05), (-0.4209971894939688, -6.30282570215357e-05, 0.14884013797247952), (-0.5698271380625544, -8.530986004595675e-05, 2.1328837348733032e-05), (-0.4210083305952077, -6.302992497664306e-05, -0.1488086213991462), (-0.2720931291529265, -0.0001260413294232876, 1.0184545417679658e-05), (-0.42085456057731463, 0.14876116408473417, 1.5751905531047328e-05), (-0.5698271380625544, -8.530986004595675e-05, 2.1328837348733032e-05), (-0.4209804792755252, -0.14888740721321847, 1.575828666666723e-05), (-0.2720931291529265, -0.0001260413294232876, 1.0184545417679658e-05), (-0.2720931291529265, -0.0001260413294232876, 1.0184545417679658e-05), (0.0, -1.3322676295501878e-15, 0.0), (-1.1141101238898443e-05, -1.6679564396326896e-09, 0.2721144031802565), (0.00014271626145045957, 0.14882419235483146, 0.42093877648166433), (0.0, -1.3322676295501878e-15, 0.569763162551884), (1.671021844362741e-05, -0.14882437895619827, 0.42093878286606934), (-1.1141101238898443e-05, -1.6679564396326896e-09, 0.2721144031802565), (-0.14882987953462568, -2.2281592690021057e-05, 0.4209443534141677), (0.0, -1.3322676295501878e-15, 0.569763162551884), (0.14890412937122033, -6.29878057401001e-05, 0.42093320912223664), (-1.1141101238898443e-05, -1.6679564396326896e-09, 0.2721144031802565), (-3.151178319171777e-05, -4.717688018018862e-09, -0.2721144015837451), (-5.935678879254169e-05, 0.14882437257149927, -0.4209387812697942), (-4.265288443061621e-05, -6.385641793116292e-09, -0.5697631609553717), (-1.4801564748090357e-05, -0.1488243836738845, -0.42093878126955797), (-3.151178319171777e-05, -4.717688018018862e-09, -0.2721144015837451), (-0.1488613913178174, -2.2286310378039076e-05, -0.4209332107214614), (-4.265288443061621e-05, -6.385641793116292e-09, -0.5697631609553717), (0.1488726175880286, -6.299252342767403e-05, -0.42094435501339156), (-3.151178319171777e-05, -4.717688018018862e-09, -0.2721144015837451)],per = False, d=1, k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
                    n=name)
        # mergedShape = self.mergeShapes(list)
        # pm.select(mergedShape)
        # return mergedShape

    def mergeShapes(self, shapeList):
        '''
        Merge shapes into single node (last element of shapeList
        Args:
            shapeList:

        Returns: merged shape Transform node

        '''
        if len(shapeList) < 2:
            return shapeList[0]
        #print 'shapelist is %s'%shapeList
        for x in range(len(shapeList)-1):
            pm.select(shapeList[x+1])
            pm.makeIdentity(apply=True, t=1, r=1, s=1)
            shapeNode = pm.listRelatives(shapeList[x+1], shapes=True)
            pm.parent(shapeNode, shapeList[0], add=True, s=True)
            pm.delete(shapeList[x+1])

        return shapeList[0]

    def placer(self):
        pointList1 =[pm.dt.Point([0.498, 0.0, -6.164]),
          pm.dt.Point([0.498, 0.0, -7.409]),
          pm.dt.Point([0.996, 0.0, -7.409]),
          pm.dt.Point([0.0, 0.0, -8.654]),
          pm.dt.Point([-0.996, 0.0, -7.409]),
          pm.dt.Point([-0.498, 0.0, -7.409]),
          pm.dt.Point([-0.498, 0.0, -6.164])]
        pointList2 =[pm.dt.Point([6.096, 0.0, 0.43]),
          pm.dt.Point([6.096, 0.0, -0.566]),
          pm.dt.Point([7.341, 0.0, -0.566]),
          pm.dt.Point([7.341, 0.0, -1.064]),
          pm.dt.Point([8.586, 0.0, -0.065]),
          pm.dt.Point([7.341, 0.0, 0.928]),
          pm.dt.Point([7.341, 0.0, 0.43])]
        pointList3 = [pm.dt.Point([-0.498, 0.0, 6.0284]),
          pm.dt.Point([-0.498, 0.0, 7.2734]),
          pm.dt.Point([-0.996, 0.0, 7.2734]),
          pm.dt.Point([0.0, 0.0, 8.5184]),
          pm.dt.Point([0.996, 0.0, 7.2734]),
          pm.dt.Point([0.498, 0.0, 7.2734]),
          pm.dt.Point([0.498, 0.0, 6.0284])]
        pointList4=[pm.dt.Point([-6.096, 0.0, -0.566]),
          pm.dt.Point([-7.341, 0.0, -0.566]),
          pm.dt.Point([-7.341, 0.0, -1.064]),
          pm.dt.Point([-8.586, 0.0, -0.065]),
          pm.dt.Point([-7.341, 0.0, 0.928]),
          pm.dt.Point([-7.341, 0.0, 0.43]),
          pm.dt.Point([-6.096, 0.0, 0.43])]

        list = []
        list.append(pm.curve(p=pointList1, name='shape1', d=1))
        pm.closeCurve(list[-1], ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        list.append(pm.curve(p=pointList2, name='shape2', d=1))
        pm.closeCurve(list[-1], ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        list.append(pm.curve(p=pointList3, name='shape3', d=1))
        pm.closeCurve(list[-1], ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        list.append(pm.curve(p=pointList4, name='shape4', d=1))
        pm.closeCurve(list[-1], ps=1, ch=1, bb=0.5, bki=0, p=0.1, rpo=1)
        list.append(pm.circle(r=5, n='addCenter',nry=1,nrz=0))
        placerNode = self.mergeShapes(list)
        pm.rename(placerNode, "PLACER")
        return placerNode




'''
import maya.OpenMaya as OpenMaya
import pymel.core as pm

getClosestVertex('pCone1_geo_boundingBox', 'locator1')

crv = pm.selected()[0]
crvShape = crv.getShape()
geo = pm.selected()[0]
geoShape = geo.getShape()
pm.pointPosition('pCone1_geo_boundingBoxShape.vtx[2]')

numcvs = crvShape.numCVs()
numverices = geoShape.numVertices()

for curvePoint in range(numcvs):
    
    print crvShape.cv[curvePoint].getPosition()
    tempLoc = pm.spaceLocator(n='tempLoc')
    pm.xform(tempLoc, t=pm.pointPosition(crvShape.cv[curvePoint]))
    closestVertex = getClosestVertex(geo, tempLoc)
    print closestVertex
    crvShape.setCV(curvePoint,  pm.pointPosition(closestVertex), space='world')
    
    pm.setAttr(crvShape.cv[curvePoint], pm.pointPosition(closestVertex))
    #print pm.setAttr(crvShape.cv[curvePoint], geoShape.vtx[curvePoint].getPosition())


for curvePoint in range(numcvs):

'''