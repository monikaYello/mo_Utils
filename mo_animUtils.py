import random
import pymel.core as pm
import maya.cmds as cmds

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
    for f in range(int(startFrame), int(endFrame)):
        pm.currentTime(f)
        print 'Executing code on frame %s' % f
        exec(commandStr)


def infinity(type='linear'):
    pm.setInfinity(pri=type, poi=type)
    pm.keyTangent(itt='spline', ott='spline')


def copyKeys(source=None, target=None, channel=None, offset=0):
    if source == None or target == None:
        if len(pm.ls(sl=1)) < 2:
            return False

        target = pm.ls(sl=1)
        source = pm.ls(sl=1)[0]

    if channel == None:
        pm.copyKey(source)
    else:
        pm.copyKey(source, attribute=channel)
    i = 0
    for each in target:
        print each
        if i > 0:
            if channel == None:
                pm.pasteKey(each, timeOffset=offset*i)
            else:
                pm.pasteKey(each, attribute=channel, timeOffset=offset*i)
        i = i+1



def setTimesliderToKeyrange():
    keyedObj = pm.ls(sl=1)
    firstKf = pm.findKeyframe(which='first')
    lastKf = pm.findKeyframe(which='last')
    pm.playbackOptions(min=firstKf, max=lastKf)
    return [firstKf, lastKf]

def keyEmpty(obj=None):
    if obj == None:
      obj = pm.ls(sl=1)[0]
    if isinstance(obj, list):
      obj = obj[0]
    channels = pm.listAttr(obj, keyable=1)
    for channel in channels:
        if pm.listConnections('%s.%s'%(obj, channel)) == []:
            print 'setting keyframe on %s.%s'%(obj, channel)
            pm.setKeyframe('%s.%s'%(obj, channel))
#key bang
def keyFlash(obj=None, channel=None, fade=18):
    if obj==None:
        obj=pm.ls(sl=1)[0]
    if channel==None:
        channel = 'translateX'
    current = pm.currentTime(q=1)
    
    kf = [current-1, current, current+1, current+fade]
    
    value = pm.getAttr('%s.%s'%(obj, channel))   
    #see if already keys
    if pm.listConnections('%s.%s'%(obj, channel)) is not []:
        pm.cutKey(obj, at=channel, time=(kf[0], kf[-1]))
        
    
    pm.setKeyframe(obj,  at=channel, v=0, t=[kf[0]], ott='stepnext')
    pm.setKeyframe(obj,  at=channel, v=value, t=[kf[1]], ott='stepnext')
    pm.setKeyframe(obj,  at=channel, v=value*0.75, t=[kf[2]], ott='auto')
    pm.setKeyframe(obj,  at=channel, v=0, t=[kf[3]], ott='auto')
    
    pm.keyTangent(obj,  at=channel, a=1, outWeight=1, e=1, t=[kf[2]], outAngle=-10.253096)
    
def keyFastinSlowout(obj=None, channel=None, span=18):
    if obj==None:
        obj=pm.ls(sl=1)[0]
    if channel==None:
        channel = 'translateX'
    current = pm.currentTime(q=1)
    
    kf = [current, current+span]
    
    value = pm.getAttr('%s.%s'%(obj, channel))
    #see if already keys
    if pm.listConnections('%s.%s'%(obj, channel)) is not []:
       pm.cutKey(obj, at=channel, time=(kf[0], kf[-1]))
       
    pm.setKeyframe(obj,  at=channel, v=value, t=[kf[0]], ott='linear')
    pm.setKeyframe(obj,  at=channel, v=value+12, t=[kf[1]], ott='auto')     
    
    pm.keyTangent(obj,  at=channel, a=1, outWeight=1, e=1, t=[kf[0]], outAngle=57.815214) 
               
