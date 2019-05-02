# @File(label = "Image File", persist=True) FILENAME
# @Integer(label = "Select Channel", value=1, persist=True) CHANNEL2ANAlYSE
# @String(label = "Label Connectivity", choices={"6", "26"}, style="listBox", value="6", persist=True) LABEL_CONNECT
# @Integer(label = "MinVoxelSize", value=200, persist=True) MINVOXSIZE
# @Boolean(label = "Colorize Labels", value=True, persist=True) LABEL_COLORIZE
# @Boolean(label = "Save Particle Stack", value=True, persist=True) PASAVE
# @String(label = "Choose Save Format", choices={"ome.tiff", "png", "jpeg", "tiff"}, style="listBox", value="ome.tiff", persist=True) SAVEFORMAT
# @Boolean(label = "Save Result File as TXT", value=True, persist=True) RESULTSAVE
# @Boolean(label = "Run in headless mode", value=False, persist=False) HEADLESS
# @OUTPUT String FILENAME
# @OUTPUT Integer CHANNEL2ANAlYSE
# @OUTPUT String LABEL_CONNECT
# @OUTPUT Integer MINVOXSIZE
# @OUTPUT Boolean LABEL_COLORIZE
# @OUTPUT Boolean PASAVE
# @OUTPUT String SAVEFORMAT
# @OUTPUT Boolean RESULTSAVE
# @OUTPUT Boolean HEADLESS

#@UIService uiService
#@LogService log


"""
File: 3d_analytics_CH.py
Author: Sebastian Rhode
Date: 2019_03_14
Version: 0.5
"""

# append path
import os
import sys
scriptdir = os.path.join(os.getcwd(), 'Scripts')
sys.path.append(scriptdir)
log.info('Fiji Script Directory: ' + scriptdir)

from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import AnalyzeTools, RoiTools, MiscTools, ThresholdTools
from java.lang import Double, Integer
from ij import IJ, ImagePlus, ImageStack, Prefs
from ij.process import ImageProcessor, ImageConverter, LUT, ColorProcessor
from ij.plugin import Thresholder, Duplicator
from ij.plugin.filter import GaussianBlur, RankFilters, BackgroundSubtracter, Binary
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.plugin.frame import RoiManager
from ij.io import FileSaver
from ij.gui import Roi, Overlay
from ij.measure import ResultsTable
from ij.plugin import ChannelSplitter

import json
import os
import urllib
from java.awt import Color
from java.util import Random
from jarray import zeros
from org.scijava.vecmath import Point3f, Color3f

# MorphoLibJ imports
from inra.ijpb.binary import BinaryImages
from inra.ijpb.morphology import MinimaAndMaxima3D, Morphology, Strel3D
from inra.ijpb.watershed import Watershed
from inra.ijpb.label import LabelImages
from inra.ijpb.plugins import ParticleAnalysis3DPlugin, BoundingBox3DPlugin, ExtendBordersPlugin
from inra.ijpb.data.border import BorderManager3D, ReplicatedBorder3D
from inra.ijpb.util.ColorMaps import CommonLabelMaps
from inra.ijpb.util import CommonColors
from inra.ijpb.plugins import DistanceTransformWatershed3D

############################################################################


