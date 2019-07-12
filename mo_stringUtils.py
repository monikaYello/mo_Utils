import pymel.core as pm
import maya.cmds as cmds

def getSuffix(theObject):
    """ Desc:    Splits string and returns string behind _"""
    buffer = []
    buffer = theObject.split("_")
    return buffer[1]


def getPrefix(theObject):
    """ Desc:    Splits string and returns string before _"""
    buffer = []
    buffer = theObject.split("_")
    return buffer[0]


def removeNameSpace(theObject):
    """ Desc:    Removes the nameSpace of a given node and returns just the full name of the node
    :Parameters:  
        theObject : str
            a single object with namespace
    :Return:
        objNoNamesapce : str
    """
    buffer = []
    buffer = theObject.split(":")
    if len(buffer) == 2:
        return buffer[1]

    else:
        return buffer[0]


#######################
## renames all objects in hierarchy matching the name of the root objects
## for example root object name is 'C_neck_skinJnt' - hierarchy will be named C_neck1_skinJnt, C_neck2_skinJnt .....
## only objects of same type unless specified
#######################
def renameHierarchy(objects=None, type=None, prefix='C', suffix='ctrlJnt'):
    #name
    if objects == None:
        objects = pm.ls(sl=1)
    if objects == []:
        return

    for obj in objects:
        name = ''
        splitname = obj.name().split('_')

        if len(splitname) < 3:
            name = obj.name()
        else:
            prefix = splitname[0]
            name = splitname[1]
            suffix = splitname[2]

        type = obj.type()
        children = pm.listRelatives(obj, ad=1, type=type)

        i = 0
        for child in children:
            newname = '%s_%s%s_%s' % (prefix, name, len(children) + 1 - i,
                                      suffix)
            print 'renaming: %s >> %s' % (child, newname)
            pm.rename(child, newname)
            i = i + 1

        pm.rename(obj, '%s_%s%s_%s' % (prefix, name, 1, suffix))


def list_duplicates(seq=None):
    if seq == None:
        print 'searching scene'
        seq = [f.name() for f in pm.ls(tr=1) if '|' in f]
        print seq
        #short but slow: set([x for x in l if l.count(x) > 1])w
        seen = set()

        seen_add = seen.add
        print seen_add
        # adds all elements it doesn't know yet to seen and all other to seen_twice
        seen_twice = set()
        for x in seq:
            print x
            if x.rsplit('|')[1] in seen:
                seen_twice.add(x)
                print 'adding seen_twice %s' % x
            else:
                seen.add(x.rsplit('|')[1])
        #seen_twice = set( x for x in seq if  x.rsplit('|')[1] in seen or seen_add(x.rsplit('|')[1]) )

    else:
        #short but slow: set([x for x in l if l.count(x) > 1])w
        seen = set()
        seen_add = seen.add
        # adds all elements it doesn't know yet to seen and all other to seen_twice
        seen_twice = set(x for x in seq if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    return list(seen_twice)


def renameDuplicates(nodes=None, splitChar='', padding=2):
    # if an xform name contains a '|', it's appearing more than once and we'll have to rename it.
    badXforms = nodes
    if nodes == None:
        badXforms = [f.name() for f in pm.ls() if '|' in f.name()]
    else:
        badXforms = [f.name() for f in nodes if '|' in f.name()]

    badXformsUnlock = [
        f for f in badXforms if pm.lockNode(f, q=1, lock=1)[0] == False
    ]
    count = 0
    addChar = padding + len(splitChar)
    # sort list by the number of '|' in  name so we can edit names from the bottom of the hierarchy up,
    countDict = {}
    for f in badXformsUnlock:
        countDict[f] = f.count('|')
    # now sort the dictionary by value, in reverse, and start renaming.
    for key, value in sorted(countDict.iteritems(),
                             reverse=True,
                             key=lambda (key, value): (value, key)):
        n = 1
        newObj = pm.rename(
            key,
            key.split('|')[-1] + splitChar + str(n).zfill(padding))

        while newObj.count('|') > 0:
            #PREV INFINITE LOOP PROBLEM: if the transform and the shape are named the same
            n += 1
            basename = newObj.split('|')[-1]

            newName = basename[0:-addChar] + splitChar + str(n).zfill(padding)
            newObj = pm.rename(newObj, newName)
        print 'renamed %s to %s' % (key, newObj)
        count = count + 1
    if count < 1:
        print 'No duplicate names found.'
    else:
        print 'Found and renamed ' + str(
            count
        ) + ' objects with duplicate names. Check script editor for details.'
    return badXforms


SUFFIXES = {
    "mesh" : "geo",
    "joint" : "jnt",
    "transform" : "grp",
    "camera" : None

}
def renameObectsByType(selection=True):
    """
    This function will add object type as suffix for all or all selected objects
    Args:
        selection: Wheter or not we use the current selection or all objects

    Returns:
        A list of all the objects we operated on
    """
    objects = cmds.ls(selection=selection, dag=True, long=True)

    if selection and not objects:
        raise RuntimeError("You don't have anything selected! How dare you.")

    objects.sort(key=len, reverse=1)

    for obj in objects:
        print obj
        shortName = obj.split('|')[-1]
        children = cmds.listRelatives(obj, children=True, fullPath=1, ni=1) or []
        print 'children are %s'%children
        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
        elif len(children) > 1:
            childrenTypes = []
            for child in children:
                childrenType = cmds.objectType(child)
                childrenTypes.append(childrenType)
            if 'mesh' in childrenTypes:
                objType = 'mesh'
            else:
                objType = cmds.objectType(obj)
        else:
            objType = cmds.objectType(obj)
        print objType

        # get suffix
        suffix = SUFFIXES.get(objType, objType)

        # skip camera
        if not suffix:
            print "Skipping object with type %s"%cmds.objectTupe(obj)
            continue

        if obj.endswith(suffix):
            continue
        newName = '%s_%s'%(shortName, suffix)
        cmds.rename(obj, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    print('Done renaming %s objects.' % len(objects))
    return objects
