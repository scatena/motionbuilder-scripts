# FRESH RIG BUTTON

Developed Jan 2015

## -- INFO --

This tool plots the animation of the current character to the skeleton and plots back to a fresh FK/IK Control Rig.

If there are no active control rig, it will just plot to a fresh one.

## -- USAGE --

- Single use:

Just drag and drop the .py file to the viewport from explorer or Asset browser and execute.

You might dock the window anywhere you like.


- Continuous use:

Copy FreshRigButton.py to C:\Users\#yourname#\Documents\MB\#yourversion#\config\PythonStartup (create folder if necessary).

Drag and drop the .py file to the viewport.

Dock the window anywhere you like and save the layout.

From now on, it should open with MotionBuilder automatically.

## -- MORE INFO --

It works with the current character only.


Files with several takes will take longer to process.


Properties set by default:

  - Plot all takes*.
  - Plot on frame.
  - Plot translation on root only.
  - Applies Unroll filter.
  - Constant key reducer active.

Anyone can change theses properties by editing the .py 
file (it should be easy).

###### * A NOTE ON TAKES

As the scripts plots the animation to the skeleton and deletes 
the control rig, all former control rig animation is lost.

"Plot all takes" is now ON by default as a safe precaution.