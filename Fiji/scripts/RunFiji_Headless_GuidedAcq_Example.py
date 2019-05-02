"""
File: RunFiji_Headless_GuidedAcq_Example.czmac
Author: Sebastian Rhode
Date: 2018_10_12
"""
version = 0.4

import sys
# adapt this path depending on your system
sys.path.append(r'c:\Users\m1srh\Documents\External_Python_Scripts_for_OAD')
import ConvertTools as ct
import jsontools as jt
import FijiTools as ft
import clr
import time
from System.Diagnostics import Process
from System.IO import Directory, Path, File, FileInfo


# clear output console
Zen.Application.MacroEditor.ClearMessages()

# define image
czifile = r'c:\Output\Guided_Acquisition\OverViewScan.czi'

#load image in Zen
img = Zen.Application.LoadImage(czifile, False)
Zen.Application.Documents.Add(img)
metadata = jt.fill_metadata(img)


IMAGEJ = 'c:\\Users\\m1srh\\Documents\\Fiji\\ImageJ-win64.exe'
IMAGEJDIR =  Path.GetDirectoryName(IMAGEJ)
SCRIPT = 'c:\\Users\\m1srh\\Documents\\Fiji\\scripts\\GuidedAcq_fromZEN.py'

# define script parameters
params = {}
params['IMAGEJ'] = IMAGEJ
params['IMAGEJSCRIPT'] = SCRIPT
params['IMAGE'] = czifile
params['IMAGEDIR'] = Path.GetDirectoryName(czifile)
params['FILEWOEXT'] = Path.GetFileNameWithoutExtension(czifile)

# define processing parameters
params['JSONPARAMSFILE'] =  Path.Combine(params['IMAGEDIR'], params['FILEWOEXT'] + '.json')
params['BIN'] = 4
params['RANKFILTER'] = 'MEDIAN'
params['RADIUS'] = 3.0
params['THRESHOLD'] = 'Triangle'
params['THRESHOLD_BGRD'] = 'black'
params['CORRFACTOR'] = 1.0
params['MINSIZE'] = 10000
params['MINCIRC'] = 0.01
params['MAXCIRC'] = 0.99
params['PYLEVEL'] = 0
# define outputs
params['PASAVE'] = True
params['SAVEFORMAT'] = 'ome.tiff'
params['RESULTTABLE'] = ''
params['RESULTIMAGE'] = ''

# update dictionary
params.update(metadata)

print params

# write JSON file for Fiji
jsonfilepath = jt.write_json(params, jsonfile=params['FILEWOEXT']+'.json', savepath=params['IMAGEDIR'])
print('Save Data to JSON: ', jsonfilepath)

# configre the options
option1 = "--ij2 --headless --console --run " + SCRIPT + " "
option2 = '"' + "JSONPARAMFILE=" + "'" + params['JSONPARAMSFILE'] + "'" + '"'
print(option1)
print(option2)
option = option1 + option2
print(option)

fijistr = ft.createFijistring(IMAGEJDIR, SCRIPT, jsonfilepath)
fijistr = fijistr.replace('\\', '\\\\')
print fijistr

# start Fiji script in headless mode
app = Process()
#app.StartInfo.FileName = IMAGEJ
app.StartInfo.FileName = "java"
app.StartInfo.Arguments = fijistr
app.Start()
# wait until the script is finished
app.WaitForExit()
excode = app.ExitCode

print('Exit Code: ', excode)
print('Fiji Analysis Run Finished.')

# read metadata JSON - the name of the file must be specified correctly
md_out = jt.readjson(jsonfilepath)
print('ResultTable: ', md_out['RESULTTABLE'])
# extract the relevant data
OVScan_CenterX = md_out['CENTERX']
OVScan_CenterY = md_out['CENTERY']
OVScan_Width = md_out['WIDTH_MICRON']
OVScan_Height = md_out['HEIGHT_MICRON']

# show result image
rimage = Zen.Application.LoadImage(md_out['RESULTIMAGE'])
Zen.Application.Documents.Add(rimage)

# auto-dosplay min-max
ids = rimage.DisplaySetting.GetAllChannelIds()
for id in ids:
    rimage.DisplaySetting.SetParameter(id, 'IsAutoApplyEnabled', True)

# initialize ZenTable object
SingleObj = ZenTable()
# read the result table and convert into a ZenTable
SingleObj = ct.ReadResultTable(md_out['RESULTTABLE'], 1, '\t', 'FijiTable', SingleObj)
# change the name of the table
SingleObj.Name = Path.GetFileNameWithoutExtension(Path.GetFileName(md_out['RESULTTABLE']))
# show and save data tables to the specified folder
Zen.Application.Documents.Add(SingleObj)

# check the table for the required colums
colrequired = ['BX', 'BY', 'Width', 'Height']
colID, columnOK = ct.CheckTableColumns(SingleObj, requiredcols=colrequired)

if columnOK == False:
    message = 'Required column(s) not found. No Detailed Experiment is possible.'
    print message
    raise SystemExit

# check the number of detected objects = rows inside image analysis table
num_POI = SingleObj.RowCount

# execute detailed experiment at the position of every detected object
for i in range(0, num_POI, 1):

    # get the object information from the position table
    POI_ID = SingleObj.GetValue(i, 0) # get the ID of the object - IDs start with 2 !!!
    xpos_Fiji = SingleObj.GetValue(i, colID['BX']) # get X-position from table
    ypos_Fiji = SingleObj.GetValue(i, colID['BY']) # get Y-position from table
    bwidth = SingleObj.GetValue(i, colID['Width']) # get the width of the bounding box
    bheight = SingleObj.GetValue(i, colID['Height']) # get the height of the bounding box
    
    # convert to ZEN Stage coordinate
    #xpos, ypos = Fiji2ZenStageXY(xpos_Fiji, ypos_Fiji, OVScan_CenterX, OVScan_CenterY, OVScan_Width, OVScan_Height)
    xpos, ypos = ct.BoundingCenterFiji2StageXY(xpos_Fiji, ypos_Fiji, bwidth, bheight, OVScan_CenterX, OVScan_CenterY, OVScan_Width, OVScan_Height)

    # move to the current position
    print('Moving Stage to Object ID:', POI_ID, ' at :', round(xpos, 2), round(ypos, 2))
