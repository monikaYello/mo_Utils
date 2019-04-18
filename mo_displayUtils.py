import pymel.core as pm


###############################
## Select and Returns Array of all nodes in hierarchy with specified type
###############################
def selectHierarchy(type=None, objArray=None):
    returnNodes = []
    if objArray is None: objArray = pm.ls(sl=1)
    for obj in objArray:
        pm.select(obj)
        if type == None:
            returnNodes.append(pm.ls(dag=1, ap=1, sl=1))
        else:
            returnNodes.append(pm.ls(dag=1, ap=1, sl=1, type=type))
        #pm.select(pm.ls(dag=1, ap=1, sl=1, type='joint')) 'nurbsCurve' 'constraint' 'mesh'
    pm.select(returnNodes)
    print returnNodes
    
###############################
## Returns Array of display layers of objArray/selection
###############################
def getDisplayLayer(objArray = None):
    displayLayers = []
    if objArray is None: 
        objArray = pm.ls(sl=1)
    for obj in objArray:
        conns = pm.listConnections(obj)
        for conn in conns:
            if conn.type() == 'displayLayer':
                print 'Object in Display Layer: %s >>> %s'%(obj, conn)
                displayLayers.append(conn)
    return displayLayers
       
       
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
        if shapeNodes ==[]:
            print 'Warning: Select either mesh or transform nodes with valid shapes. %s'%(obj)
            #return False
        print shapeNodes   
        #for all shape nodes
        for shapeNode in shapeNodes:
            conns = pm.listConnections(shapeNode)
            plugs = pm.listConnections(shapeNode, type='shadingEngine', connections=True)
            for conn in conns:
                if conn.type() == 'shadingEngine':
                    print 'Disconnecting shader engine: %s >>> %s'%(obj, conn)
                    #break ocnnection to shader
                    pm.disconnectAttr(plugs[0])
                
###############################
## delete specific refeference edits that contain searchString
## default deletes all shader associated edits
## other searchstrings: 'Shape' - all modifications to shape
###############################
def deleteRefEdits(refNodes=None, searchStrings=['SG', 'material']):
    #prepare refNode, argument or selection,  make it array :
    if refNodes == None:
        refNodes = pm.ls(sl=1)
    elif type(refNodes) == str:
        refNodes = [refNodes]
        
    #run through all objects 
    for refNode in refNodes:
        namespace = refNode.split(':')[0]
        
        #find matching refrence node
        refNodes = pm.listReferences()
        refFound = False
        for refNode in refNodes:
            if namespace == refNode.namespace:
                refFound = refNode
        if refNode == False: print 'Error: No Reference Node found. Select either referenced object or pass namespace'
             
        refEdits = refFound.getReferenceEdits()  
        rebuild = []
        
        #run through all ref edits
        for refEdit in refEdits:
            matchingRef = False
            #find match searchstring in refEdit
            for searchString in searchStrings:
                if searchString in refEdit:
                    matchingRef=True
                    break 
                    
            if matchingRef == True:
                #split - type of edit command - edit dommand
                editC = refEdit.partition(' ')[0].strip()
                editR = refEdit.partition('"')[2].partition('"')[0].strip()
                refFound.removeReferenceEdits(editCommand=editC, removeEdits=editR, successfulEdits=1, failedEdits=1, force=True)
            #need to rebuild connectAttr types after clean up to restore animation        
            elif 'connectAttr' in refEdit:
                rebuild.append(refEdit)   
        refFound.load()
        
        #rebuild animation connection nodes
        for reb in rebuild:
            try: maya.mel.eval(reb)
            except: continue
    return rebuild

def closeAllFloatingWindows():
    openwins = pm.lsUI(wnd=1)
    for openwin in openwins:
        print openwin
        if openwin.name() != 'MayaWindow':
            print openwin.name()
            pm.deleteUI(openwin)

