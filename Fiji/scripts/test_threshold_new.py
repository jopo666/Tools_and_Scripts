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

stackopt=True
method='Li'
background_threshold = 'dark'
imagefile = "/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/3d_nuclei_image_holes_T.ome.tiff"
corrf = 1.0

if stackopt:
	thcmd = method + ' ' + background_threshold + ' stack'
if not stackopt:
	thcmd = method + ' ' + background_threshold + ' stack'

# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)


def threshold_stack(imp, thvalue):
	# get the stacks
	stack, nslices = ImageTools.getImageStack(imp)
	
	for index in range(1, nslices + 1):
	    ip = stack.getProcessor(index)
	    # get the histogramm
	    hist = ip.getHistogram()
	    lowth = Auto_Threshold.Otsu(hist)
	    ip.threshold(thvalue)

	return imp


if mt == 'stack':

	IJ.setAutoThreshold(imp, "Otsu dark stack")
	ip = imp.getProcessor()
	hist = ip.getHistogram()
	lowth = ip.getMinThreshold()
	lowth_corr = int(round(lowth* corrf, 0))
	print('Low Threshold      : ' +str(lowth))
	print('Low Threshold Corr : ' +str(lowth_corr))

	# process stack with corrected threshold value
	if corrf <> 1.0:
		print('Using corrected threshold value.')
		imp = threshold_stack(imp, lowth_corr)


if mt == 'slice':
	
	# get the stacks
	stack, nslices = ImageTools.getImageStack(imp)
	print('Threshold slice-by-slice')
	
	for index in range(1, nslices + 1):
		ip = stack.getProcessor(index)
		# get the histogramm
		hist = ip.getHistogram()
		# get the threshold value
		lowth_corr = ThresholdTools.apply_autothreshold(hist, corrf=corrf, method=method)
		ip.threshold(lowth_corr)

imp.show()







