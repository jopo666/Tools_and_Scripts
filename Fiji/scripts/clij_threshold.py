# @File(label = "Image File", persist=True) FILENAME
# @String(label = "Method", choices={"Otsu", "Triangle", "IJDefault", "Huang", "MaxEntropy", "Mean", "Shanbhag", "Yen", "Li"}, style="listBox", value="Otsu", persist=True) threshold_method
# @OUTPUT String FILENAME
# @OUTPUT String threshold_method

# @UIService uiService
# @LogService log
#@ IOService io
#@ UIService ui
#@ OpService ops

# clear the console automatically when not in headless mode
uiService.getDefaultUI().getConsolePane().clear()

import time
import os
import sys
from sys import path
from java.lang.System import getProperty
path.append(getProperty('fiji.dir') + '/scripts')

from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import RoiTools, MiscTools, ThresholdTools, AnalyzeTools

from ij import IJ
from net.haesleinhuepf.clij import CLIJ

import inspect
def getResource(file):
    return os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + "/" + file

#imagefile = r"/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/Osteosarcoma_01.ome.tiff"
#imagefile = r"c:\Users\m1srh\Documents\Apeer_Modules\clij_test_0cb844d2-410a-4d6f-a27c-371fc1954661\input\test.ome.tiff"

# get the FILENAME as string
imagefile = FILENAME.toString()

# summarize parameters
log.info('Starting ...')
log.info('Filename               : ' + imagefile)
log.info('-----------------------------------------------')
log.info('Threshold Method       : ' + threshold_method)
log.info('------------  START IMAGE ANALYSIS ------------')


# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)

start = time.clock()

# init GPU
clij = CLIJ.getInstance();

# push image to GPU
input = clij.push(imp);

# reserve memory for output, same size and type as input
output = clij.create(input);
	
# apply threshold method on GPU
if threshold_method == 'Otsu':
	clij.op().automaticThreshold(input, output, threshold_method);

	# show result
	clij.pull(output).show();
	IJ.setMinAndMax(0, 1);

end = time.clock()

log.info('Duration of Processing CLIJ: ' + str(end - start))

threshold_stackoption = True
threshold_background = 'dark'
threshold_corr = 1.0

start2 = time.clock()

log.info('Apply Threshold ...')
th_image = ThresholdTools.apply_threshold(imp,
                                          method=threshold_method,
                                          background_threshold="dark",
                                          stackopt=threshold_stackoption,
                                          corrf=threshold_corr)

end2 = time.clock()

log.info('Duration of Processing Fiji: ' + str(end2 - start2))

# finish
log.info('Done.')

th_image.show()