def layoutCleanScripting(name='cleanOutliner/Persp/ScriptEditor'):

    import maya.cmds as cmds
    '''

    import mo_Utils.mo_displayUtil as mo_displayUtil
    mo_displayUtil.customScriptLayout()
    '''
    closeAllFloatingWindows()
    try:
        configName=cmds.getPanel(cwl=name)
        cmds.deleteUI(configName, panelConfig=1)
    except: pass


    cmds.panelConfiguration(defaultImage="defaultThreeSplitRightLayout.png",
        label=(pm.mel.localizedPanelLabel(name)),
        ap=[(False, (pm.mel.localizedPanelLabel("Outliner")), "outlinerPanel", "$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName", "outlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName"),
            (True, (pm.mel.localizedPanelLabel("Persp View")), "modelPanel", "$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1438\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName", "modelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1438\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName"),
            (False, (pm.mel.localizedPanelLabel("Script Editor")), "scriptedPanel", "$panelName = `scriptedPanel -unParent  -type \"scriptEditorPanel\" -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels `", "scriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName")],
        sc=False,
        configString="global string $gMainPane; paneLayout -e -cn \"right3\" -ps 1 14 100 -ps 2 86 40 -ps 3 86 60 $gMainPane;",
        image="")

    pm.mel.eval('setNamedPanelLayout( "%s" )'%name)
    #pm.deleteUI(configName, panel=1)

def layoutCleanAnim(name='cleanOutliner/Persp/Graph'):

    import maya.cmds as cmds
    '''

    import mo_Utils.mo_displayUtil as mo_displayUtil
    mo_displayUtil.customScriptLayout()
    '''
    closeAllFloatingWindows()
    try:
        configName=cmds.getPanel(cwl=name)
        cmds.deleteUI(configName, panelConfig=1)
    except: pass


    cmds.panelConfiguration(defaultImage="defaultThreeSplitRightLayout.png",
        label=(pm.mel.localizedPanelLabel(name)),
        ap=[(False, (pm.mel.localizedPanelLabel("Outliner")), "outlinerPanel", "$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName", "outlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName"),
            (True, (pm.mel.localizedPanelLabel("Persp View")), "modelPanel", "$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1438\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName", "modelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1438\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName"),
            (False, (pm.mel.localizedPanelLabel("Graph Editor")), "scriptedPanel", "$panelName = `scriptedPanel -unParent  -type \"graphEditor\" -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -isSet 0\n                -isSetMember 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                -selectionOrder \"display\" \n                -expandAttribute 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -clipTime \"on\" \n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName", "scriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -isSet 0\n                -isSetMember 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                -selectionOrder \"display\" \n                -expandAttribute 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -clipTime \"on\" \n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName")],
        sc=False,
        configString="global string $gMainPane; paneLayout -e -cn \"right3\" -ps 1 11 100 -ps 2 89 50 -ps 3 89 50 $gMainPane;",
        image="")

    pm.mel.eval('setNamedPanelLayout( "%s" )'%name)
    #pm.deleteUI(configName, panel=1)

def layoutCleanOutliner(name='cleanPersp/Outliner'):

    import maya.cmds as cmds
    '''

    import mo_Utils.mo_displayUtil as mo_displayUtil
    mo_displayUtil.layoutCleanOutliner()
    '''
    closeAllFloatingWindows()
    try:
        configName=cmds.getPanel(cwl=name)
        cmds.deleteUI(configName, panelConfig=1)
    except: pass


    pm.panelConfiguration(defaultImage="defaultTwoSideBySideLayout.png",
        label=(pm.mel.localizedPanelLabel(name)),
        ap=[(False, (pm.mel.localizedPanelLabel("Outliner")), "outlinerPanel", "$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName", "outlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\noutlinerEditor -e \n    -docTag \"isolOutln_fromSeln\" \n    -showShapes 0\n    -showAssignedMaterials 0\n    -showReferenceNodes 1\n    -showReferenceMembers 1\n    -showAttributes 0\n    -showConnected 0\n    -showAnimCurvesOnly 0\n    -showMuteInfo 0\n    -organizeByLayer 1\n    -showAnimLayerWeight 1\n    -autoExpandLayers 1\n    -autoExpand 0\n    -showDagOnly 1\n    -showAssets 1\n    -showContainedOnly 1\n    -showPublishedAsConnected 0\n    -showContainerContents 1\n    -ignoreDagHierarchy 0\n    -expandConnections 0\n    -showUpstreamCurves 1\n    -showUnitlessCurves 1\n    -showCompounds 1\n    -showLeafs 1\n    -showNumericAttrsOnly 0\n    -highlightActive 1\n    -autoSelectNewObjects 0\n    -doNotSelectNewObjects 0\n    -dropIsParent 1\n    -transmitFilters 0\n    -setFilter \"defaultSetFilter\" \n    -showSetMembers 1\n    -allowMultiSelection 1\n    -alwaysToggleSelect 0\n    -directSelect 0\n    -isSet 0\n    -isSetMember 0\n    -displayMode \"DAG\" \n    -expandObjects 0\n    -setsIgnoreFilters 1\n    -containersIgnoreFilters 0\n    -editAttrName 0\n    -showAttrValues 0\n    -highlightSecondary 0\n    -showUVAttrsOnly 0\n    -showTextureNodesOnly 0\n    -attrAlphaOrder \"default\" \n    -animLayerFilterOptions \"allAffecting\" \n    -sortOrder \"none\" \n    -longNames 0\n    -niceNames 1\n    -showNamespace 1\n    -showPinIcons 0\n    -mapMotionTrails 0\n    -ignoreHiddenAttribute 0\n    -ignoreOutlinerColor 0\n    -renderFilterVisible 0\n    -renderFilterIndex 0\n    -selectionOrder \"chronological\" \n    -expandAttribute 0\n    $editorName"),
            (True, (pm.mel.localizedPanelLabel("Persp View")), "modelPanel", "$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\nmodelEditor -e \n    -cam `findStartUpCamera persp` \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1430\n    -height 732\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName", "modelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\nmodelEditor -e \n    -cam `findStartUpCamera persp` \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 1430\n    -height 732\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName")],
        sc=False,
        configString="global string $gMainPane; paneLayout -e -cn \"vertical2\" -ps 1 12 100 -ps 2 88 100 $gMainPane;",
        image="")


    pm.mel.eval('setNamedPanelLayout( "%s" )'%name)
    #pm.deleteUI(configName, panel=1)

