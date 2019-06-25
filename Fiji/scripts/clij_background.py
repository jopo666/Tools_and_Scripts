# CLIJ example ImageJ Ops jython: backgroundSubtraction.py
#
# This script shows how background subtraction can be done in the GPU.
#
# Author: Robert Haase, rhaase@mpi-cbg.de
# Author: Deborah Schmidt, frauzufall@mpi-cbg.de
# May 2019
# ---------------------------------------------

#@ IOService io
#@ UIService ui
#@ OpService ops

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


#imagefile = r"C:\Temp\input\01_3CH.ome.tiff"
imagefile = r'C:\Temp\input\3d_nuclei_big.tiff'


# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)
imp.show();


# init GPU
clij = CLIJ.getInstance()

# push image to GPU
input = clij.push(imp)

# reserve memory for output, same size and type as input
output = clij.create(input)

# apply threshold method on GPU
clij.op().automaticThreshold(input, output, "Otsu")

# show result
clij.pull(output).show()
IJ.setMinAndMax(0, 1)
"""

#########################

# open image stack
input, MetaInfo = ImportTools.openfile(imagefile)

#input = io.open(getResource("../samples/t1-head.tif"))
ui.show("input", input)
# push image to GPU
inputGPU = ops.run("CLIJ_push", input)
# Blur in GPU
background = ops.run("CLIJ_blur", inputGPU, 10, 10, 1)
background_subtracted = ops.run("CLIJ_addImagesWeighted", inputGPU, background, 1, -1)
#maximum_projected = ops.run("CLIJ_maximumZProjection", background_subtracted)

# show result
#result = ops.run("CLIJ_pull", maximum_projected)
result = ops.run("CLIJ_pull", background_subtracted)
ui.show("background subtraction", result)

#cleanup
ops.run("CLIJ_close", inputGPU)
ops.run("CLIJ_close", background)
ops.run("CLIJ_close", background_subtracted)
#ops.run("CLIJ_close", maximum_projected)
ops.run("CLIJ_close")

"""