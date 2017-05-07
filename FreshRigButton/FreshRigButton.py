#################################
###
### Fresh Rig Button
### Paulo Scatena, Jan 2015
### phscatena@gmail.com
###
#################################
###
### This tool plots the animation of the current character to the
### skeleton and plots back to a fresh FK/IK Control Rig.
### If there are no active control rig, it will just plot to a fresh one.
###
### Flags for additional control are available below.
###
#################################

from pyfbsdk import *
from pyfbsdk_additions import FBCreateUniqueTool, FBHBoxLayout, FBVBoxLayout

# Fresh Rig Code
def CreateFreshRig(control, event):
    
    # Plot options
    # (more about it on the docs)
    # http://docs.autodesk.com/MB/2015/ENU/#!/url=./files/GUID-FF721B07-D791-4F31-A9F4-FAA29D313B6F.htm
    
    lOptions = FBPlotOptions()
    
    ## OPEN TO CUSTOM INPUT ##
    
    # Should we plot all takes?
    lOptions.PlotAllTakes = True
    
    # Should we plot locked properties?
    lOptions.PlotLockedProperties = False
    
    # Should we plot on frame?
    lOptions.PlotOnFrame = True
    
    # The plot period (meaning "plot every X frames")
    lOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
    
    # Should we plot the translation on root only?
    lOptions.PlotTranslationOnRootOnly = True
    
    # The rotation filter to apply.
    lOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
    
    # Should we use a constant key reducer with the filter?
    lOptions.UseConstantKeyReducer = True
    
    # Should the constant key reducer keep at least one key?
    lOptions.ConstantKeyReducerKeepOneKey = True
    
    # Should we use precise time dicontinuities?
    lOptions.PreciseTimeDiscontinuities = True
    
    ## CUSTOM INPUT ENDS ##
    
    
    # This gets the current character
    lChar = FBApplication().CurrentCharacter
    
    # This generates a warning if no character is active
    if not lChar:
        FBMessageBox( "Warning","No character is active.","OK")
        return False
    
    # This gets the Control Rig (it is a FBControlSet object)
    lCtrlSet = lChar.GetCurrentControlSet()
    
    # This plots animation to the skeleton
    if lCtrlSet and lChar.ActiveInput:
        # This condition placed to check if the animation is actually coming from the control rig.
        # If it is not and you try to plot it this way, it will delete all skeleton animation.
        lChar.PlotAnimation (FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton,lOptions )
    
    # This deletes the control rig, if it exists
    if lCtrlSet:
        lCtrlSet.FBDelete()
    
    # And plots back to a fresh rig
    lChar.CreateControlRig(True)
    lChar.PlotAnimation (FBCharacterPlotWhere.kFBCharacterPlotOnControlRig,lOptions )
    
    # Making sure it is active (this might be redundant)
    lChar.ActiveInput=1


# This creates the button
def PopulateLayout(mainLyt):
    
    
    x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
    y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
    w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
    h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
    mainLyt.AddRegion("main","main", x, y, w, h)
    main = FBVBoxLayout()
    mainLyt.SetControl("main",main)
    
    lyt = FBHBoxLayout()

    empty = FBHBoxLayout()
    lyt.AddRelative(empty,.1)
    
    b = FBButton()
    b.Caption = "Fresh Rig"
    b.Justify = FBTextJustify.kFBTextJustifyCenter
    lyt.AddRelative(b,3)
    b.OnClick.Add(CreateFreshRig)
    
    empty = FBHBoxLayout()
    lyt.AddRelative(empty,.1)

    main.AddRelative(lyt,1)
    

# This creates the window for the button
def CreateTool():
    t = FBCreateUniqueTool("Fresh Rig Button")
    t.StartSizeX = 150
    t.StartSizeY = 50
    PopulateLayout(t)
    ShowTool(t)
    
# This runs the tool
CreateTool()