def getQuickSelSets():
    import maya.cmds as cmds
    allSets = cmds.listSets(allSets=1)
    deformSet = cmds.listSets(t=1)
    shaderSet = cmds.listSets(t=2)

    unusedSet = ["defaultCreaseDataSet", "initialTextureBakeSet",
                 "initialVertexBakeSet", "tmpTextureBakeSet", "defaultObjectSet", "defaultLightSet"]
    allSets = [x for x in allSets if x not in deformSet]
    allSets = [x for x in allSets if x not in shaderSet]
    allSets = [x for x in allSets if x not in unusedSet]
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
            withNS = cmds.ls("*:" + str(xSet))
            if len(withNS) > 0:
                print withNS
                if cmds.sets(withNS[0], q=1, t=1) == "gCharacterSet":
                    print withNS
                    selSets.append(withNS[0])
                elif len(withNS) > 0:
                    unnSets.append(withNS[0])
    return selSets + unnSets


def isolateChannel():
    selected = pm.selected()
    attr = 'translateY'
    pm.select(clear=1)
    for s in selected:
        pm.select(pm.ls("%s_%s" % (s.split(":")[-1], attr)), add=1)


def bakeTimeWarp(objects, start, end, killWarp=True):
    # for each frame between start and end, query time1.outTime and time1.unwarpedTime
    # for each object, get each channel with at least one keyframe set
    # for each channel:
    #     get the value of the channel at outTime
    #     set the channel to this value at unwarpedTime and set a keyframe

    # # testing #
    # objects = cmds.ls(sl=1)
    # start = int(cmds.playbackOptions(q=1, min=1))
    # end = int(cmds.playbackOptions(q=1, max=1))

    for i in objects:
        dupe = cmds.duplicate(i, po=1)[0]
        if not cmds.attributeQuery('bakeTimeWarpConnection', node=i, ex=1):
            cmds.addAttr(i, ln='bakeTimeWarpConnection', at='message')
        cmds.connectAttr(dupe+'.message', i+'.bakeTimeWarpConnection')
    for x in range(start, end+1):
        cmds.currentTime(x)
        outTime = cmds.getAttr('time1.outTime')
        unwarpedTime = cmds.getAttr('time1.unwarpedTime')
        for i in objects:
            # build a list of all keyed channels.
            keyables = cmds.listAttr(i, k=1)
            keyedChans = [
                f for f in keyables if cmds.keyframe(i+'.'+f, q=1, n=1)]
            dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
            for chan in keyedChans:
                val = cmds.getAttr(i+'.'+chan, t=outTime)
                cmds.setAttr(dupe+'.'+chan, val)
                cmds.setKeyframe(dupe+'.'+chan, t=unwarpedTime)
    # now reconnect anim curves from the duplicate to the original. then delete the duplicates and finally remove the timewarp.
    for i in objects:
        dupe = cmds.listConnections(i+'.bakeTimeWarpConnection')[0]
        chans = [f for f in cmds.listAttr(
            dupe, k=1) if cmds.keyframe(dupe+'.'+f, q=1, n=1)]
        for chan in chans:
            animCurve = cmds.keyframe(dupe+'.'+chan, q=1, n=1)[0]
            oldCurve = cmds.keyframe(i+'.'+chan, q=1, n=1)
            cmds.connectAttr(animCurve+'.output', i+'.'+chan, f=1)
            cmds.delete(oldCurve)
        cmds.delete(dupe)
        cmds.deleteAttr(i+'.bakeTimeWarpConnection')
    if killWarp:
        timeWarp = cmds.listConnections('time1.timewarpIn_Raw')[0]
        cmds.delete(timeWarp)


