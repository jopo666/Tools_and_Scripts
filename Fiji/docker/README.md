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
COPY ./fijipytools.py /Fiji.app/scripts

# add Fiji-Update sites
RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BAR http://sites.imagej.net/Tiago/
#RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BASIC http://sites.imagej.net/BaSiC/
#RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BIG-EPFL http://sites.imagej.net/BIG-EPFL/
#RUN ./Fiji.app/ImageJ-linux64 --update add-update-site BioVoxxel http://sites.imagej.net/BioVoxxel/
#RUN ./Fiji.app/ImageJ-linux64 --update add-update-site CMP-BIAtools http://sites.imagej.net/CMP-BIA/
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
docker build -t czsip/fiji_linux64_baseimage:latest .

docker push czsip/fiji_linux64_baseimage:latest
```