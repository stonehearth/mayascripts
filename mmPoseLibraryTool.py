Atom Export Example

# precision - No idea what this is.
# statics - No idea what this is.
# baked - This is asking if it should bake down sdk animations - i think the general answer is no?  because that's not part of the animation, that's part of the rig.
# sdk - No idea what this is.
# constraint - This is asking if constraints should be baked down - generally no.
# animLayers - Unsure about this, documentation makes it sound like True means only this layer, False means all layers.  think we generally want False.
# selected - Probably always want selectedOnly, but this allows different ways of determining what selection to store animation data from.
# whichRange - This can either be 1 for all, or 2 for 'use the range value' - probably always want it to be 2 and just specify the range manually.
# range - This is the actual frame number start:end, and they can be the same number.
# hierarchy - No idea what this is.
# controlPoints - This is No. Documentation makes it sound like this tries to export animation from cv curves and vertices (like for a morph target).
# useChannelBox - 1 is "all keyable", 2 is "from channel box".  Probably better to leave this as 1.
# options - No idea what this is.
# copyKeyCmd=-animation objects -time >0:14> -float >0:14> -option keys -hierarchy none -controlPoints 0
#  This all appears to be duplicate information of what is already passed in, but at least looks to be important that it matches the above.
#     'time' and 'float' appear to be the same as range, everything else should probably always stay as they are here.
mmOptions = """
precision=8;
statics=1;
baked=0;
sdk=0;
constraint=0;
animLayers=1;
selected=selectedOnly;
whichRange=2;
range=0:14;
hierarchy=none;
controlPoints=0;
useChannelBox=1;
options=keys;
copyKeyCmd=-animation objects -time >0:14> -float >0:14> -option keys -hierarchy none -controlPoints 0
"""
cmds.file( "C:/Users/mmalley/Documents/Work/AnimationExports/rabbit/hop_fall_singleframe.atom", force = True, options = mmOptions, typ = "atomExport", es = True)


Atom Import Example

# "targetTime" is the "Time range:" field. Counting 1,2,3 - there is no 0.
# "time" is the actual frame number start:end, and they can be the same number.
# no idea what "option=scaleInsert;" is doing.
# "match" is saying whether or not to use the search/replace options, if it were "string" then those would be used.
#  Might want to leave it as "string", but probably doesn't matter.
# "selected" is asking how does it know where to import animations, prolly best to leave it on selected.
# "mapFile" is not used - its asking where the mapping file is.  we could create a mapping file, but no need since transfering between complicit files.
mmOptions = """
;;
targetTime=2;
time=0:14;
option=scaleInsert;
match=hierarchy;;
selected=selectedOnly;
search=;
replace=;
prefix=;
suffix=;
mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;
"""
cmds.file(  "C:/Users/mmalley/Documents/Work/AnimationExports/rabbit/hop_fall_singleframe.atom", import = True, type = "atomImport", ra = True, namespace = "hop_fall_singleframe", options = mmOptions )
