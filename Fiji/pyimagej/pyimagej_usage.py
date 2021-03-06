# This script shows the basic functionalities of the Python imagej client.
# It uploads an image to imagej-server, inverts the image, and display both the
# original and the inverted ones.


import imagej.server as imagej
#import imagej
import json


fiji_location = r'c:\Users\m1srh\Documents\Fiji'
filename = r'C:\Temp\input\01_DAPI.ome.tiff'

ij = imagej.IJ()
#ij = imagej.init(fiji_location)

# Find modules that contain a specific string in its ID.
create = ij.find("CreateImgFromImg")[0]
invert = ij.find("InvertII")[0]

# Check details of a module. Names of "inputs" and "outputs" are usually important.
print('Details for CreateImgFromImg:')
print(json.dumps(ij.detail(create), indent=4))
print('Details for InvertII:')
print(json.dumps(ij.detail(invert), indent=4))

# Upload an image.
img_in = ij.upload(filename)

# Execute modules.
result = ij.run(create, {'in': img_in})
img_out = result['out']
result = ij.run(invert, {'in': img_in, 'out': img_out})
img_out = result['out']

# retrieve/show images.
ij.retrieve(img_out, format='png', dest='/tmp')
ij.show(img_in, format='jpg')
ij.show(img_out)
