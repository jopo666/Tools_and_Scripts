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


############################################################################

stackopt=False
method='Otsu'
background_threshold = 'dark'
imagefile = "c:\Users\m1srh\Downloads\Osteosarcoma_01.ome.tiff"
corrf = 1.0

if stackopt:
	thcmd = method + ' ' + background_threshold + ' stack'
if not stackopt:
	thcmd = method + ' ' + background_threshold

# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)


imp = ThresholdTools.apply_threshold(imp,
									 method=method,
									 background_threshold='dark',
									 stackopt=stackopt,
									 corrf=corrf)
											

imp.show()







