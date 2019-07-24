import pymel.core as pm
import re
'''
# Convert all shaders to aiStandard

mrShadersToArnold.py
...in C:\solidangle\mtoadeploy\2018\docs

'''


def createMaterial(name, color, shader):
    newNode = pm.shadingNode(shader, asShader=True, name=name)
    print 'new node created'

    pm.sets(renderable=True,
            noSurfaceShader=True,
            empty=True,
            name=newNode + 'SG')
    print 'sets'

    pm.setAttr(newNode + '.color',
               color[0],
               color[1],
               color[2],
               type='double3')
    pm.connectAttr(newNode + '.outColor', newNode + 'SG.surfaceShader')
    return newNode


def assignMaterial(name, target):
    pm.sets(name + 'SG', edit=True, forceElement=target)


def assignNewMaterial(name, color, shader, target):
    if pm.objExists(name):
        pm.warning(
            'Material with name %s already exists. Assigning existing.' % name)
        assignMaterial(name, target)
        return
    node = createMaterial(name, color, shader)
    print 'assigning %s' % node
    print 'target %s' % target
    assignMaterial(node, target)


def attachAODiffuse(shaders=None, samples=32, f=0):
    if shaders == None:
        shaders = pm.ls(sl=1)
    for shader in shaders:
        print shader
        diffuseinput = pm.listConnections('lambert5.diffuse')
        if diffuseinput != [] and f == 0:
            print 'diffuse of %s has already connections. Aborting. Use f=1 to force a connection' % shader
            continue
        if pm.objExists('occlusionShader'):
            occ = 'occlusionShader'
        else:
            occ = pm.mel.mrCreateCustomNode('-asTexture', "",
                                            'mib_amb_occlusion')
            occ = pm.rename(occ, 'occlusionShader')
            pm.setAttr("%s.samples" % occ, samples)
            pm.setAttr("%s.max_distance" % occ, 50)
        if pm.objExists('occlusionShaderLuminance'):
            luminance = 'occlusionShaderLuminance'
        else:
            luminance = pm.shadingNode('luminance',
                                       asUtility=1,
                                       name='occlusionShaderLuminance')

        pm.connectAttr('%s.outValue' % occ, '%s.value' % luminance, f=1)
        pm.connectAttr('%s.outValue' % luminance, '%s.diffuse' % shader, f=1)
    return shaders


def mentalraySetupSoftblast():
    # sampling
    pm.setAttr("miDefaultOptions.maxRefractionRays", 0)
    pm.setAttr("miDefaultOptions.maxRayDepth", 6)
    # motionblur
    pm.setAttr("miDefaultOptions.motionBlur", 2)
    pm.setAttr("miDefaultOptions.motionBlurShadowMaps", True)
    # shadow
    pm.setAttr("miDefaultOptions.maxShadowRayDepth", 3)
    pm.setAttr("miDefaultOptions.shadowMethod", 1)
    pm.setAttr("miDefaultOptions.shadowMaps", 1)


