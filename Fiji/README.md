# scripts

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

# docker

This explains how to create your own docker container with the latest Fiji inside.

1. Download latest Fiji for Linux and unpack it.
2. There should be a folder called Fiji.app inside the same folder as the dockefile.
3. Make sure docker is running and open a terminal.

```bash
docker login
user:yourusername
pwd:yourpwd
```

The dockerfile for updating and creating Fiji docker container looks like this:

```docker
# Pull base JDK-8 image only ig using Fiji that doe not already contain a JDK.
#FROM java:8-jre
FROM ubuntu:latest

COPY ./Fiji.app /Fiji.app

# copy Fiji and other scripts or files
#COPY ./fijipytools.py /Fiji.app/scripts

# add Fiji-Update sites
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BAR http://sites.imagej.net/Tiago/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BASIC http://sites.imagej.net/BaSiC/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BIG-EPFL http://sites.imagej.net/BIG-EPFL/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BioVoxxel http://sites.imagej.net/BioVoxxel/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site CMP-BIAtools http://sites.imagej.net/CMP-BIA/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site IBMP-CNRS http://sites.imagej.net/Mutterer/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site IJPB-plugins http://sites.imagej.net/IJPB-plugins/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site ImageScience http://sites.imagej.net/ImageScience/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site IMCFUniBasel http://sites.imagej.net/UniBas-IMCF/
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site MOSAICToolSuite http://mosaic.mpi-cbg.de/Downloads/update/Fiji/MosaicToolsuite
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site PTBIOP http://biop.epfl.ch/Fiji-Update
RUN ./Fiji.app/ImageJ-linux64 --ij2 --headless --update update
RUN ./Fiji.app/ImageJ-linux64 --ij2 --headless
```

When the login was sucessfull start the build and push the new container.

```bash
docker build -t xyz/fiji_linux64_baseimage:latest .

docker push xyz/fiji_linux64_baseimage:latest
```
