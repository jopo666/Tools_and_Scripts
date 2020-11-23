# @File(label = "Image File", persist=True) FILENAME
# @OUTPUT String FILENAME

# @UIService uiService
# @LogService log

# required imports
import os
import json
import time
import sys
import jarray
from java.lang.System import getProperty
sys.path.append(getProperty('fiji.dir') + '/scripts')

from java.lang import Double, Integer
from ij import IJ, ImagePlus, ImageStack, Prefs
from ij.process import ImageProcessor, LUT
from ij.plugin import ChannelSplitter
from fijipytools import ExportTools, FilterTools, ImageTools, ImportTools
from fijipytools import AnalyzeTools, RoiTools, MiscTools, ThresholdTools
from org.scijava.log import LogLevel
from ij.plugin import Duplicator


def calc_normvar(ip, mean, width, height):

    normvar = 0
    b = 0
    for x in range(0, width):
        for y in range(0, height):

            p = ip.getPixel(x, y)
            t = (p - mean) * (p - mean)
            b = b + t

    normvar = b / (height * width * mean)

    return normvar


def calc_focus(imp, name):
    stack = imp.getStack()  # get the stack within the ImagePlus
    nslices = stack.getSize()  # get the number of slices
    fv = []
    fv_max = 0
    fv_max_index = 0

    for index in range(1, nslices + 1):
        # get the image processor
        ip = stack.getProcessor(index)
        width = ip.getWidth()
        height = ip.getHeight()
        mean_current = ip.getStatistics().mean
        normvar_curr = calc_normvar(ip, mean_current, width, height)
        log.log(LogLevel.INFO, 'Slice : ' + str(index) + ' FV : ' + str(normvar_curr))
        fv.append(normvar_curr)
        if normvar_curr > fv_max:
            fv_max = normvar_curr
            fv_max_index = index
            new_imp = ImagePlus(name + '_Z=' + str(index), ip)

    return new_imp, fv, fv_max, fv_max_index


def getstackfrom5d(imp, metadata,
                   firstC=1,
                   lastC=1,
                   firstZ=1,
                   lastZ=1,
                   firstT=1,
                   lastT=1):

    substack = Duplicator().run(imp, firstC, lastC, firstZ, lastZ, firstT, lastT)

    return substack

############################################################################


# clear the console automatically when not in headless mode
uiService.getDefaultUI().getConsolePane().clear()


