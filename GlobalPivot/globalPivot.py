## Global Pivot (Global Transform) Tool
## Paulo Scatena - http://scatena.tv
## Created: January 2017
## Modified: May 2017

from pyfbsdk import *

## Helper Functions

# "Smart" Plot
def SmartKey( pSrc, pDst, *pRefs):
    # Getting main nodes
    lNodes = []
    lNodes.append(pSrc.Translation.GetAnimationNode())
    lNodes.append(pSrc.Rotation.GetAnimationNode())
    
    # Getting optional ref nodes
    for Ref in pRefs:
        lNodes.append(Ref.Translation.GetAnimationNode())
        lNodes.append(Ref.Rotation.GetAnimationNode())

    # Getting curves
    lFCurves = []
    # Add curves if node exists
    for Node in (Node for Node in lNodes if Node):
        for SubNode in Node.Nodes:
            lFCurves.append(SubNode.FCurve)
    
    # Get all the key times
    lKeytimes = []
    for fC in lFCurves:
        for Key in fC.Keys:
            lKeytimes.append(Key.Time.Get())

    # Get rid of duplicates
    lKeytimes = list(set(lKeytimes))
    lKeytimes.sort()

    # If there are no keys, just snap
    if len(lKeytimes) == 0:
        Snap( pDst, pSrc )
    
    # Pseudo smart - Set keys on all times found, using KeyAdd directly on the node
    lPlayerControl = FBPlayerControl()
    lTranslation = pDst.Translation;
    lTraNode = lTranslation.GetAnimationNode()
    lRotation = pDst.Rotation;
    lRotNode = lRotation.GetAnimationNode()
    lInterp = FBInterpolation.kFBInterpolationCubic # Auto
    lTangen = FBTangentMode.kFBTangentModeClampProgressive # Auto
    for Time in lKeytimes:
        lPlayerControl.Goto( FBTime(Time) )
        # Translation
        lData = [lTranslation.Data[0], lTranslation.Data[1], lTranslation.Data[2]]
        lTraNode.KeyAdd(FBTime(Time), lData, lInterp, lTangen);
        # Rotation
        lData = [lRotation.Data[0], lRotation.Data[1], lRotation.Data[2]]
        lRotNode.KeyAdd(FBTime(Time), lData, lInterp, lTangen);


# Every Frame Plot Helper
def PlotKeys( pDst ):
    # Set plot options
    lOptions = FBPlotOptions()
    lOptions.ConstantKeyReducerKeepOneKey = False
    lOptions.PlotAllTakes = False
    lOptions.PlotLockedProperties = False
    lOptions.PlotOnFrame = False
    # Plot period = 1/fps
    lOptions.PlotPeriod = FBTime(int(FBTime().OneSecond.Get() / FBPlayerControl().GetTransportFpsValue()))
    lOptions.PlotTangentMode = FBPlotTangentMode.kFBPlotTangentModeAuto
    lOptions.PlotTranslationOnRootOnly = False
    lOptions.PreciseTimeDiscontinuities = False
    lOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
    lOptions.UseConstantKeyReducer = False
    # Deselect - just plot on main node
    Deselect()
    pDst.Selected = True
    FBSystem().CurrentTake.PlotTakeOnSelected( lOptions )


# Deselect Everything Helper
def Deselect():
    for lComp in (lComp for lComp in FBSystem().Scene.Components if lComp != None and lComp.Selected):
        lComp.Selected = False


# Snap destination to location
def Snap( lDst, lSrc ):
    # snap translation
    lVector = FBVector3d()
    # true for global
    lSrc.GetVector(lVector, FBModelTransformationType.kModelTranslation, True)
    lDst.Translation = lVector
    # snap rotation
    lSrc.GetVector(lVector, FBModelTransformationType.kModelRotation, True)
    lDst.Rotation = lVector


# Check if object exists (not only wrapper, but in actual scene)
def NotExists( pArray ):
    for item in pArray:
        if not item:
            return True
        if not FBFindModelByLabelName(item.Name):
            return True
    return False


# Reset Tool - For Fresh Start (avoiding errors)
def ResetTool( pClearList ):
    if ( tool.PivotMarker ):
        tool.PivotMarker.FBDelete()
        tool.PivotMarker = None
    if ( tool.RootControl ):
        tool.RootControl.FBDelete()
        tool.RootControl = None
    if ( tool.Constraint ):
        tool.Constraint.FBDelete()
        tool.Constraint = None
    if ( pClearList ):
        tool.ListRoot.Items.removeAll()
        tool.RootModel = None
    # Deactivate buttons
    tool.bsetup.Enabled = False
    tool.bplot.Enabled = False
            
        
## UI Callbacks

