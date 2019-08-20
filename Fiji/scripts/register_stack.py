# @ File(label = "Image File", style="file", persist=True) filename
# @ Integer(label = "Z-Plane used as Reference", value=1) refplane
# @ Boolean(label = "Remove folder with single source images", value=False, persist=True) remove_source
# @ Boolean(label = "Remove folder with single target images", value=False, persist=True) remove_target
# @ Boolean(label = "Remove folder with transformations", value=False, persist=True) remove_trans


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

# imp.show()

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


featuremodelindex = {0: "Translation",
                     1: "Rigid",
                     2: "Similarity",
                     3: "Affine"}

regmodelindex = {0: "Translation",
                 1: "Rigid",
                 2: "Similarity",
                 3: "Affine",
                 4: "Elastic",
                 5: "Moving Least Squares"}

# shrinkage option (false)
use_shrinking_constraint = False

p = Register_Virtual_Stack_MT.Param()


# inlier ratio
p.minInlierRatio = 0.05
# implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE
p.featuresModelIndex = 3
# maximal allowed alignment error in pixels
p.maxEpsilon = 10
# Implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE, 4=ELASTIC, 5=MOVING_LEAST_SQUARES
p.registrationModelIndex = 3
# Closest/next neighbor distance ratio
p.rod = 0.9
# SIFT - maximum image size
p.sift.maxOctaveSize = 1024

log.info("bUnwarpJ parameters for consistent elastic registration")
log.info(p.elastic_param)
log.info("-------------------------------------------------------")
log.info("FeatureModelIndex           : " + str(p.featuresModelIndex) + " = " + str(featuremodelindex[p.featuresModelIndex]))
log.info("RegistrationModelIndex      : " + str(p.registrationModelIndex) + " = " + str(regmodelindex[p.registrationModelIndex]))
log.info("Max. Aligmnet Error [pixel] : " + str(p.maxEpsilon))
log.info("Min. Inlier Ratio           : " + str(p.minInlierRatio))
log.info("Next Neighbour Distance Ratio : " + str(p.rod))

# SIFT Parameters
print p.sift.fdBins
print p.sift.fdSize
print p.sift.initialSigma
print p.sift.minOctaveSize
print p.sift.maxOctaveSize
print p.sift.steps

print "elastic_param"
print p.elastic_param


# get list of all single plane files and pick one as reference
sourcefiles = MiscTools.getfiles(sourcedir, filter='.tiff')
ref = os.path.basename(sourcefiles[refplane])

# pepare strings to work with the plugin ...
source = sourcedir + r'/'
target = targetdir + r'/'
trans = transformdir + r'/'

# run the actual registration
log.info('Registering z-Planes ...')
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

# remove directories with single images or files
if remove_source:
    shutil.rmtree(sourcedir, ignore_errors=True)
if remove_target:
    shutil.rmtree(targetdir, ignore_errors=True)
if remove_trans:
    shutil.rmtree(transformdir, ignore_errors=True)

# finish
log.info('Done.')
