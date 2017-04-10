## Mirror joints for proper characterization
## Paulo Scatena - http://scatena.tv
## Created: September 2015
## Modified: March 2017

from pyfbsdk import FBApplication, FBMessageBox, FBVector3d, FBModelTransformationType

## Auxiliary Functions ##

#Checking if the property is a joint Link
def checkName(lProperty, sideString):
    return lProperty.GetName().startswith(sideString) and lProperty.GetName().endswith('Link')

#Creating filtered lists for left and right joints
def listLinks(lChar):
    lPropertyList = lChar.PropertyList
    lFilteredRight = []
    lFilteredLeft = []
    for lProperty in lPropertyList:
        if checkName(lProperty, "Left"):
            lFilteredLeft.append(lProperty)
        if checkName(lProperty, "Right"):
            lFilteredRight.append(lProperty)
    lFilteredTuple = (lFilteredLeft, lFilteredRight)
    return lFilteredTuple

#Mirroring the joints from one side to the other
def mirrorJoints(srcList,dstList):
    
    # Open Undo Stack
    lUndo = FBUndoManager()  
    lUndo.TransactionBegin("mirror")
    
    #Empty vector to store rotation
    lRotation = FBVector3d()
    for i in range(len(srcList)):
        if len(srcList[i]):
            # Add Model TRS in Undo Stack
            lUndo.TransactionAddModelTRS(dstList[i][0])
            #Get vector
            srcList[i][0].GetVector (lRotation, FBModelTransformationType.kModelRotation)
            #Making adjustments to the values
            if lRotation[0] > 90:
                lRotation[0]=lRotation[0]-180
            elif lRotation[0] < 90:
                lRotation[0]=lRotation[0]+180
            else:
                lRotation[0]=-lRotation[0]
            lRotation[1]=-lRotation[1]
            lRotation[2]=-lRotation[2]
            #Setting the values for the corresponding opposite link
            dstList[i][0].SetVector (lRotation,
            FBModelTransformationType.kModelRotation, True)

    # Close Undo Stack
    lUndo.TransactionEnd()


## Calling the functions ##

#The current character is the one used
lChar = FBApplication().CurrentCharacter

if not lChar:
    FBMessageBox( "Warning", "No character is currently selected.", "Ok" )
    print "Script terminated. No character selected."

if lChar:
    if lChar.GetCharacterize():
        FBMessageBox( "Warning", "Characterization is already locked.\n       Changes will likely be lost.", "Ok" )

    # User input
    lDirection = FBMessageBox( "Mirror Characterization - Select Direction", "(Hips must be facing +Z axis)", "Left to Right", "Right to Left", "Cancel" )

    if lDirection < 3:
        # Getting the lists
        lFilteredTuple = listLinks(lChar)
        lLeftList = lFilteredTuple[0]
        lRightList = lFilteredTuple[1]




    if lDirection == 1:
        #Left to right
        mirrorJoints(lLeftList,lRightList)
    
    if lDirection == 2:
        #Right to left
        mirrorJoints(lRightList,lLeftList)



# Cleanup.
del( FBApplication, FBMessageBox, FBVector3d, FBModelTransformationType )