class Colour(pm.dt.Vector):
    NAMED_PRESETS = {
        "active": (0.26, 1, 0.64),
        "black": (0, 0, 0),
        "white": (1, 1, 1),
        "grey": (.5, .5, .5),
        "lightgrey": (.7, .7, .7),
        "darkgrey": (.25, .25, .25),
        "red": (1, 0, 0),
        "lightred": (1, .5, 1),
        "peach": (1, .5, .5),
        "darkred": (.6, 0, 0),
        "orange": (1., .5, 0),
        "lightorange": (1, .7, .1),
        "darkorange": (.7, .25, 0),
        "yellow": (1, 1, 0),
        "lightyellow": (1, 1, .5),
        "darkyellow": (.8, .8, 0.),
        "green": (0, 1, 0),
        "lightgreen": (.4, 1, .2),
        "darkgreen": (0, .5, 0),
        "blue": (0, 0, 1),
        "lightblue": (.4, .55, 1),
        "darkblue": (0, 0, .4),
        "purple": (.7, 0, 1),
        "lightpurple": (.8, .5, 1),
        "darkpurple": (.375, 0, .5),
        "brown": (.57, .49, .39),
        "lightbrown": (.76, .64, .5),
        "darkbrown": (.37, .28, .17)
    }

    NAMED_PRESETS['highlight'] = NAMED_PRESETS['active']
    NAMED_PRESETS['pink'] = NAMED_PRESETS['lightred']

    DEFAULT_COLOUR = NAMED_PRESETS['black']
    DEFAULT_ALPHA = 0.7  # alpha=0 is opaque, alpha=1 is transparent

    INDEX_NAMES = 'rgba'
    _EQ_TOLERANCE = 0.1

    _NUM_RE = re.compile('^[0-9. ]+')

    def __eq__(self, other, tolerance=_EQ_TOLERANCE):
        return pm.dt.Vector.__eq__(self, other, tolerance)

    def __ne__(self, other, tolerance=_EQ_TOLERANCE):
        return pm.dt.Vector.__ne__(self, other, tolerance)

    def __init__(self, colour):
        '''
        colour can be a combination:
        name alpha  ->  darkred 0.5
        name
        r g b a  ->  1 0 0 0.2
        if r, g, b or a are missing, they're assumed to be 0
        a 4 float, RGBA array is returned
        '''
        if isinstance(colour, basestring):
            alpha = self.DEFAULT_ALPHA
            toks = colour.lower().split(' ')[:4]

            if len(toks) > 1:
                if toks[-1].isdigit():
                    alpha = float(toks[-1])

            clr = [0, 0, 0, alpha]
            for n, c in enumerate(self.DEFAULT_COLOUR[:4]):
                clr[n] = c

            clr[3] = alpha

            if not toks[0].isdigit():
                try:
                    clr = list(self.NAMED_PRESETS[toks[0]])[:3]
                    clr.append(alpha)
                except KeyError:
                    pass
            else:
                for n, t in enumerate(toks):
                    try:
                        clr[n] = float(t)
                    except ValueError:
                        continue
        else:
            clr = colour

        pm.dt.Vector.__init__(self, clr)

    def darken(self, factor):
        '''
        returns a colour vector that has been darkened by the appropriate ratio.
        this is basically just a multiply, but the alpha is unaffected
        '''
        darkened = self * factor
        darkened[3] = self[3]

        return darkened

    def lighten(self, factor):
        toWhiteDelta = Colour((1, 1, 1, 0)) - self
        toWhiteDelta = toWhiteDelta * factor
        lightened = self + toWhiteDelta
        lightened[3] = self[3]

        return lightened

    def asRGB(self):
        return list(self)[:3]

    @classmethod
    def ColourToName(cls, theColour):
        '''
        given an arbitrary colour, will return the most appropriate name as
        defined in the NAMED_PRESETS class dict
        '''
        if not isinstance(theColour, Colour):
            theColour = Colour(theColour)

        theColour = pm.dt.Vector(theColour[:3])  # make sure its a 3 vector
        matches = []
        for name, colour in cls.NAMED_PRESETS.iteritems():
            colour = pm.dt.Vector(colour)
            diff = (colour - theColour).magnitude()
            matches.append((diff, name))

        matches.sort()

        return matches[0][1]


###############################
## break connection to shading network
###############################
def disconnectShaders(objArray=None):
    if objArray is None: objArray = pm.ls(sl=1)
    shapeNodes = []
    #for all selected obj
    for obj in objArray:
        #selection is mesh
        if pm.ls(obj, type='mesh'):
            shapeNodes.append(obj)
        #selection is not mesh. search hierarchy
        else:
            shapeNodes = shapeNodes + (pm.ls(obj, dag=1, ap=1, type='mesh'))
        if shapeNodes == []:
            print 'Warning: Select either mesh or transform nodes with valid shapes. %s' % (
                obj)
            #return False
        print shapeNodes
        #for all shape nodes
        for shapeNode in shapeNodes:
            conns = pm.listConnections(shapeNode)
            plugs = pm.listConnections(shapeNode,
                                       type='shadingEngine',
                                       connections=True)
            for conn in conns:
                if conn.type() == 'shadingEngine':
                    print 'Disconnecting shader engine: %s >>> %s' % (obj,
                                                                      conn)
                    #break ocnnection to shader
                    pm.disconnectAttr(plugs[0])