def offsetKeyframe(timechChange, nodes='all'):
    if nodes == 'all':
        anim_curves = cmds.ls(
            type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
    else:
        anim_curves = pm.ls(nodes)
    for each in anim_curves:
        cmds.keyframe(each, edit=True, relative=True, timeChange=timechChange)


def scaleKeyframes(by=1.041666666666667, nodes='all'):
    # to do a scene conversion from 25 to 24 frames per sec
    if nodes == 'all':
        anim_curves = cmds.ls(
            type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
    else:
        anim_curves = nodes

    for each in anim_curves:
        pm.scaleKey(each, timeScale=by)
    print 'Done. Scaled %s Keyframe' % len(anim_curves)


def convertFrameRate(fromFPS, toFPS, nodes='all'):
    '''

    :param fromFPS: originial frame rate, eg 25
    :param toFPS: target frame rate, eg 24
    :param nodes: the nodes to scale. All will scale all keyframes in the scene
    :return: scaledKeys: Nr of keys to be scaled

    example:
    convertFrameRate(25, 24, nodes='all')
    '''
    scaledKeys = []

    by = (float(fromFPS) * 1.0000000) / (float(toFPS) * 1.000000)
    print 'Scaling by %s' % by

    if nodes == 'all':
        anim_curves = cmds.ls(
            type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
    else:
        anim_curves = nodes

    for each in anim_curves:
        try:
            pm.scaleKey(each, timeScale=by)
            scaledKeys.append(each)
        except:
            pass
    print 'Done. Scaled %s Keyframe by %s' % (len(scaledKeys), by)
    return len(scaledKeys)


def copyPasteKeyWithOffset(rctrls, rsuffix='R_', lsuffix='L_'):
    pm.select(rctrls)
    for rctrl in rctrls:
        lctrl = rctrl.replace(rsuffix, lsuffix)
        print 'lctrl is %s' % lctrl
        rc = pm.copyKey(rctrl, t=(0, 31))
        pm.pasteKey(lctrl, t=31, o="merge")
        try:
            pm.cutKey(lctrl, t=(32, 66))
        except:
            pass
        pm.pasteKey(lctrl, t=32, o="merge")


def randomizeRotationAndScale():
    for geo in pm.selected():
        geo.ry.set(random.uniform(0, 360))
        geo.sy.set(random.uniform(0.8, 1.2))



def popAnimRaiseTranslateY(objs, startframe=1):
    i=startframe
    keyframe1 = 1
    keyframe2 = keyframe1 + 6
    keyframe3 = keyframe1 + 9
    for obj in objs:
        pm.currentTime(keyframe1, u=0)
        pm.setKeyframe("%s.ty" %obj)
        pm.currentTime(keyframe2, u=0)
        pm.setAttr("%s.translateY" %obj, 50)
        pm.setKeyframe("%s.ty" %obj)
        pm.currentTime(keyframe3, u=0)
        pm.setAttr("%s.translateY" %obj, 0)
        pm.setKeyframe("%s.ty" %obj, itt="linear")
        if i % 10 == 0:
            keyframe1 = keyframe1 + 1
            keyframe2 = keyframe1 + 6
            keyframe3 = keyframe1 + 9
        i= i+1

def popAnimFallTranslateY(objs, startframe=1, height=1300, offset=10):
    i=0
    keyframe1 = startframe
    keyframe2 = keyframe1 + 6
    keyframe3 = keyframe1 + 9
    keyframe4 = keyframe1 + 11
    for obj in objs:
        pm.cutKey(obj)
        endpose_ty = pm.getAttr("%s.ty"%obj)
        endpose_scale = pm.getAttr("%s.scale"%obj)[0]
        pm.setKeyframe("%s.scale"%obj, t=keyframe1, v= 0)
        pm.setKeyframe("%s.scale"%obj, t=keyframe1+4, v= endpose_scale)
        pm.setKeyframe("%s.ty"%obj, t=keyframe1, v= endpose_ty + height)
        pm.setKeyframe("%s.ty"%obj, t=keyframe2, v= endpose_ty, itt="linear", ott="linear")
        pm.setKeyframe("%s.ty"%obj, t=keyframe3, v= endpose_ty + (height/50.0))
        pm.setKeyframe("%s.ty"%obj, t=keyframe4, v= endpose_ty, itt="linear")
        if i % offset == 0:
            keyframe1 = keyframe1 + 1
            keyframe2 = keyframe1 + 6
            keyframe3 = keyframe1 + 9
            keyframe4 = keyframe1 + 11
        i= i+1


def popAnimFallTranslateYWiggle(objs, startframe=1, height=1300):
    i=0
    keyframe1 = startframe
    keyframe2 = keyframe1 + 6
    keyframe3 = keyframe1 + 9
    keyframe4 = keyframe1 + 11
    for obj in objs:
        endpose_ty = pm.getAttr("%s.ty"%obj)
        endpose_rx = pm.getAttr("%s.rotateX"%obj)
        pm.setKeyframe("%s.ty"%obj, t=keyframe1, v= endpose_ty + height)
        pm.setKeyframe("%s.ty"%obj, t=keyframe2, v= endpose_ty, itt="linear", ott="linear")
        pm.setKeyframe("%s.ty"%obj, t=keyframe3, v= endpose_ty + (height/50.0))
        pm.setKeyframe("%s.ty"%obj, t=keyframe4, v= endpose_ty, itt="linear")
        # rotate
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe3, v= endpose_rx)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe4, v= endpose_rx+12)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe4+6, v= endpose_rx-12)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe4+10, v= endpose_rx)
        if i % 10 == 0:
            keyframe1 = keyframe1 + 1
            keyframe2 = keyframe1 + 6
            keyframe3 = keyframe1 + 9
            keyframe4 = keyframe1 + 11
        i= i+1


