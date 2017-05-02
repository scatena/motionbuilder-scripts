# Global Pivot Tool

Script for transforming objects - animated or not - in global space.
Demonstration video: https://vimeo.com/215409208

## Instructions

Run the tool - it has a graphical user interface.
- Drag and drop the object you wish to control (usually root of hierarchy);
- To set where you want the pivot to be, click "Create Pivot" and reposition auxiliary marker (note: if any object is selected, newly created marker will snap to the one selected last);
- Click setup to plot root animation to auxiliary node;
- Move / transform / animate the reference Pivot ("GlobalPivot") to your liking;
- Click "Plot Transform and Cleanup" to make changes permanent. Undo and repeat if necessary.

Note 1: If you reach any error after set-up and want to start over, just click "Create Marker" and you will be prompted to reset the tool.
Note 2: Tool uses by default a self-implemented 'smart-plot'. If you are having issues with how animation is being transfered, try choosing "Every Frame" under "Plot Options".

## Installation

To execute the script, either:
- Drag and drop the file from an external explorer to MotionBuilder's viewport, choose execute;
- Add the scripts folder to your Asset Browser, drag and drop to viewport, execute;
- Open the Python Editor window, load the script file, run it.