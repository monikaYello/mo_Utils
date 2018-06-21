import pymel.core as pm

def getSuffix(theObject):
    """ Desc:    Splits string and returns string behind _"""
    buffer=[]
    buffer=theObject.split("_")
    return buffer[1]

def getPrefix(theObject):
    """ Desc:    Splits string and returns string before _"""
    buffer=[]
    buffer=theObject.split("_")
    return buffer[0]

def removeNameSpace(theObject):
    """ Desc:    Removes the nameSpace of a given node and returns just the full name of the node
    :Parameters:  
        theObject : str
            a single object with namespace
    :Return:
        objNoNamesapce : str
    """
    buffer=[]
    buffer=theObject.split(":")
    if len(buffer) == 2:
        return buffer[1]
        
    
    else:
        return buffer[0]
    
#######################
## renames all objects in hierarchy matching the name of the root objects
## for example root object name is 'C_neck_skinJnt' - hierarchy will be named C_neck1_skinJnt, C_neck2_skinJnt .....
## only objects of same type unless specified
#######################
def renameHierarchy(objects = None, type=None,prefix='C', suffix='ctrlJnt'):
    #name
    if objects == None:
        objects = pm.ls(sl=1)
    if  objects == []:
        return
         
    for obj in objects:
        name = ''
        splitname =obj.name().split('_')
        
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
            newname = '%s_%s%s_%s'%(prefix, name, len(children)+1-i, suffix)
            print 'renaming: %s >> %s'%(child, newname)
            pm.rename(child, newname)
            i = i+1
            
        pm.rename(obj, '%s_%s%s_%s'%(prefix, name, 1, suffix))