def popAnimScaleYWiggle(objs, startframe=1, offset=2):
    i=0
    keyframe1 = startframe
    keyframe2 = keyframe1 + 6
    keyframe3 = keyframe1 + 9
    keyframe4 = keyframe1 + 11
    for obj in objs:
        pm.cutKey(obj)
        endpose_scale = pm.getAttr("%s.scale"%obj)[0]
        endpose_rx = pm.getAttr("%s.rotateX"%obj)
        pm.setKeyframe("%s.scale"%obj, t=keyframe1, v=0)
        pm.setKeyframe("%s.scale"%obj, t=keyframe2, v=endpose_scale*1.1)
        pm.setKeyframe("%s.scale"%obj, t=keyframe3, v=endpose_scale, itt="linear")

        # rotate
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe2, v= endpose_rx)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe3, v= endpose_rx+12)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe3+4, v= endpose_rx-12)
        pm.setKeyframe("%s.rotateX"%obj, t=keyframe3+8, v= endpose_rx)
        if i % offset == 0:
            keyframe1 = keyframe1 + 1
            keyframe2 = keyframe1 + 6
            keyframe3 = keyframe1 + 9
        i= i+1

def popAnimScale(objs, startframe=1, offset=2):
    i=0
    keyframe1 = startframe
    keyframe2 = keyframe1 + 6
    keyframe3 = keyframe1 + 9
    for obj in objs:
        pm.currentTime(keyframe1, u=0)
        pm.setAttr("%s.scaleZ" %obj, 0)
        pm.setAttr("%s.scaleY" %obj, 0)
        pm.setAttr("%s.scaleX" %obj, 0)
        pm.setKeyframe("%s.sx" %obj, "%s.sy" %obj, "%s.sz" %obj)
        pm.currentTime(keyframe2, u=0)
        pm.setAttr("%s.scaleZ" %obj, 1.15)
        pm.setAttr("%s.scaleY" %obj, 1.15)
        pm.setAttr("%s.scaleX" %obj, 1.15)
        pm.setKeyframe("%s.sx" %obj, "%s.sy" %obj, "%s.sz" %obj)
        pm.currentTime(keyframe3, u=0)
        pm.setAttr("%s.scaleZ" %obj, 1)
        pm.setAttr("%s.scaleY" %obj, 1)
        pm.setAttr("%s.scaleX" %obj, 1)
        pm.setKeyframe("%s.sx" %obj, "%s.sy" %obj, "%s.sz" %obj, itt="linear")
        if i % offset == 0:
            keyframe1 = keyframe1 + 2
            keyframe2 = keyframe1 + 6
            keyframe3 = keyframe1 + 9
        i= i+1
      
def popAnimVisibility(objs, startframe=1):
    i=0
    keyframe1 = startframe
    keyframe2 = keyframe1 + 1
    for obj in objs:
        pm.currentTime(keyframe1, u=0)
        pm.setAttr("%s.visibility" %obj, 0)
        pm.setKeyframe("%s.v" %obj)
        pm.currentTime(keyframe2, u=0)
        pm.setAttr("%s.visibility" %obj, 1)
        pm.setKeyframe("%s.v" %obj)
        if i % 1 == 0:
            keyframe1 = keyframe1 + 1
            keyframe2 = keyframe1 + 1
        i= i+1