def run(imagefile, verbose=False):

    # open image file and get a specific series
    log.log(LogLevel.INFO, 'Opening Image: ' + imagefile)
    imp, MetaInfo = ImportTools.openfile(imagefile)

    # output of image metadata in log window
    if verbose:
        for k, v in MetaInfo.items():
            log.log(LogLevel.INFO, str(k) + ' : ' + str(v))

    log.log(LogLevel.INFO, 'File Extension    : ' + MetaInfo['Extension'])
    if 'ResolutionCount' in MetaInfo:
        log.log(LogLevel.INFO, 'Resolution Count  : ' + str(MetaInfo['ResolutionCount']))
    if 'SeriesCount' in MetaInfo:
        log.log(LogLevel.INFO, 'SeriesCount       : ' + str(MetaInfo['SeriesCount']))
    if 'SizeC' in MetaInfo:
        log.log(LogLevel.INFO, 'Channel Count     : ' + str(MetaInfo['SizeC']))

    # do the processing
    log.log(LogLevel.INFO, 'Start Processing ...')

    # create empty image list
    imglist_t_c = []
    imglist_t = []
    numch = imp.getNChannels()

    # do the processing
    for t in range(MetaInfo['SizeT']):

        # get the timepoint
        imp_t = getstackfrom5d(imp, MetaInfo,
                               firstC=1,
                               lastC=MetaInfo['SizeC'],
                               firstZ=1,
                               lastZ=MetaInfo['SizeZ'],
                               firstT=t + 1,
                               lastT=t + 1)

        # calc the focus values for the different channels
        for ch in range(numch):

            # get a stack for a channel
            imp_t_c = getstackfrom5d(imp_t, MetaInfo,
                                     firstC=ch + 1,
                                     lastC=ch + 1,
                                     firstZ=1,
                                     lastZ=MetaInfo['SizeZ'],
                                     firstT=1,
                                     lastT=1)

            # create a name for the plane
            #name = os.path.basename(imagefile) + 'T=' + str(t+1) + '_CH=' + str(ch+1)
            name = 'T=' + str(t + 1) + '_CH=' + str(ch + 1)

            # get the plane with the bst focus to the current timepoint and current channel
            sp_c, fv, fv_max, fv_max_index = calc_focus(imp_t_c, name)
            log.log(LogLevel.INFO, 'Processing TimePoint : ' + str(t + 1))
            log.log(LogLevel.INFO, 'Processing Channel   : ' + str(ch + 1))
            log.log(LogLevel.INFO, 'Max. Value           : ' + str(fv_max))
            log.log(LogLevel.INFO, 'Max. Value Slice     : ' + str(fv_max_index))

            # set correct image properties
            sp_c = MiscTools.setproperties(sp_c,
                                           scaleX=MetaInfo['ScaleX'],
                                           scaleY=MetaInfo['ScaleY'],
                                           scaleZ=MetaInfo['ScaleZ'],
                                           unit='micron',
                                           sizeC=1,
                                           sizeZ=1,
                                           sizeT=1)

            imglist_t_c.append(sp_c)

        print 'List CH Stacks :', len(imglist_t_c)

        for i in range(len(imglist_t_c)):
            print str(i) + ' : ', type(imglist_t_c[i])

        # in case of more than one channel use an jarray
        if numch > 1:

            # create an array
            imgarray_c = jarray.array(imglist_t_c, ImagePlus)
            # create an ImageStack from the array
            print 'Type imgarray_c : ', type(imgarray_c)

            for i in range(numch):
                print type(imgarray_c[i])

            imgstack_c = ImageStack.create(imgarray_c)

            # create an ImagePlus object from the jarray
            new_name = os.path.splitext(os.path.basename(imagefile))[0]
            imp_sp_c = ImagePlus(new_name + '_SHARPEST_C', imgstack_c)

        # in case of exactly one channel directly use the ImgPlus
        if numch == 1:
            imp_sp_c = imglist_t_c[0]

        # set correct image properties for the final image
        imp_sp_c = MiscTools.setproperties(imp_sp_c,
                                           scaleX=MetaInfo['ScaleX'],
                                           scaleY=MetaInfo['ScaleY'],
                                           scaleZ=MetaInfo['ScaleZ'],
                                           unit='micron',
                                           sizeC=numch,
                                           sizeZ=1,
                                           sizeT=1)

        # concatenate the timepoints
        imglist_t.append(imp_sp_c)

        if numch > 1:
            # create an array
            imgarray = jarray.array(imglist_t, ImagePlus)
            # create an ImageStack from the array
            imgstack = ImageStack.create(imgarray)
            # create an ImagePlus object from the jarray
            new_name = os.path.splitext(os.path.basename(imagefile))[0]
            imp_sp_t = ImagePlus(new_name + '_SHARPEST_CT', imgstack)

        # in case of exactly one channel directly use the ImgPlus
        if numch == 1:
            imp_sp_t = imglist_t[0]

    return imp_sp_t


#########################################################################

# the the filename
IMAGEPATH = FILENAME.toString()

# suffix for the filename of the saved data
SUFFIX = '_SHARPEST_CT'
SAVEFORMAT = 'ome.tiff'

##############################################################

# define path for the output
imagedir = os.path.dirname(IMAGEPATH)
basename = os.path.splitext(os.path.basename(IMAGEPATH))[0]

# remove the extra .ome before reassembling the filename
if basename[-4:] == '.ome':
    basename = basename[:-4]
    log.log(LogLevel.INFO, 'New basename for output :' + basename)

# save processed image
outputimagepath = os.path.join(imagedir, basename + SUFFIX + '.' + SAVEFORMAT)

#############   RUN MAIN IMAGE ANALYSIS PIPELINE ##########

# get the starting time of processing pipeline
start = time.clock()

# run image analysis pipeline
sharpest_image = run(IMAGEPATH, verbose=False)

# get time at the end and calc duration of processing
end = time.clock()
log.log(LogLevel.INFO, 'Duration of whole Processing : ' + str(end - start))

###########################################################

log.log(LogLevel.INFO, 'Save As : ' + outputimagepath)

start = time.clock()

savepath_result_image = ExportTools.savedata(sharpest_image,
                                             outputimagepath,
                                             extension=SAVEFORMAT,
                                             replace=True)

# check if the saving did actually work
filesavestackOK = os.path.exists(savepath_result_image)
log.log(LogLevel.INFO, 'FileCheck 3D Stack Result : ' + str(filesavestackOK))

end = time.clock()

log.log(LogLevel.INFO, 'Duration OME-TIFF export  : ' + str(end - start))
log.log(LogLevel.INFO, 'Saved Processed Image     : ' + savepath_result_image)

# show the image
sharpest_image.show()

# finish
log.log(LogLevel.INFO, 'Done.')
