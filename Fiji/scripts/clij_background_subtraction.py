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

imagefile = r"/datadisk1/tuxedo/Github/Tools_and_Scripts/Fiji/scripts/Osteosarcoma_01.ome.tiff"
# open image stack
imp, MetaInfo = ImportTools.openfile(imagefile)


# init GPU
clij = CLIJ.getInstance();

# push image to GPU
input = clij.push(imp);

# reserve memory for output, same size and type as input
output = clij.create(input);

# apply threshold method on GPU
clij.op().automaticThreshold(input, output, "Otsu");

# show result
clij.pull(output).show();
IJ.setMinAndMax(0, 1);
