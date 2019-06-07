#@ Integer(label="Gradient radius",description="Radius of the morphological gradient",value=2) radius
#@ Integer(label="Tolerance",description="Local extrema dynamic",value=3) tolerance
#@ String(label="Connectivity",description="Local connectivity", choices={"6","26"}) strConn
#@ Boolean(label="Calculate dams",description="Flag to use dams in watershed",value=true) dams
#@OUTPUT ImagePlus resultImage

#@UIService uiService
#@LogService log
# clear the console automatically when not in headless mode
uiService.getDefaultUI().getConsolePane().clear()

# append path
import os
import sys
from sys import path
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/scripts')

from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import RoiTools, MiscTools, ThresholdTools, AnalyzeTools
from java.lang import Double, Integer
from ij import IJ, ImagePlus, ImageStack, Prefs
from ij.process import ImageProcessor, ImageConverter
from ij.plugin import Thresholder, Duplicator
from ij.process import StackStatistics
from ij.process import AutoThresholder
from ij.plugin.filter import GaussianBlur, RankFilters, BackgroundSubtracter, Binary
from fiji.threshold import Auto_Threshold
# MorphoLibJ imports
from inra.ijpb.binary import BinaryImages
from inra.ijpb.morphology import MinimaAndMaxima3D
from inra.ijpb.morphology import Morphology
from inra.ijpb.morphology import Strel3D
from inra.ijpb.watershed import Watershed
from inra.ijpb.data.image import Images3D


############################################################################

stackopt=True
method='Otsu'
background_threshold = 'dark'
#imagefile = r"/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/3d_nuclei_image_holes_T.ome.tiff"
#imagefile = r"/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/3d_nuclei_image_holes.ome.tiff"
imagefile = r"/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/Osteosarcoma_01.ome.tiff"
imagefile = r'"C:\Temp\input\Osteosarcoma_01.ome.tiff"
corrf = 1.0

if stackopt:
	thcmd = method + ' ' + background_threshold + ' stack'
if not stackopt:
	thcmd = method + ' ' + background_threshold

# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)

imp = MiscTools.splitchannel(imp, 3)

imp = ThresholdTools.apply_threshold(imp,
									 method=method,
									 background_threshold='dark',
									 stackopt=stackopt,
									 corrf=corrf)
											

imp.show()