def layoutCleanTrak(name='cleanPersp/Outliner'):

    import maya.cmds as cmds
    '''

    import mo_Utils.mo_displayUtil as mo_displayUtil
    mo_displayUtil.customScriptLayout()
    '''
    closeAllFloatingWindows()
    try:
        configName=cmds.getPanel(cwl=name)
        cmds.deleteUI(configName, panelConfig=1)
    except: pass
    trakcam = pm.ls('trak:*', type='camera')[0]

    cmds.panelConfiguration(defaultImage="defaultThreeSplitTopLayout.png",
        label=(pm.mel.localizedPanelLabel("animateTrak")),
        ap=[(True, (pm.mel.localizedPanelLabel("Top View")), "modelPanel", "$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 807\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName", "modelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"persp\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 807\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName"),
            (True, (pm.mel.localizedPanelLabel("Side View")), "modelPanel", "$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels `;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"" + trakcam + "\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 807\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName", "modelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n$editorName = $panelName;\nmodelEditor -e \n    -camera \"trak:cam\" \n    -useInteractiveMode 0\n    -displayLights \"default\" \n    -displayAppearance \"smoothShaded\" \n    -activeOnly 0\n    -ignorePanZoom 0\n    -wireframeOnShaded 0\n    -headsUpDisplay 1\n    -holdOuts 1\n    -selectionHiliteDisplay 1\n    -useDefaultMaterial 0\n    -bufferMode \"double\" \n    -twoSidedLighting 0\n    -backfaceCulling 0\n    -xray 0\n    -jointXray 0\n    -activeComponentsXray 0\n    -displayTextures 0\n    -smoothWireframe 0\n    -lineWidth 1\n    -textureAnisotropic 0\n    -textureHilight 1\n    -textureSampling 2\n    -textureDisplay \"modulate\" \n    -textureMaxSize 16384\n    -fogging 0\n    -fogSource \"fragment\" \n    -fogMode \"linear\" \n    -fogStart 0\n    -fogEnd 100\n    -fogDensity 0.1\n    -fogColor 0.5 0.5 0.5 1 \n    -depthOfFieldPreview 1\n    -maxConstantTransparency 1\n    -rendererName \"vp2Renderer\" \n    -objectFilterShowInHUD 1\n    -isFiltered 0\n    -colorResolution 256 256 \n    -bumpResolution 512 512 \n    -textureCompression 0\n    -transparencyAlgorithm \"frontAndBackCull\" \n    -transpInShadows 0\n    -cullingOverride \"none\" \n    -lowQualityLighting 0\n    -maximumNumHardwareLights 1\n    -occlusionCulling 0\n    -shadingModel 0\n    -useBaseRenderer 0\n    -useReducedRenderer 0\n    -smallObjectCulling 0\n    -smallObjectThreshold -1 \n    -interactiveDisableShadows 0\n    -interactiveBackFaceCull 0\n    -sortTransparent 1\n    -nurbsCurves 1\n    -nurbsSurfaces 1\n    -polymeshes 1\n    -subdivSurfaces 1\n    -planes 1\n    -lights 1\n    -cameras 1\n    -controlVertices 1\n    -hulls 1\n    -grid 1\n    -imagePlane 1\n    -joints 1\n    -ikHandles 1\n    -deformers 1\n    -dynamics 1\n    -particleInstancers 1\n    -fluids 1\n    -hairSystems 1\n    -follicles 1\n    -nCloths 1\n    -nParticles 1\n    -nRigids 1\n    -dynamicConstraints 1\n    -locators 1\n    -manipulators 1\n    -pluginShapes 1\n    -dimensions 1\n    -handles 1\n    -pivots 1\n    -textures 1\n    -strokes 1\n    -motionTrails 1\n    -clipGhosts 1\n    -greasePencils 1\n    -shadows 0\n    -captureSequenceNumber -1\n    -width 807\n    -height 344\n    -sceneRenderFilter 0\n    $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\nmodelEditor -e \n    -pluginObjects \"gpuCacheDisplayFilter\" 1 \n    $editorName"),
            (False, (pm.mel.localizedPanelLabel("Graph Editor")), "scriptedPanel", "$panelName = `scriptedPanel -unParent  -type \"graphEditor\" -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -isSet 0\n                -isSetMember 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                -selectionOrder \"display\" \n                -expandAttribute 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -clipTime \"on\" \n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName", "scriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -isSet 0\n                -isSetMember 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                -selectionOrder \"display\" \n                -expandAttribute 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -clipTime \"on\" \n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName")],
        sc=False,
        configString="global string $gMainPane; paneLayout -e -cn \"top3\" -ps 1 50 50 -ps 2 50 50 -ps 3 100 50 $gMainPane;",
        image="")


    pm.mel.eval('setNamedPanelLayout( "%s" )'%name)
    #pm.deleteUI(configName, panel=1)


def viewportSnapshot(name=None, savelocation = None):
    #Import api modules
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI
    
    if savelocation is None:
       savelocation = pm.workspace.getcwd() 
    if name is None:
       name='MayaViewportSnapshot'
    #Grab the last active 3d viewport
    view = apiUI.M3dView.active3dView()
     
    #read the color buffer from the view, and save the MImage to disk
    image = api.MImage()
    view.readColorBuffer(image, True)
    image.writeToFile('%s%s.jpg'%(savelocation,name), 'jpg')
    print 'Snapshot saved in %s%s.jpg'%(savelocation,name)


def toggleFlatShaded():
    activeview = pm.getPanel(up=1)
    if 'modelPanel' in activeview:
        nurbsCurvesstatus = pm.modelEditor(activeview, q=1, dl=1)

        if nurbsCurvesstatus == "default":
            pm.modelEditor(activeview, dl="flat", e=1)
        else:
            pm.modelEditor(activeview, dl="default", e=1)

def toggleGeometryVisibility():
    activeview=pm.getPanel(wf=1)
    if 'modelPanel' in activeview:
        nurbsCurvesstatus=pm.modelEditor(activeview, q=1, polymeshes=1)

        if nurbsCurvesstatus:
            pm.modelEditor(activeview, e=1, polymeshes=0)
        else:
            pm.modelEditor(activeview, e=1, polymeshes=1)


def toggleCurvesVisibility():
    activeview = pm.getPanel(wf=1)
    if 'modelPanel' in activeview:
        nurbsCurvesstatus = pm.modelEditor(activeview, q=1, nurbsCurves=1)

    if nurbsCurvesstatus:
        pm.modelEditor(activeview, e=1, nurbsCurves=0)
    else:
        pm.modelEditor(activeview, e=1, nurbsCurves=1)


def changeASSmode(obj_list='all', mode=0):
    '''
    set display types of each arnoldStandin in obj list to defined mode

    modes
    0   boundingbox
    1   boundingbox per object
    3   wireframe 
    4   polywire
    5   pointcloud
    6   shaded

    obj_list = pm.ls(sl=True)
    '''
    if obj_list == 'all':
        obj_list  = pm.ls(type=pm.nodetypes.AiStandIn)
    
    for obj in obj_list:
        print obj
        try: # get shape and set
            obj.getShape().mode.set(mode)
        except:
            try: # have shape and set
                obj.getShape().mode.set(mode)
            except:
                continue