# Drag and Drop for main node
def EventListDragAndDrop(control, event):
    if event.State == FBDragAndDropState.kFBDragAndDropDrag:
        event.Accept()
    elif event.State == FBDragAndDropState.kFBDragAndDropDrop:
        # Check if is model
        if event.Components[-1] == FBFindModelByLabelName(event.Components[-1].LongName):
            control.Items.removeAll()
            control.Items.append(event.Components[-1].Name)
            tool.RootModel = event.Components[-1]
            # if there is marker, activate setup
            if ( "PivotMarker" in dir(tool) ):
                if ( tool.PivotMarker ):
                    tool.bsetup.Enabled = True


# OnChange Callback to keep UI list deselected
def EventListDeselect(control, event):
    control.Selected(0, False);


# Create Pivot Button Callback
def BtnCallbackPivot(control, event):
    # Clear if exists
    if ( tool.PivotMarker ):
        # But check if there is root control (meaning has been setup)
        if ( tool.RootControl ):
            if ( FBMessageBox( "Warning", "Tool has already been set up.\nReset tool?", "OK", "Cancel" ) == 1 ):
                # Reset tool ( False for keep list intact )
                ResetTool( False )
            else: # Case of cancel or escape (2, False)
                return False
        else:
            tool.PivotMarker.FBDelete() 
    # Create new marker
    tool.PivotMarker = FBModelMarker('GlobalPivot')
    tool.PivotMarker.Show = True
    # Set its look
    tool.PivotMarker.Size = 300
    tool.PivotMarker.Look = FBMarkerLook.kFBMarkerLookHardCross
    # If there is selection, snap to it
    lModels = FBModelList()
    FBGetSelectedModels(lModels)
    if len(lModels):
        Snap(tool.PivotMarker, lModels[-1] )
    # If there is model, activate setup
    if ( "RootModel" in dir(tool) ):
        if ( tool.RootModel ):
            tool.bsetup.Enabled = True
    # Deselect all and select newly created marker
    Deselect()
    tool.PivotMarker.Selected = True


# Setup Button Callback
def BtnCallbackSetup(control, event):
    # Safety check
    if ( NotExists( [tool.RootModel, tool.PivotMarker] ) ):
        if ( FBMessageBox( "Error", "Main nodes were not found.\nReset tool?", "OK", "Cancel" ) == 1 ):
            # Reset tool ( True for reset list )
            ResetTool( True )
        return False
    
    # Check if already has been setup
    if ( tool.RootControl ):
        FBMessageBox( "Warning", "Tool has already been set up.", "OK" )
        return False
    
    
    # Add a null to snap to root
    tool.RootControl = FBModelNull('RootControl')
    # Make it a son of pivot
    tool.RootControl.Parent = tool.PivotMarker

    # Step 1
    # Add constraint
    tool.Constraint = FBConstraintManager().TypeCreateConstraint( "Parent/Child" )
    tool.Constraint.Name = "GlobalPivotConstraint"
    
    # Add null as child
    tool.Constraint.ReferenceAdd(0, tool.RootControl)
    # Add root as parent
    tool.Constraint.ReferenceAdd(1, tool.RootModel)
    # Activate
    tool.Constraint.Active = True
    # Evaluate 
    FBSystem().Scene.Evaluate()
    
    # If "smart bake"
    if tool.bsmart.State:
        SmartKey( tool.RootModel, tool.RootControl )
    else:
        # Plot every frame
        PlotKeys( tool.RootControl )
    
    # Step 2
    # Deactivate constraint
    tool.Constraint.Active = False
    # Remove references
    tool.Constraint.ReferenceRemove(0, tool.RootControl)
    tool.Constraint.ReferenceRemove(1, tool.RootModel)
    # Reverse references
    tool.Constraint.ReferenceAdd(1, tool.RootControl)
    tool.Constraint.ReferenceAdd(0, tool.RootModel)
    # Reactivate
    tool.Constraint.Active = True
    
    # Activate plot back button
    tool.bplot.Enabled = True
    
    # Deactivate setup
    tool.bsetup.Enabled = False
    

# Plot Back Button Callback
def BtnCallbackPlot(control, event):
    # Safety check
    if ( NotExists( [tool.RootControl, tool.RootModel, tool.PivotMarker] ) ):
        FBMessageBox( "Error", "Something went wrong. Try setting up again, or plot manually", "OK" )
        return False
    
    # Open Undo Stack
    lUndo = FBUndoManager()  
    lUndo.TransactionBegin("plot")
    
    lUndo.TransactionAddModelTRS( tool.RootModel )
    
    # If "smart bake"
    if tool.bsmart.State:
        # Copy back keys
        SmartKey( tool.RootControl, tool.RootModel, tool.PivotMarker )
    else:
        # Plot every frame
        PlotKeys( tool.RootModel )
    # Cleanup
    ResetTool( True )
    
    # Close Undo Stack
    lUndo.TransactionEnd()