def run(imagefile):

    # Opening the image
    log.info('Opening Image: ' + imagefile)

    # open image file and get a specific series
    imp, MetaInfo = ImportTools.openfile(imagefile)

    log.info('File Extension   : ' + MetaInfo['Extension'])
    if 'ResolutionCount' in MetaInfo:
        log.info('Resolution Count : ' + str(MetaInfo['ResolutionCount']))
    if 'SeriesCount' in MetaInfo:
        log.info('SeriesCount      : ' + str(MetaInfo['SeriesCount']))
    if 'ChannelCount' in MetaInfo:
        log.info('Channel Count    : ' + str(MetaInfo['ChannelCount']))

    # do the processing
    log.info('Start Processing ...')

    # get the correct channel
    if MetaInfo['ChannelCount'] > 1:
        log.info('Extract Channel  : ' + str(MetaInfo['ChannelCount']))
        imps = ChannelSplitter.split(imp)
        imp = imps[CHINDEX-1]

    # 3D fill holes

    # 3d DistanceTransformWatershed3D on the stack
    #DistanceTransformWatershed3D.run(imp, "distances=[Borgefors (3,4,5)] output=[16 bits] normalize dynamic=2 connectivity=6")
    #IJ.run(imp, "Distance Transform Watershed 3D", "distances=[Borgefors (3,4,5)] output=[16 bits] normalize dynamic=2 connectivity=6")

    
    # extend borders
    log.info('Applying Border Extension ...')
    # create BorderManager and add Zeros in all dimensions
    bmType = BorderManager3D.Type.fromLabel("BLACK")
    bm = bmType.createBorderManager(imp.getStack())
    BorderExt = ExtendBordersPlugin()
    # extend border by always exb
    imp = BorderExt.process(imp.getStack(), EXB, EXB, EXB, EXB, EXB, EXB, bm)
    # convert back to ImgPlus
    pastack = ImagePlus('Particles', imp)

    # check for pixel in 3d by size
    log.info('Filtering VoxelSize - Minimum : ' + str(MINVOXSIZE))
    pastack = BinaryImages.volumeOpening(pastack.getStack(), MINVOXSIZE)
    imp = ImagePlus('Particles Filtered', pastack)
    pastack = BinaryImages.componentsLabeling(imp, LABEL_CONNECT, LABEL_BITDEPTH)

    # get the labels
    labels = LabelImages.findAllLabels(pastack)
    log.info('Labels Filtered : ' + str(len(labels)))

    # run 3D particle analysis
    log.info('3D Particle Analysis ...')
    PA3d = ParticleAnalysis3DPlugin()
    results = PA3d.process(pastack)

    # colorize the labels
    if LABEL_COLORIZE:
    
        log.info('Colorize Lables ...')
        #maxLabel = 255
        maxLabel = len(labels)
        bgColor = Color.BLACK
        shuffleLut = True
        lutName = CommonLabelMaps.GOLDEN_ANGLE.getLabel()

        # Create a new LUT from info in dialog
        lut = CommonLabelMaps.fromLabel(lutName).computeLut(maxLabel, shuffleLut)

        #  Create a new RGB image from index image and LUT options
        pastack_rgb = LabelImages.labelToRgb(pastack, lut, bgColor)

        # convert to rgb color
        IJ.run(pastack_rgb, "RGB Color", "slices")

    if LABEL_COLORIZE:
        return pastack_rgb, results, labels
    elif not LABEL_COLORIZE:
        return pastack, results, labels

################################################################################


if not HEADLESS:
    # clear the console automatically when not in headless mode
    uiService.getDefaultUI().getConsolePane().clear()

###### Define various parameters ######
MAXSIZE = Double.POSITIVE_INFINITY
CHINDEX = Integer.valueOf(CHANNEL2ANAlYSE)
SUFFIX_PA = '_PA'
SUFFIX_RT = '_RESULTS'
SAVEFORMAT_RT = 'txt'
IMAGESERIES = 0
LABEL_BITDEPTH = 16
LABEL_CONNECT = Integer.valueOf(LABEL_CONNECT)
EXB = 1

# get the FILENAME as string
imagefile = FILENAME.toString()

log.info('Starting pipeline ...')
log.info('Image Filename        : ' + imagefile)
log.info('Channel to Analyse    : ' + str(CHINDEX))
log.info('Label Connectivity    : ' + str(LABEL_CONNECT))
log.info('Label Output BitDepth : ' + str(LABEL_BITDEPTH))
log.info('Colorize Labels       : ' + str(LABEL_COLORIZE))
log.info('Minimun Voxel Size    : ' + str(MINVOXSIZE))
log.info('Headless Mode         : ' + str(HEADLESS))
log.info('------------  START IMAGE ANALYSIS ------------')


# run image analysis pipeline
objstack, results, labels = run(imagefile)


# show objects
log.info('Show Objects inside stack ...')
objstack.show()

log.info('Show ResultsTable ...')
results.show('3D Objects')

outputimagepath = os.path.splitext(imagefile)[0] + SUFFIX_PA + '.' + SAVEFORMAT

if PASAVE:
    log.info('Start Saving ...')
    savepath_objstack = ExportTools.savedata(objstack,
                                             outputimagepath,
                                             extension=SAVEFORMAT)

    log.info('Saved Processed Image to : ' + savepath_objstack)

# save the result file
if RESULTSAVE:
    # save the result table
    rtsavelocation = AnalyzeTools.create_resultfilename(imagefile,
                                                        suffix=SUFFIX_RT,
                                                        extension=SAVEFORMAT_RT)
    results.saveAs(rtsavelocation)
    log.info('Save Results to : ' + rtsavelocation)

# finish
log.info('Done.')