def getShaders(obj):
    pm.select(obj)
    pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
    return pm.ls(
        sl=True
    )  # Returns all shaders associated with the object (shape, face etc)


def copyPasteMaterial(objects):
    source = objects[0]
    target = objects[-1]

    pm.select(source)
    pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
    shaders = pm.ls(
        sl=True)  # all shaders associated with the object (shape, face etc)

    shader = [s for s in shaders if s.type() != 'renderLayer']
    shadingEngine = shader[0].listConnections(type='shadingEngine')

    pm.sets(shadingEngine[0], edit=True, forceElement=target)


def setReceiveShadow(objectList):
    for o in objectList:
        try:
            shape = o.getShape()
            print o
            pm.setAttr('%s.receiveShadows' % shape, 0)
        except:
            print 'no shape found. skipping'
            pass


def convertFileAlphaConnectionsToLuma():
    filenodes = pm.ls(type='file')

    pm.select(filenodes[0])
    for filenode in filenodes:
        alphaConnections = filenode.outAlpha.listConnections(plugs=1)
        for alphaConnection in alphaConnections:
            luminanceNode = pm.shadingNode('luminance', asUtility=1)
            filenode.outColor >> luminanceNode.value
            luminanceNode.outValue >> alphaConnection


def replaceBumpWithAiNormalForNormalFileNodes(filenodes='all'):
    if filenodes == 'all':
        filenodes = pm.ls(type='file')

    for filenode in filenodes:
        filename = filenode.fileTextureName.get().split('/')[-1].split('.')[0]
        if 'norm' in filename:
            print filename
            alphaConnections = filenode.outAlpha.listConnections(
                destination=1, plugs=1) + filenode.outColor.listConnections(
                    destination=1, plugs=1)

            for aplhaConnection in alphaConnections:
                print aplhaConnection.split('.')
                if aplhaConnection.split('.')[-1] == 'bumpValue':
                    print 'found normal file to bump connection: %s' % alphaConnection
                    destinationConnections = pm.listConnections(
                        aplhaConnection.split('.')[0] + '.outNormal',
                        destination=1,
                        plugs=1)
                    print 'destinationconnection is: %s' % destinationConnection
                    if destinationConnections == []:
                        print 'No destination Connection found for bump'
                        break
                    normalNode = pm.shadingNode('aiNormalMap', asUtility=1)
                    filenode.outColor >> normalNode.input
                    normalNode.outValue >> destinationConnection[0]
                    pm.delete(aplhaConnection.split('.')[0])


# def renameShadingTree(base_node, basename, target_attr = None, skip_nodes = ['defaultColorMgtGlobals']):
    
#     input_plugs =  base_node.connections(source=1, d=0, scn=1, plugs=1)
#     node_list = skip_nodes
    
#     for input_plug in input_plugs:
#         node = input_plug.plugNode()
#         if node in node_list:
#             continue
#         node_list.append(input_plug.plugNode())
        
#         node_type = node.nodeType()
#         if target_attr == None:
#             target_attr = input_plug.connections(plugs=1)[0].plugAttr(longName=True)
#         new_name = '%s_%s_%s01'%(basename, target_attr, node_type)
#         print 'input plug is %s. newname is %s'%(input_plug, new_name)
#         pm.rename(node, new_name)
#         renameChildren(node, basename, target_attr=target_attr)