# Populate Tool
def PopulateTool(mainLyt):
    # Populating regions
    # Label
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(8,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(180,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(16,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ToolLabel","ToolLabel", x, y, w, h)

    ToolLabel = FBLabel()
    mainLyt.SetControl("ToolLabel", ToolLabel)
    ToolLabel.Caption = "Root object:"
    ToolLabel.WordWrap = True

    # Using the tool itself to keep track of the root model
    tool.RootModel = None

    # Root list
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(6,FBAttachType.kFBAttachBottom,"ToolLabel")
    w = FBAddRegionParam(180,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(20,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ListRoot","ListRoot", x, y, w, h)
   
    tool.ListRoot = FBList()
    mainLyt.SetControl("ListRoot", tool.ListRoot)
    tool.ListRoot.Hint = "Drag object (root) here"
    tool.ListRoot.Style = FBListStyle.kFBVerticalList
    tool.ListRoot.OnChange.Add(EventListDeselect)
    tool.ListRoot.OnDragAndDrop.Add(EventListDragAndDrop)

    # Create pivot button
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(8,FBAttachType.kFBAttachBottom,"ListRoot")
    w = FBAddRegionParam(87,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(20,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ButtonPivot","ButtonPivot", x, y, w, h)

    # Using the tool itself to keep track of the pivot marker, aux pivot and contraint
    tool.PivotMarker = None
    tool.RootControl = None
    tool.Constraint = None
    
    b = FBButton()
    mainLyt.SetControl("ButtonPivot", b)
    b.Hint = "Create new pivot point\n(will snap to selection)"
    b.Caption = "Create Pivot"
    b.OnClick.Add(BtnCallbackPivot)
    
    # Setup button
    x = FBAddRegionParam(100,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(8,FBAttachType.kFBAttachBottom,"ListRoot")
    w = FBAddRegionParam(87,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(20,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ButtonSetup","ButtonSetup", x, y, w, h)

    tool.bsetup = FBButton()
    mainLyt.SetControl("ButtonSetup", tool.bsetup)
    tool.bsetup.Enabled = False
    tool.bsetup.Hint = "Configure tool for global pivot transformation"
    tool.bsetup.Caption = "Setup"
    tool.bsetup.OnClick.Add(BtnCallbackSetup)

    # Instructions label
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(16,FBAttachType.kFBAttachBottom,"ButtonPivot")
    w = FBAddRegionParam(180,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(16,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("SubLabel","SubLabel", x, y, w, h)

    SubLabel = FBLabel()
    mainLyt.SetControl("SubLabel", SubLabel)
    SubLabel.Caption = "Edit or animate marker before plot."
    SubLabel.WordWrap = True

    # Plot button
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(6,FBAttachType.kFBAttachBottom,"SubLabel")
    w = FBAddRegionParam(180,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(20,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ButtonPlot","ButtonPlot", x, y, w, h)

    tool.bplot = FBButton()
    mainLyt.SetControl("ButtonPlot", tool.bplot)
    tool.bplot.Enabled = False
    tool.bplot.Hint = "Plot pivot transformations to object"
    tool.bplot.Caption = "Plot Transform and Cleanup"
    tool.bplot.OnClick.Add(BtnCallbackPlot)
    
    # Population arrow
    lyt = FBHBoxLayout()
    
    # Radio buttons
    group = FBButtonGroup()
    
    tool.bsmart = FBButton()
    group.Add(tool.bsmart)
    tool.bsmart.Style = FBButtonStyle.kFBRadioButton
    tool.bsmart.Caption = "Smart"
    tool.bsmart.State = 1
    lyt.Add(tool.bsmart,60)
    
    b = FBButton()
    group.Add(b)
    b.Style = FBButtonStyle.kFBRadioButton
    b.Caption = "Every frame"

    lyt.Add(b,90)

    # Arrow button
    x = FBAddRegionParam(7,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(6,FBAttachType.kFBAttachBottom,"ButtonPlot")
    w = FBAddRegionParam(180,FBAttachType.kFBAttachNone,"")
    h = FBAddRegionParam(10,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("ArrowName","", x, y, w, h)
    
    b = FBArrowButton()
    mainLyt.SetControl("ArrowName" ,b)
    
    b.SetContent("Plot Options (beta)", lyt, 200, 20 )
    
    
# Tool Creation
def CreateTool():
    global tool
    tool = FBCreateUniqueTool("Global Pivot Tool")
    tool.StartSizeX = 210
    tool.StartSizeY = 220
    PopulateTool(tool)
    ShowTool(tool)


# Call Tool ("unsafe" method - implies recreating it)
CreateTool()

