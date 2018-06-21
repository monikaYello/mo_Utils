import pymel.core as pm

'''
sys.path.append("D:\Google Drive\PythonScripting\scripts")
import mo_Utils.mo_animUtils as mo_animUtils
mo_animUtils.doItForEveryFrame("pm.matchTransform('Jill_const_to_jack_CONST', 'JACK:jack_ac_cn_chest')")

'''

def doItForEveryFrame(commandStr, startFrame=None, endFrame=None):
    '''
    Runs commandStr for every frame from sartFramet to endFrame
    Use to snap one control to another for range
    doItForEveryFrame("pm.matchTransform('Jill_const_to_jack_CONST', 'JACK:jack_ac_cn_chest', mo=0")

    doItForEveryFrame("pm.matchTransform('Jill_const_to_jack_CONST', 'JACK:jack_ac_cn_chest')")

    @param commandStr: string representation of code to run
    @param startFrame: timeslider startframe if not set
    @param endFrame: timeslider endframe if not set
    @return:
    '''
    if startFrame == None:
        startFrame = pm.playbackOptions(q=1, min=1)
    if endFrame == None:
        endFrame = pm.playbackOptions(q=1, max=1)
    for f in range(int(startFrame),int(endFrame)):
        pm.currentTime(f)
        print 'Executing code on frame %s'%f
        exec(commandStr)





def infinity(type='linear'):
    pm.setInfinity(pri=type, poi=type)
    pm.keyTangent(itt='spline', ott='spline')


def copyKeys(source=None, target=None, channel=None, offset=0):
    if source == None or target == None:
        if len(pm.ls(sl=1))<2:
            return False

        target = pm.ls(sl=1)
        source = pm.ls(sl=1)[0]

    if channel == None:
        pm.copyKey(source)
    else:
        pm.copyKey(source, attribute=channel)
    i=0
    for each in target:
        print each
        if i>0:
            if channel == None:
                pm.pasteKey(each, timeOffset=offset*i)
            else:
                pm.pasteKey(each, attribute=channel, timeOffset=offset*i)
        i=i+1

def getQuickSelSets():
    import maya.cmds as cmds
    allSets=cmds.listSets(allSets=1)
    deformSet=cmds.listSets(t=1)
    shaderSet=cmds.listSets(t=2)

    unusedSet=["defaultCreaseDataSet", "initialTextureBakeSet", "initialVertexBakeSet", "tmpTextureBakeSet", "defaultObjectSet", "defaultLightSet"]
    allSets=[x for x in allSets if x not in deformSet]
    allSets=[x for x in allSets if x not in shaderSet]
    allSets=[x for x in allSets if x not in unusedSet]
    selSets = []
    unnSets = []
    for xSet in allSets:
        # Maya's cmd "listSets -as" not returning NS !!!
        if pm.objExists(xSet):
            if cmds.sets(xSet, q=1, t=1) == "gCharacterSet":
               selSets.append(xSet)
            else:
               unnSets.append(xSet)
        else:
            withNS=cmds.ls("*:" + str(xSet))
            if len(withNS) > 0 :
                print  withNS
                if cmds.sets(withNS[0], q=1, t=1) == "gCharacterSet":
                    print withNS
                    selSets.append(withNS[0])
                elif len(withNS) > 0 :
                    unnSets.append(withNS[0])
    return selSets + unnSets

def isolateChannel():
    selected = pm.selected()
    attr = 'translateY'
    pm.select(clear=1)
    for s in selected:
        pm.select(pm.ls("%s_%s" % (s.split(":")[-1], attr)), add=1)
