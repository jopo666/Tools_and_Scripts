# @File(label = "Image File", persist=True) JSONPARAMFILE
# @OUTPUT String JSONPARAMFILE

#@UIService uiService
#@LogService log

"""
File: GuidedAcq_fromZEN.py
Author: Sebastian Rhode
Date: 2018_10_11
Version: 0.23
"""

import json
# get the JSONPARAMFILE as string
jsonfile = JSONPARAMFILE.toString()
INPUT_JSON = json.loads(open(jsonfile).read())


# append path
import os
import sys
scriptdir = os.path.join(os.path.dirname(INPUT_JSON['IMAGEJ']), 'scripts')
sys.path.append(scriptdir)
log.info('Fiji Script Directory : ' + scriptdir)

from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import AnalyzeTools, RoiTools, MiscTools, ThresholdTools
from java.lang import Double, System
from ij import IJ, ImagePlus, ImageStack, Prefs
from ij.process import ImageProcessor, ImageConverter
from ij.plugin import Thresholder, Duplicator
from ij.plugin.filter import GaussianBlur, RankFilters
from ij.plugin.filter import BackgroundSubtracter, Binary
from ij.plugin.filter import ParticleAnalyzer as PA
from ij.plugin.frame import RoiManager
from ij.io import FileSaver
from ij.gui import Roi
from ij.gui import Overlay
from ij.measure import ResultsTable
import json
import os
import urllib


def writejsonfile(data, jsonfilename='MetaData.json', savepath='C:\Temp'):
    # write data into a JSON file
    jsonfile = os.path.join(savepath, jsonfilename)

    # Writing JSON data with correct indentation
    with open(jsonfile, 'w') as f:
        json.dump(data, f, indent=4)

    return jsonfile


############################################################################

def run(imagefile):

    # open image file and get a specific series
    #imps, MetaInfo = ImportTools.openfile(imagefile)
    imp, MetaInfo = ImportTools.openfile(imagefile,
                                         stitchtiles=True,
                                         setflatres=False,
                                         readpylevel=PYLEVEL,
                                         setconcat=True,
                                         openallseries=True,
                                         showomexml=False,
                                         attach=False,
                                         autoscale=True)

    # Opening the image
    log.info('Opening Image: ' + imagefile)
    log.info('File Extension   : ' + MetaInfo['Extension'])
    if 'ResolutionCount' in MetaInfo:
        log.info('Resolution Count : ' + str(MetaInfo['ResolutionCount']))
    if 'SeriesCount' in MetaInfo:
        log.info('SeriesCount      : ' + str(MetaInfo['SeriesCount']))

    # get sprecifies image series
    #log.info('Getting Image Series : ' + str(IMAGESERIES))
    #imp = ImageTools.getseries(imps, series=IMAGESERIES)

    # do the processing
    log.info('Start Processing ...')

    if BINFACTOR == 1:
        imp_p = imp
    elif BINFACTOR >= 2:
        # apply binning to reduce the image size
        log.info('Apply Binning: ' + str(BINFACTOR) + ' Method : ' + BINMETHOD)
        imp_p = MiscTools.apply_binning(imp, binning=BINFACTOR, method=BINMETHOD)

    # apply filter
    log.info('Apply Filter: ' + RANKFILTER)
    imp_p = FilterTools.apply_filter(imp_p, radius=RADIUS)

    # convert to 8-bit for the thresholding
    log.info('Convert to 8-bit ...')
    IJ.run(imp_p, "8-bit", "")

    # apply threshold
    log.info('Apply Threshold: ' + THRESHOLD)
    imp_p = ThresholdTools.apply_threshold(imp_p, method=THRESHOLD,
                                           background_threshold=THRESHOLD_BGRD,
                                           corrf=CORRFACTOR)

    pastack, results = AnalyzeTools.analyzeParticles(imp_p, MINSIZE, MAXSIZE, MINCIRC, MAXCIRC,
                                                     filename=imagefile,
                                                     addROIManager=ROIS)

    # apply suitable LUT to visualize detected particles
    pastack = ImagePlus('Particles', pastack)
    IJ.run(pastack, 'glasbey_inverted', '')
    IJ.run(pastack, 'Enhance Contrast', 'saturated=0.35')

    return pastack, results