# def renameSelectedShadingTree():
#     base_node = pm.selected()[0]
#     basename = base_node.replace('_ai', '')
#     renameShadingTree(base_node, basename, target_attr = None)

def renameShadingTree(base_node, basename, target_attr = None, skip_nodes = ['defaultColorMgtGlobals']):
    input_plugs =  base_node.connections(source=1, d=0, scn=1, plugs=1)
    node_list = skip_nodes
    if base_node.nodeType() == 'shadingEngine':
        input_plugs = base_node.volumeShader.connections(source=1, d=0, scn=1, plugs=1) + base_node.displacementShader.connections(source=1, d=0, scn=1, plugs=1)
        
    if base_node.nodeType() == 'aiStandardSurface':
        pm.rename(base_node, base_node.replace('_ai', '') + '_ai')
        basename = base_node.replace('_ai', '')
        print 'new basename is %s'%basename
    
    for input_plug in input_plugs:
        print 'input plug is %s'%input_plug
        print 'input plugtype is %s'%input_plug.nodeType()
        node = input_plug.plugNode()
        if node in node_list:
            continue
        node_list.append(input_plug.plugNode())
        
        node_type = node.nodeType()
        if target_attr == None:
            target_attr = input_plug.connections(plugs=1)[0].plugAttr(longName=True)
        new_name = '%s_%s_%s01'%(basename, target_attr, node_type)
        print 'input plug is %s. newname is %s'%(input_plug, new_name)
        #pm.rename(node, new_name)
        renameShadingTree(node, basename, target_attr=target_attr)

def renameSelectedShadingTree():
    """Rename the selected Shading tree. need to have shader selected
    """
    base_node = pm.PyNode('body_ai')
    basename = base_node.replace('_ai', '')
    SG = base_node.connections(t="shadingEngine")
    pm.rename(SG[0], base_node + 'SG')
    renameShadingTree(base_node, basename, target_attr=None)
    renameShadingTree(SG[0], basename, target_attr=None)

'''

def renameShadingTree(base_node, basename, target_attr = None, skip_nodes = ['defaultColorMgtGlobals']):
    input_plugs =  base_node.connections(source=1, d=0, scn=1, plugs=1)
    node_list = skip_nodes
    
    if base_node.nodeType() == 'shadingEngine':
        print 'shading engine'
        input_plugs = base_node.surfaceShader.connections(source=1, d=0, scn=1, plugs=1) + base_node.volumeShader.connections(source=1, d=0, scn=1, plugs=1) + base_node.displacementShader.connections(source=1, d=0, scn=1, plugs=1)
    
    for input_plug in input_plugs:
        print 'input plug is %s'%input_plug
        print 'input plugtype is %s'%input_plug.nodeType()
        print 'basename is %s'%basename
        node = input_plug.plugNode()
        if node in node_list:
            continue
        
        node_list.append(input_plug.plugNode())
        node_type = node.nodeType()
        
        if target_attr == None:
            target_attr = input_plug.connections(plugs=1)[0].plugAttr(longName=True)
        
        if  input_plug.connections(plugs=1)[0].nodeType() == 'aiStandardSurface':
            target_attr = input_plug.connections(plugs=1)[0].plugAttr(longName=True)
        else:
            new_name = '%s_%s_%s01'%(basename, target_attr, node_type)
            print 'node plug is %s. newname is %s'%(input_plug, new_name)
            pm.rename(node, new_name)     
        print 'target attr is %s'%target_attr
        renameShadingTree(node, basename, target_attr=target_attr)

def renameSelectedShadingTree():
    base_node = pm.PyNode('body_ai')
    basename = base_node.replace('_ai', '')
    SG = base_node.connections(t="shadingEngine")
    pm.rename(SG[0], base_node + 'SG')
    print 'start base name is %s'%basename
    renameShadingTree(SG[0], basename, target_attr=None)


import pymel.core as pm
renameSelectedShadingTree()


'''