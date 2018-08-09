from ij import IJ
from ij import *
from ij import ImagePlus
from ij import ImageStack
from ij.measure import *
from ij.plugin import *
from ij.process import *
from ij.plugin import ChannelSplitter
from ij.measure import Measurements
from ij.measure import ResultsTable
from ij.plugin import ImageCalculator
from ij.plugin import RGBStackConverter
from ij.plugin import StackCombiner

from ij.plugin.frame import RoiManager
from ij.process import ImageProcessor
from ij.process import ImageStatistics
from ij.gui import Roi
from ij.gui import PointRoi
from ij.gui import PointRoi
from ij.gui import OvalRoi
import math
from java.awt import *
from java.awt import Font
import itertools
import glob
import os

MakeGallery = True

save_gallery = True

roisize = 10

GalleryROI = 50

Pixelsize = 0.080
framerate = 0.33


twocolor =True


#dataname = "P2_Measurements"
savepath = "c:/example/"


def normList2(L, normalizeTo=100):
    '''normalize values of a list to make its max = normalizeTo'''
    vMax = max(L)
    return [ x/(vMax*1.0)*normalizeTo for x in L]

def CalcVelocity(distancelist, framerate):
    return [x*framerate for x in distancelist]


def GenerateRGB(imp):
    channels1 = imp.getNChannels();
    slices1 = slices2 = imp.getNSlices();
    frames1 = frames2 = imp.getNFrames();
    c1 = imp.getChannel();
    z1 = imp.getSlice();
    t2 = imp.getFrame();
    imp2 = imp.createHyperStack("title2", 1, slices2, frames2, 24)
    RGBStackConverter().convertHyperstack(imp, imp2);
#    imp2.show()
    return imp2

def CombineStacks(imp1, imp2):
    imp1stack = imp1.getStack()
    imp2stack = imp2.getStack()
    imp3stack = StackCombiner().combineVertically(imp1stack, imp2stack)
    imp3 = ImagePlus("Combined Stacks", imp3stack)
#    imp3.show()
    print imp3
    return imp3

def ExtractChannel(imp, channel):
    imp_height = imp.getHeight()
    imp_width = imp.getWidth()
    channelnumber = imp.getNChannels()
    slicenumber = imp.getNSlices()
    timepoints = imp.getNFrames()
    imp2 = IJ.createHyperStack("Gallery",imp_width, imp_height, channelnumber, slicenumber, timepoints, 16)
    imp2.copyLuts(imp)
    for frame in range(1,timepoints+1):
            imp.setT(frame)
            imp.setC(channel)
            imp.copy()
            imp2.setT(frame)
            imp2.setC(channel)
            imp2.paste()
    return imp2

def dist(p0, p1):
    """ Calculates the  distance between two xy coordinates, each
    each coordinated supplied by a tupel"""
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)


## Generates a gallery from multiple point ROIs
imp = IJ.getImage()
roinumber = RoiManager.getInstance().getCount()
channelnumber = imp.getNChannels()
slicenumber = imp.getNSlices()
timer = 0
imp2 = IJ.createHyperStack("Gallery",GalleryROI, GalleryROI, channelnumber, slicenumber, roinumber, 16)
#imp2.copyLuts(imp)
MeanChannel1 = []
#MeanChannel2 = []
#MeanChannel3 = []
XYCoordinates = []
Distance = []
#print roinumber
#for roi in RoiManager.getInstance().getRoisAsArray(): ## Does not work for time, since only xz coordinates are returned
movietime = []

Lastcoordinates = (0,0)
for roi5 in range(roinumber):
    #print roi5
    RoiManager().getInstance().select(imp, roi5)
    roi = imp.getRoi()
    movietime.append(imp.getT())
    timer = timer + 1
 #  proi =  IJ.getImage().getRoi()
    px = roi.getXCoordinates()
    py = roi.getYCoordinates()
    bounds = roi.getBounds()
    #print bounds
    coord = (bounds.x, bounds.y)
    XYCoordinates.append(coord)
    if roi5 ==0:
        Distance.append(0.0)
    else:
        Distance.append(round(dist(Lastcoordinates, coord),3))    
    Lastcoordinates = coord
    #print coord
    roi2 = OvalRoi(coord[0]-(roisize/2), coord[1]-roisize/2, roisize,roisize)
   # imp.setC(1)
    imp.setRoi(roi2)
    stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA | Measurements.FERET | Measurements.CENTROID)
    MeanChannel1.append(stats.mean)
    if MakeGallery:
        roi3 = Roi(coord[0]-(GalleryROI/2), coord[1]-GalleryROI/2, GalleryROI,GalleryROI)
        imp.setRoi(roi3)
        imp.copy()
        imp2.setT(timer)
        imp2.paste()

parameters = 'columns=' +'3' + ' rows=2 scale=1 increment=1 border=4 font=12'
#print parameters
#print imp
if MakeGallery:

    imp7 = imp2
    imp7.show()



NormChannel1 = normList2(MeanChannel1)

Velocity = CalcVelocity(Distance, framerate)

#print MeanChannel1
#print MeanChannel2
#print MeanChannel3
#print NormChannel1
#print NormChannel2
#print NormChannel3
#print XYCoordinates
#print Distance
#print Velocity
ort = ResultsTable()
ort.setPrecision(3)
#print ort.getCounter

count = len(MeanChannel1)
for i in range(count):
    ort.incrementCounter()
    ort.addValue("Frame", i)
    ort.addValue("Channel 1", MeanChannel1[i])
    ort.addValue("X coordinate", str(XYCoordinates[i][0]))
    ort.addValue("Y coordinate", str(XYCoordinates[i][1]))
    ort.addValue("Distance in um", str((Distance[i]*Pixelsize)))
    ort.addValue("Velocity in um/s", str((Velocity[i]*Pixelsize)))
    ort.addValue("Timepoint", str(movietime[i]))
ort.show("Measured intensities")

dataname = imp.getShortTitle()


filename_tif = dataname+"_gallery_001.tif"
files_tif = glob.glob(savepath+"/Galleries/"+dataname+"*.tif")

files_tif.sort()
#print files
if len(files_tif) == 0:
    cur_num_tif = 0
else:
    cur_num_tif = int(os.path.basename(files_tif[-1])[-7:-4])
    filename_tif = os.path.basename(files_tif[-1][:-7])
    cur_num_tif +=1
    cur_num_tif = str(cur_num_tif).zfill(3)
    #print cur_num
    filename_tif = filename_tif+cur_num_tif+str( os.path.basename(files_tif[-1][-4:]))
savename_tif = savepath+"/galleries/"+filename_tif

if save_gallery:
    IJ.saveAs(imp7, "Tiff", savename_tif)
    imp7.changes = False
    imp7.close()


filename = dataname+"_001.csv"
files = glob.glob(savepath+"/Measurements/"+dataname+"*.csv")

files.sort()
#print files
if len(files) == 0:
    cur_num = 0
else:
    cur_num = int(os.path.basename(files[-1])[-7:-4])
    filename = os.path.basename(files[-1][:-7])
    cur_num +=1
    cur_num = str(cur_num).zfill(3)
    #print cur_num
    filename = filename+cur_num+str( os.path.basename(files[-1][-4:]))
savename = savepath+"/Measurements/"+filename
ort.saveAs(savename)


