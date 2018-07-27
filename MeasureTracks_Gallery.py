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

roisize = 7

GalleryROI = 15

Pixelsize = 0.080
framerate = 0.33

threecolour = False


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
imp2.copyLuts(imp)
MeanChannel1 = []
MeanChannel2 = []
MeanChannel3 = []
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
    imp.setC(1)
    imp.setRoi(roi2)
    stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA | Measurements.FERET | Measurements.CENTROID)
    MeanChannel1.append(stats.mean)
    imp.setC(2)
    stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA | Measurements.FERET | Measurements.CENTROID)
    MeanChannel2.append(stats.mean)
    if channelnumber > 2:
       imp.setC(3)
       stats = imp.getStatistics(Measurements.MEAN | Measurements.AREA | Measurements.FERET | Measurements.CENTROID)
       MeanChannel3.append(stats.mean)
       threecolour = True
    roi3 = Roi(coord[0]-(GalleryROI/2), coord[1]-GalleryROI/2, GalleryROI,GalleryROI)
    imp.setC(1)
    imp.setRoi(roi3)
    imp.copy()
    imp2.setT(timer)
    imp2.setC(1)
    imp2.paste()
    imp.setC(2)
    imp.copy()
    imp2.setC(2)
    imp2.paste()
    if channelnumber > 2:
       imp.setC(3)
       imp.copy()
       imp2.setC(3)
       imp2.paste()
       threecolour = True

parameters = 'columns=' +'3' + ' rows=2 scale=1 increment=1 border=4 font=12'
print parameters
print imp

imp3 = ExtractChannel(imp2, 1)
imp4 = ExtractChannel(imp2, 2)
if threecolour:
    imp5 = ExtractChannel(imp2,3)

imp6 = CombineStacks(GenerateRGB(imp2), GenerateRGB(imp3))
imp7 = CombineStacks(imp6, GenerateRGB(imp4))
if threecolour:
    imp8 = CombineStacks(imp7, GenerateRGB(imp5))
    imp8.show()
else:
    imp7.show()


NormChannel1 = normList2(MeanChannel1)
NormChannel2 = normList2(MeanChannel2)
if threecolour:
    NormChannel3 = normList2(MeanChannel3)
else:
    NormChannel3 = []

Velocity = CalcVelocity(Distance, framerate)

print MeanChannel1
print MeanChannel2
print MeanChannel3
print NormChannel1
print NormChannel2
print NormChannel3
print XYCoordinates
print Distance
print Velocity
ort = ResultsTable()
ort.setPrecision(3)
print ort.getCounter

count = len(MeanChannel1)
for i in range(count):
	ort.incrementCounter()
	ort.addValue("Frame", i)
	ort.addValue("Channel 1", MeanChannel1[i])
	ort.addValue("Channel 2", MeanChannel2[i])
	if threecolour:
	    ort.addValue("Channel 3", MeanChannel3[i])
	ort.addValue("NormCh 1", NormChannel1[i])
	ort.addValue("NormCh 2", NormChannel2[i])
        if threecolour:
            ort.addValue("NormCh 3", NormChannel3[i])
        ort.addValue("XY coordinates", str(XYCoordinates[i]))
        ort.addValue("Distance in um", str((Distance[i]*Pixelsize)))
        ort.addValue("Velocity in um/s", str((Velocity[i]*Pixelsize)))
ort.show("Measured intensities")

