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

method='Otsu'
background_threshold = 'dark'
imagefile = "/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/3d_nuclei_image_holes_T.ome.tiff"
corrf = 1.0

# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)

mt = 'stack'

"""
if mt == 'fiji':

	imp, thvalues = ThresholdTools.apply_threshold(imp, method=method,
                                                   background_threshold=background_threshold,
                                                   stackopt=True,
                                                   corrf=1.0)
                                                   
	print(thvalues)
"""

lowth_values = []

if mt == 'stack':

	"""
	ip = imp.getProcessor()
	#stackstats = StackStatistics(imp)
	#hist = stackstats.histogram
    # get the histogramm
	hist = ip.getHistogram()
	lowth = Auto_Threshold.Otsu(hist)
	print(lowth)
	ip.threshold(lowth)
	
	# get the stacks
	stack, nslices = ImageTools.getImageStack(imp)
	
	for index in range(1, nslices + 1):
	    ip = stack.getProcessor(index)
	    # apply correction factor
	    lowth_corr = int(round(lowth* corrf, 0))
	    ip.threshold(lowth_corr)
	"""
	
	# use whole histogramm for calculating the threshold
	IJ.setAutoThreshold(imp, "Otsu dark stack")
	ip = imp.getProcessor()
	hist = ip.getHistogram()
	#stackstats = StackStatistics(imp)
	#stack_histogram = stackstats.histogram
	#print(type(stack_histogram))
	#print(stackstats.histMax)
	#print(stackstats.histMin)
	#print(stackstats.lowerThreshold)
	#print(stackstats.upperThreshold)
	lowth = ip.getMinThreshold()
	lowth_values.append(lowth)
	log.info('Low Threshold : ' +str(lowth))




if mt == 'slice':
	
	# get the stacks
	stack, nslices = ImageTools.getImageStack(imp)
	lowth_corr_values = []
	
	for index in range(1, nslices + 1):
	    ip = stack.getProcessor(index)
	    # get the histogramm
	    hist = ip.getHistogram()
	    lowth = Auto_Threshold.Otsu(hist)
	    # apply correction factor
	    lowth_corr = int(round(lowth* corrf, 0))
	    #ip.threshold(lowth_corr)
	    ip.threshold(380)
	    log.info(lowth_corr)
	    lowth_corr_values.append(lowth_corr)

imp.show()

print(lowth_values)