################################################################################

# Define various parameters ######
MAXSIZE = Double.POSITIVE_INFINITY
SUFFIX_PA = '_PA'
SUFFIX_RT = '_RESULTS'
SAVEFORMAT_RT = 'txt'
IMAGESERIES = 0

# for rolling ball
CREATEBACKGROUND = False
LIGHTBACKGROUND = False
USEPARABOLOID = False
DOPRESMOOTH = True
CORRECTCORNERS = False

# for binning
BINMETHOD = 'Sum'

# transfer values from input JSON to distinct variables
imagefile = INPUT_JSON['IMAGE']
BINFACTOR = int(INPUT_JSON['BIN'])
RANKFILTER = INPUT_JSON['RANKFILTER']
RADIUS = int(INPUT_JSON['RADIUS'])
THRESHOLD = INPUT_JSON['THRESHOLD']
THRESHOLD_BGRD = INPUT_JSON['THRESHOLD_BGRD']
MINSIZE = int(INPUT_JSON['MINSIZE'])
MINCIRC = float(INPUT_JSON['MINCIRC'])
MAXCIRC = float(INPUT_JSON['MAXCIRC'])
THRESHOLD = INPUT_JSON['THRESHOLD']
CORRFACTOR = float(INPUT_JSON['CORRFACTOR'])
SAVEFORMAT = INPUT_JSON['SAVEFORMAT']
SCRIPT = INPUT_JSON['IMAGEJSCRIPT']
#PYLEVEL = INPUT_JSON['PYLEVEL']
PYLEVEL = 0


# other required parameters
HEADLESS = True
ROIS = False
PASAVE = True
RESULTSAVE = True
BACKGROUNDTHRESH = 'black'
EXIT_AT_END = True

if not HEADLESS:
    # clear the console automatically when not in headless mode
    uiService.getDefaultUI().getConsolePane().clear()

# output for logging
log.info('Start Fiji Image Analysis ...')
log.info('Fiji Python Script            : ' + SCRIPT)
log.info('Filename                      : ' + imagefile)
log.info('BinFactor                     : ' + str(BINFACTOR))
log.info('RankFilter                    : ' + RANKFILTER)
log.info('Filter Radius                 : ' + str(RADIUS))
log.info('Threshold Method              : ' + THRESHOLD)
log.info('Threshold Background          : ' + THRESHOLD_BGRD)
log.info('Min. Partice Size [pixel]     : ' + str(MINSIZE))
log.info('Min. Circularity              : ' + str(MINCIRC))
log.info('Max. Circularity              : ' + str(MAXCIRC))
log.info('Add Particles to ROI-Manger   : ' + str(ROIS))
log.info('Save Particles as Image       : ' + str(PASAVE))
log.info('Save Format                   : ' + SAVEFORMAT)
log.info('Save Results                  : ' + str(RESULTSAVE))
log.info('Headless Mode                 : ' + str(HEADLESS))
log.info('------------  START IMAGE ANALYSIS ------------')

# run image analysis pipeline
pastack, results = run(imagefile)

outputimagepath = os.path.splitext(imagefile)[0] + SUFFIX_PA + '.' + SAVEFORMAT

# save the particle stack
if PASAVE:

    savepath_pastack = ExportTools.savedata(pastack,
                                            outputimagepath,
                                            extension=SAVEFORMAT)

    log.info('Saving Processed Image to : ' + savepath_pastack)

# save the result file
if RESULTSAVE:

    rtsavelocation = AnalyzeTools.create_resultfilename(imagefile,
                                                        suffix=SUFFIX_RT,
                                                        extension=SAVEFORMAT_RT)

    results.saveAs(rtsavelocation)
    log.info('Save Results to: ' + rtsavelocation)


# update MetaData.json and write file
INPUT_JSON['RESULTIMAGE'] = savepath_pastack
INPUT_JSON['RESULTTABLE'] = rtsavelocation
outjsonfilepath = writejsonfile(INPUT_JSON,
                                jsonfilename=os.path.basename(jsonfile),
                                savepath=os.path.dirname(imagefile))

log.info('Updated Metadata and writing JSON to: ' + outjsonfilepath)

# finish
log.info('Done.')

# finish and exit the script
# if EXIT_AT_END:
#    os._exit(42)
