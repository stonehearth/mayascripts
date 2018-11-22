Here is a link to our github repository with the Maya 2015 scripts which were written while working on Stonehearth: https://github.com/stonehearth/mayascripts

DIsclaimer TLDR:
This code may not work.
This code is styled poorly.
This code is overly commented and has lots of ugly, unused code within it.
Despite this, we hope that giving this code away will in some way help you all, our modders : ).

(More at bottom)
______________________________________________________________________

Rough descriptions/explanations:
Animation Scripts:
Some general helper type scripts - like the swap value buttons (useful to attempting to mirror without putting in more work on a real mirroring script), also some generic maya issue fixes (like viewport fix - which does as expected).
Also the last stage of animation work - exporting.  These create the formats that we are specifically looking for in Stonehearth.
Rig Adjustment Scripts:
Some scripts which adjust a completed rig, either to be helpful while animating or to actually add something to a rig.
Some corrective scripts for when rigs/geometry are broken (like clean selected meshes - which fixes a random issue with maya’s geo which sometimes occurs).
An experimental script (bubblesoft) playing with possible looks that never went anywhere.
Rig Creation Scripts:
This is the real meat and potatoes of the scripts.  The names/explanations of the UI should (hopefully) make sense, but in general, a mesh is imported, cleaned, the user moves pivot points, then runs all scripts with default values or steps through the process and does minor changes as they go.
These scripts are mostly split in two columns - they do not mix between (you either make a human rig, or a generic rig).
Mass Conversion Scripts:
These scripts were useful when we made the conversion from 3DSMax to Maya.
Also needed these occasionally when doing batch updates, like when making some change to the base rig and needing to re-export all animations in a folder.
And some random scripts that ended up being needed due to random issues with the other scripts.
Other Tabs:
Other random scripts that were written at one point or another.  These scripts are even less likely to work, but were still useful on occasion.

______________________________________________________________________


Disclaimer 1:
Please be aware, we don’t intend to update these scripts or even promise that they are functional now.  The reason we are releasing these is to show our processes and to allow any modders to use these (all, or in part) to improve their own skills.

Disclaimer 2: 
The version of Maya which these scripts were designed to be run in is Maya 2015, they very likely will not work properly outside of that version.  Some of these scripts may also have never worked in the first place, be half finished, or provide an output which is different than the description states.  So ye’ be warned.

Disclaimer 3:
These scripts in general were written by someone (me - Matt Malley) who barely has a grasp on python and coding in general, so be aware that many things I have done are not ‘best practice’, ‘good practice’, or even ‘common sense’.  I was under a timer and was not sure if anyone would ever use these scripts besides myself.  The descriptions above are fairly vague, but within each script you will see that I over-comment all my code (at times to insane levels), put descriptions above (nearly) every function, and left extra comments for myself where things were especially misbehaving or confusing.  There are also large sections of code which are commented out because I wanted to try something new, and never cleaned up afterwards.  I could go through and clean all this stuff out, but honestly that would take a long time and may actually not be as beneficial as showing you all some of the mistakes I made along the way.  But - I wanted to at least attempt to explain the ugly code, the method behind the madness.

