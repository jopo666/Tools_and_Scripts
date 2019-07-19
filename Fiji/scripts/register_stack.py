#@ File(label = "Image File", style="file", persist=True) filename
#@ Integer(label = "Z-Plane used as Reference", value=1) refplane
 
# @UIService uiService
# @LogService log

import sys
import os
import json
import time
import shutil

from java.lang.System import getProperty
sys.path.append(getProperty('fiji.dir') + '/scripts')

from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import AnalyzeTools, RoiTools, MiscTools, ThresholdTools
from fijipytools import WaterShedTools, BinaryTools
from fijipytools import JSONTools
from ij.measure import ResultsTable
from ij.gui import Roi, Overlay
from ij.io import FileSaver
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.plugin.filter import GaussianBlur, RankFilters
from ij.plugin.filter import BackgroundSubtracter, Binary
from ij.plugin import Thresholder, Duplicator
from ij.process import ImageProcessor, ImageConverter, LUT, ColorProcessor
from ij import IJ, ImagePlus, ImageStack, Prefs
from java.lang import Double, Integer
from register_virtual_stack import Register_Virtual_Stack_MT


############################################################################

# clear the console automatically when not in headless mode
uiService.getDefaultUI().getConsolePane().clear()


##############  PIPELINE START ##################

# open the image
imagefile = filename.toString()
log.info('Opening CZI stack: ' + imagefile)

# stitch togehter image tiles
stitchtiles = True
# when set to True the number of pyramid levels can be read
setflatres = True
# select the desired pyramid level - level=0 for full resolution
readpylevel = 0
setconcat = True
openallseries = True
showomexml = False
attach = False
autoscale = True
verbose = False
showorig = False

# read the image
imp, MetaInfo = ImportTools.openfile(imagefile,
                                     stitchtiles=stitchtiles,
                                     setflatres=setflatres,
                                     readpylevel=readpylevel,
                                     setconcat=setconcat,
                                     openallseries=openallseries,
                                     showomexml=showomexml,
                                     attach=attach,
                                     autoscale=autoscale)

#imp.show()

# get the base directory
basedir = os.path.dirname(imagefile)
# get the filename without the extension
filename_woext = os.path.splitext(os.path.basename(imagefile))[0]
# create new directories
sourcedir = os.path.join(basedir, 'source')
targetdir = os.path.join(basedir, 'target')
transformdir = os.path.join(basedir, 'transform')

log.info('Base Directory           : ' + basedir)
log.info('Filename wo Extension    : ' + filename_woext)
log.info('Source Directory         : ' + sourcedir)
log.info('Target Directory         : ' + targetdir)
log.info('Transformation Directory : ' + transformdir)

state_sourcedir = MiscTools.createdir(sourcedir)
state_tragetdir = MiscTools.createdir(targetdir)
state_transformdir = MiscTools.createdir(transformdir)

#### Register Slices ####

# save all planes as single images
ExportTools.save_singleplanes(imp, sourcedir, MetaInfo,
                              mode='Z',
                              format='tiff')

# shrinkage option (false)
use_shrinking_constraint = False
 
p = Register_Virtual_Stack_MT.Param()
# maximum image size
p.sift.maxOctaveSize = 1024
# inlier ratio
p.minInlierRatio = 0.05
# implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE
p.featuresModelIndex = 3
# maximal allowed alignment error in pixels
p.maxEpsilon = 10

# get list of all single plane files and pick one as reference
sourcefiles = MiscTools.getfiles(sourcedir, filter='.tiff')
ref = os.path.basename(sourcefiles[refplane])

# pepare strings to work with the plugin ...
source = sourcedir + r'/'
target = targetdir + r'/'
trans = transformdir + r'/'

# run the actual registration
log.info('Registering z-Planes ...) 
Register_Virtual_Stack_MT.exec(source, target, trans, ref, p, use_shrinking_constraint)

# get the virtual stack as an ImagePlus object
imp = IJ.getImage()

# define the output path and save the virtual stack as OME-TIFF
saveformat = 'ome.tiff'
outputimagepath = os.path.join(basedir, filename_woext + '_reg.' + saveformat)
log.info('Output Stack             : ' + outputimagepath)

# save the registered stack
savepath_pastack = ExportTools.savedata(imp,
                                        outputimagepath,
                                        extension=saveformat,
                                        replace=True)

# finish
log.info('Done.')
