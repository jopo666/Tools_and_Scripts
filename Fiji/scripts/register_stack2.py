#@ File(label = "Image File", style="file", persist=True) filename
#@ Integer(label = "Z-Plane used as Reference", value=1) refplane
#@ String(label = "Feature Model", choices={"Translation", "Rigid", "Similarity", "Affine"}, style="listBox", value="Affine", persist=True) fmodelstring
#@ String(label = "Registration Model", choices={"Translation", "Rigid", "Similarity", "Affine", "Elastic", "Moving Least Squeares"}, style="listBox", value="Affine", persist=True) rmodelstring
#@ Boolean(label = "Remove folder with single source images", value=False, persist=True) remove_source
#@ Boolean(label = "Remove folder with single target images", value=False, persist=True) remove_target
#@ Boolean(label = "Remove folder with transformations", value=False, persist=True) remove_trans


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
verbose = True
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

#for k, v in MetaInfo.items():
#    log.info(str(k) + ' : ' + str(v))

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


featuremodelindex = ["Translation",
                     "Rigid",
                     "Similarity",
                     "Affine"]

regmodelindex = ["Translation",
                 "Rigid",
                 "Similarity",
                 "Affine",
                 "Elastic",
                 "Moving Least Squares"]


fmi = featuremodelindex.index(fmodelstring)
rmi = regmodelindex.index(rmodelstring)

# shrinkage option (false)
use_shrinking_constraint = False
 
p = Register_Virtual_Stack_MT.Param()

# inlier ratio
p.minInlierRatio = 0.05
# implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE
#p.featuresModelIndex = 3
p.featuresModelIndex = fmi
# maximal allowed alignment error in pixels
p.maxEpsilon = 10
# Implemented transformation models for choice 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE, 4=ELASTIC, 5=MOVING_LEAST_SQUARES
#p.registrationModelIndex = 3
p.registrationModelIndex = rmi
# Closest/next neighbor distance ratio
p.rod = 0.9

#############    bunwarpJ Parameters   #########

# consistency weight
p.elastic_param.consistencyWeight = 10.0
# curl weight
p.elastic_param.curlWeight = 0.0
# divergence weight
p.elastic_param.divWeight = 0.1
# image similarity weight
p.elastic_param.imageWeight = 1.0
# image subsampling factor (from 0 to 7, representing 2**0=1 to 2**7 = 128)
p.elastic_param.img_subsamp_fact = 0
# landmark weight
p.elastic_param.landmarkWeight = 0.0
# minimum scale deformation (0 - Very Coarse, 1 - Coarse, 2 - Fine, 3 - Very Fine)
p.elastic_param.min_scale_deformation = 1
# maximum scale deformation (0 - Very Coarse, 1 - Coarse, 2 - Fine, 3 - Very Fine, 4 - Super Fine)
p.elastic_param.max_scale_deformation = 3
# mode accuracy mode (0 - Fast, 1 - Accurate, 2 - Mono)
p.elastic_param.mode = 2
# stopping threshold
p.elastic_param.stopThreshold = 0.01


#############   SIFT Parameters ################
# SIFT - minimum and maximum image size
p.sift.minOctaveSize = 64
p.sift.maxOctaveSize = 1024
# SIFT - steps per scale octave
p.sift.steps = 3
# SIFT - Feature descriptor orientation bins How many bins per local histogram
p.sift.fdBins = 8
# SIFT - Feature descriptor size How many samples per row and column
p.sift.fdSize = 4

# log the parameters

# bUnwarpJ parameters
log.info("-----------   bUnwarpJ Parameters   -------------------")
log.info("bUnwarpJ parameters for consistent elastic registration")
log.info(p.elastic_param)

# general registration parameters
log.info("-----------   Registration Parameters   ---------------")
log.info("FeatureModelIndex             : " + str(p.featuresModelIndex) + " = " + str(featuremodelindex[p.featuresModelIndex]))
log.info("RegistrationModelIndex        : " + str(p.registrationModelIndex) + " = " + str(regmodelindex[p.registrationModelIndex]))
log.info("Max. Alignmnet Error [pixel]  : " + str(p.maxEpsilon))
log.info("Min. Inlier Ratio             : " + str(round(p.minInlierRatio, 3)))
log.info("Next Neighbour Distance Ratio : " + str(round(p.rod, 3)))

# SIFT Parameters
log.info("-----------   SIFT Parameters   -----------------------")
# Feature descriptor orientation bins How many bins per local histogram
log.info("Feature Descriptor bins per local histogram   : " + str(p.sift.fdBins))
# Feature descriptor size How many samples per row and column
log.info("Feature Descriptor samples per row and column : " + str(p.sift.fdSize))
# Initial sigma of each Scale Octave
log.info("Initial sigma of each Scale Octave            : " + str(round(p.sift.initialSigma, 3)))
# Size limits for scale octaves in px: minOctaveSize < octave < maxOctaveSize
log.info("Minimum Size for Scale Octaves [pixel]        : " + str(p.sift.minOctaveSize))
log.info("Maximum Size for Scale Octaves [pixel]        : " + str(p.sift.maxOctaveSize))
log.info("Steps per Scale Octave                        : " + str(p.sift.steps))
log.info("-------------------------------------------------------")

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
vregstack = IJ.getImage()
vregstack.close()

# define the output path and save the virtual stack as OME-TIFF
saveformat = 'ome.tiff'
outputimagepath = os.path.join(basedir, filename_woext + '_reg.' + saveformat)
log.info('Output Stack             : ' + outputimagepath)

namepattern = os.path.splitext(os.path.basename(imagefile))[0]

stack = MiscTools.import_sequence(targetdir,
                                  number=MetaInfo['SizeZ'],
                                  start=1,
                                  increment=1,
                                  filepattern=namepattern,
                                  sort=True,
                                  use_virtualstack=False)

# set properties for new stack
stack = MiscTools.setproperties(stack,
                                scaleX=MetaInfo['ScaleX'],
                                scaleY=MetaInfo['ScaleY'],
                                scaleZ=MetaInfo['ScaleZ'],
                                unit="micron",
                                sizeC=MetaInfo['SizeC'],
                                sizeZ=MetaInfo['SizeZ'],
                                sizeT=MetaInfo['SizeT'])

# save the registered stack
savepath_stack = ExportTools.savedata(stack,
                                      outputimagepath,
                                      extension=saveformat,
                                      replace=True)
                                      
stack.close()

log.info('SavePath Registered Stack : ' + savepath_stack)

# read the registered stack
regstack, MetaInfo = ImportTools.openfile(savepath_stack)

# output of image metadata in log window
if verbose:
    for k, v in MetaInfo.items():
        log.info(str(k) + ' : ' + str(v))

regstack.show()

# remove directories with single images or files
if remove_source:
    shutil.rmtree(sourcedir, ignore_errors=True)
if remove_target:
    shutil.rmtree(targetdir, ignore_errors=True)
if remove_trans:
    shutil.rmtree(transformdir, ignore_errors=True)

# finish
log.info('Done.')
