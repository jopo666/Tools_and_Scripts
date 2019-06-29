# Tools and Scripts

This is a collection tools and scripts related to Fiji. Use the at your own risk. Most likely this scripts still contains some bugs or things that could be implemented in a much smarter way. Feedback is appreciated.

The structure is still a bit "messy" and will most likely change ...

## fijipytools.py

Since many image analysis workflows required the same kind of building blocks it makes sense top collect useful tools and functions inside on module. This way it those functions can be reused and simplified, so that the actual image analysis script becomes "cleaner" and "easier to read".

### Function and Tools inside fijipytools.py

Very brief descriptions of the functions. Most things are commented inside the source code

#### ImportTools

* here the most import metadata will be read and stored inside a dictionary
* depending on the file extension the correct function to open the image file will be used
  * readbf - for all kind of files
  * readCZI - reads CZI using BioFormats with many additional options like specifying the desired pyramid level etc.
  * openJPG - reading JPGs using the standard IJ opener or BioFormats

#### ExportTools

* depending on the choose file extension BioFormats or other built-in save methods will be used
* moss common use case is obviously to save the image data as OME-TIFF using the BioFormats exporter

#### FilterTools

* simple wrapper to use the rolling ball background subtraction
* can be used to apply a rank filter, like *Median*

#### BinaryTools

* can be used to fill holes inside a binary image using MorphoLibJ functionality

#### WaterShedTools

* checks if the image is a z-stack and calls either a 2D or 3D watershed
* uses the built-in watershed to separate objects in 2D images
* uses the MorphoLibJ 3D watershed to separate binary objects in 3D

#### ImageTools

* can be used to read a specific images series or pyramid level (for CZIs) from an image

#### ThresholdTools

* this function allows to apply a threshold to a stack using various methods like *Otsu*
* the threshold can be calculated slice-by-slice or for the whole stack
* it is possible to apply a correction factor to the calculated threshold value

#### AnalyzeTools

* can be used to call the ParticleAnalyzer with various options

#### RoiTools

* add the detected objects to the ROI manager when needed

#### MiscTools

* apply binning to an image to reduce its size
* can detect the file extension
* set or change the properties and the scaling for an ImagePlus
* split an image into different channels

#### JSONTools

* read and write JSON files
* is useful when writing modules for [APEER](https://www.apeer.com "APEER - Free and Open Platform for Your Processing Needs")
* for more details please check: [APEER - Fiji Python Tutorial](https://docs.apeer.com/tutorials/fiji-python-scripting "APEER - Use Fiji Python Scripting to create your own module")



