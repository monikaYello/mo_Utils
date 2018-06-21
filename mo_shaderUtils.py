import pymel.core as pm

def createMaterial(name, color, shader):
    newNode = pm.shadingNode(shader, asShader = True, name = name)
    pm.sets(renderable = True, noSurfaceShader = True, empty = True, name = newNode + 'SG')
    pm.setAttr(newNode + '.color', color[0], color[1], color[2], type = 'double3')
    pm.connectAttr(newNode + '.outColor', newNode + 'SG.surfaceShader')
    return newNode


def assignMaterial(name, target):
    pm.sets(target, edit = True, forceElement = name + 'SG')


def assignNewMaterial(name, color, shader, target):
    if pm.objExists(name):
        pm.warning('Material with name %s already exists. Assigning existing.'%name)
        assignMaterial(name, target)
        return
    node = createMaterial(name, color, shader)
    assignMaterial(node, target)





def attachAODiffuse(shaders=None, samples=32, f=0):
    if shaders == None:
        shaders = pm.ls(sl=1)
    for shader in shaders:
        print shader
        diffuseinput = pm.listConnections('lambert5.diffuse')
        if diffuseinput != [] and f == 0:
            print 'diffuse of %s has already connections. Aborting. Use f=1 to force a connection'%shader
            continue
        if pm.objExists('occlusionShader'):
            occ = 'occlusionShader'
        else:
            occ = pm.mel.mrCreateCustomNode('-asTexture', "", 'mib_amb_occlusion')
            occ = pm.rename(occ, 'occlusionShader')
            pm.setAttr("%s.samples"%occ, samples)
            pm.setAttr("%s.max_distance"%occ, 50)
        if pm.objExists('occlusionShaderLuminance'):
            luminance = 'occlusionShaderLuminance'
        else:
            luminance = pm.shadingNode('luminance', asUtility=1, name='occlusionShaderLuminance')
            
        pm.connectAttr('%s.outValue'%occ, '%s.value'%luminance, f=1)
        pm.connectAttr('%s.outValue'%luminance, '%s.diffuse'%shader, f=1)
    return shaders


def mentalraySetupSoftblast():
    #sampling
    pm.setAttr("miDefaultOptions.maxRefractionRays", 0)
    pm.setAttr("miDefaultOptions.maxRayDepth", 6)
    #motionblur
    pm.setAttr("miDefaultOptions.motionBlur", 2)
    pm.setAttr("miDefaultOptions.motionBlurShadowMaps", True)
    #shadow
    pm.setAttr("miDefaultOptions.maxShadowRayDepth", 3)
    pm.setAttr("miDefaultOptions.shadowMethod", 1)
    pm.setAttr("miDefaultOptions.shadowMaps", 1)


class Colour(Vector):
	NAMED_PRESETS = { "active": (0.26, 1, 0.64),
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
	                  "darkyellow": (.8,.8,0.),
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
	                  "darkbrown": (.37, .28, .17) }

	NAMED_PRESETS[ 'highlight' ] = NAMED_PRESETS[ 'active' ]
	NAMED_PRESETS[ 'pink' ] = NAMED_PRESETS[ 'lightred' ]

	DEFAULT_COLOUR = NAMED_PRESETS[ 'black' ]
	DEFAULT_ALPHA = 0.7  #alpha=0 is opaque, alpha=1 is transparent

	INDEX_NAMES = 'rgba'
	_EQ_TOLERANCE = 0.1

	_NUM_RE = re.compile( '^[0-9. ]+' )

	def __eq__( self, other, tolerance=_EQ_TOLERANCE ):
		return Vector.__eq__( self, other, tolerance )
	def __ne__( self, other, tolerance=_EQ_TOLERANCE ):
		return Vector.__ne__( self, other, tolerance )
	def __init__( self, colour ):
		'''
		colour can be a combination:
		name alpha  ->  darkred 0.5
		name
		r g b a  ->  1 0 0 0.2
		if r, g, b or a are missing, they're assumed to be 0
		a 4 float, RGBA array is returned
		'''
		if isinstance( colour, basestring ):
			alpha = self.DEFAULT_ALPHA
			toks = colour.lower().split( ' ' )[ :4 ]

			if len( toks ) > 1:
				if toks[ -1 ].isdigit():
					alpha = float( toks[ -1 ] )

			clr = [0,0,0,alpha]
			for n, c in enumerate( self.DEFAULT_COLOUR[ :4 ] ):
				clr[ n ] = c

			clr[ 3 ] = alpha

			if not toks[ 0 ].isdigit():
				try:
					clr = list( self.NAMED_PRESETS[ toks[ 0 ] ] )[ :3 ]
					clr.append( alpha )
				except KeyError: pass
			else:
				for n, t in enumerate( toks ):
					try: clr[ n ] = float( t )
					except ValueError: continue
		else:
			clr = colour

		Vector.__init__( self, clr )
	def darken( self, factor ):
		'''
		returns a colour vector that has been darkened by the appropriate ratio.
		this is basically just a multiply, but the alpha is unaffected
		'''
		darkened = self * factor
		darkened[ 3 ] = self[ 3 ]

		return darkened
	def lighten( self, factor ):
		toWhiteDelta = Colour( (1,1,1,0) ) - self
		toWhiteDelta = toWhiteDelta * factor
		lightened = self + toWhiteDelta
		lightened[ 3 ] = self[ 3 ]

		return lightened
	def asRGB( self ):
		return list( self )[ :3 ]
	@classmethod
	def ColourToName( cls, theColour ):
		'''
		given an arbitrary colour, will return the most appropriate name as
		defined in the NAMED_PRESETS class dict
		'''
		if not isinstance( theColour, Colour ):
			theColour = Colour( theColour )

		theColour = Vector( theColour[ :3 ] )  #make sure its a 3 vector
		matches = []
		for name, colour in cls.NAMED_PRESETS.iteritems():
			colour = Vector( colour )
			diff = (colour - theColour).magnitude()
			matches.append( (diff, name) )

		matches.sort()

		return matches[ 0 ][ 1 ]

