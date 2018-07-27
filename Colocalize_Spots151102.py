"""
    """
from ij import IJ, ImagePlus, ImageStack
from ij.plugin.frame import RoiManager
from ij.plugin import Duplicator
from ij.plugin import ImageCalculator
from ij.plugin import ZProjector
from ij.measure import ResultsTable
from ij.plugin import Concatenator
from ij.measure import Measurements
import math
from java.awt import *
import itertools
from ij.gui import Roi
from ij.gui import PointRoi
from ij.gui import OvalRoi
from java.lang import Boolean
import time
import itertools
import glob
import os

# Indicate noise level for channels

spot_max_distance = 5

noiseC1 = "2000"

noiseC2 = "5000"

noiseC3 = "300"

testrun = True # True or False

subst_mean_sd = True

show_coloc = True # True or False
# Save the results automatically as  CSV file ?
automatic_save_results = False # True or False

#path for CSV save
savepath = "E:\Eva/ColocalizeSpotsScript/HRS1-769_C4B_EGF/Measurements/"


# Clear all items from ROI manager



####

noisec1_1 = '"noise=' + str(noiseC1) + ' output=[Point Selection]"'   # generates the parameters for the find maxima dialog in Channel 1

noisec2_1 = '"noise=' + str(noiseC2) + ' output=[Point Selection]"'   # generates the parameters for the find maxima dialog in Channel 1

noisec3_1 = '"noise=' + str(noiseC3) + ' output=[Point Selection]"'   # generates the parameters for the find maxima dialog in Channel 1




imp0 = IJ.getImage()

if testrun:
    imp_1 = Duplicator().run(imp0, 1, 3, 1, 1, 1, 3) # Extract the first 3 spots, to change change the last 2 values
    imp_2 = Duplicator().run(imp0, 1, 3, 1, 1, 201, 203)# extract the last 3 spots
    imp_3 = Duplicator().run(imp0, 1, 3, 1, 1, 597, 599)# extract the last 3 spots
    
    concat = Concatenator()
    imp1_1 = concat.concatenateHyperstacks((imp_1, imp_2, imp_3), "Concatenated", True)
    #IJ.run(imp_1, "Concatenate...", "  title=[Test Stack] image1=Image1 image2=Image2 image3=[-- None --]");
    imp1_1.show()
    imp = IJ.getImage()
else:
    imp = imp0.duplicate()
imp.show()
# def maxZprojection(stackimp):
#     """ from EMBL python / Fiji cookbook"""
#     allTimeFrames = Boolean.TRUE
#     zp = ZProjector(stackimp)
#     zp.setMethod(ZProjector.MAX_METHOD)
#     zp.doHyperStackProjection()
#     zpimp = zp.getProjection()
#     return zpimp


def DoG(imp0, kernel1, kernel2):
    """Thresholds image and returns thresholded image,
    merge code still quite clumsy but functional"""
    imp1 = imp0.duplicate()
    imp2 = imp0.duplicate()
    IJ.run(imp1, "Gaussian Blur...", "sigma=" + str(kernel1) + " stack")
    IJ.run(imp2, "Gaussian Blur...", "sigma="+ str(kernel2) + " stack")
    ic = ImageCalculator()
    imp3 = ic.run("Subtract create stack", imp1, imp2)
    return imp3


def ExtractChannel(imp, channel):
    imp_height = imp.getHeight()
    imp_width = imp.getWidth()
    channelnumber = imp.getNChannels()
    slicenumber = imp.getNSlices()
    timepoints = imp.getNFrames()
    ExtractedChannel = Duplicator().run(imp, channel, channel, 1, slicenumber, 1, timepoints)
    ExtractedChannel.setTitle("Gallery_Channel_" + str(channel))
    return ExtractedChannel


def ThresholdMaxEntropy(imp0):
    """Thresholds image and returns thresholded image, merge code still quite clumsy but functional"""
    imp0 = IJ.getImage()
    impthres = imp0.duplicate()
    imp01 = ImagePlus("Channel1", ChannelSplitter.getChannel(imp0, 1))
    imp02 = ImagePlus("Channel2", ChannelSplitter.getChannel(imp0, 2))
    imp001 = imp01.duplicate()
    imp002 = imp02.duplicate()
    IJ.setAutoThreshold(imp001, "MaxEntropy dark")
    IJ.run(imp001, "Convert to Mask", "");
    IJ.run(imp001, "Divide...", "value=255");
    IJ.setAutoThreshold(imp002, "MaxEntropy dark")
    IJ.run(imp002, "Convert to Mask", "");
    IJ.run(imp002, "Divide...", "value=255");
    ic = ImageCalculator()
    imp0001 = ic.run("Multiply create", imp01, imp001)
    ic2 = ImageCalculator()
    imp0002 = ic2.run("Multiply create", imp02, imp002)
    imp0001.copy()
    impthres.setC(1)
    impthres.paste()
    imp0002.copy()
    impthres.setC(2)
    impthres.paste()
    imp01.close()
    imp02.close()
    imp001.close()
    imp002.close()
    imp0001.close()
    imp0002.close()
    return impthres




#dist_min = 1 
#dist_max = 10 
 
def dist(p0, p1): 
    """ Calculates the  distance between two xy coordinates, each
    each coordinated supplied by a tupel"""
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2) 

#x = [] 
#y = [] 
 
# pearson code from from http://stackoverflow.com/questions/3949226/calculating-pearson-correlation-and-significance-in-python 
 
def average(x): 
    """calculates the averade of a list x"""
    assert len(x) > 0 
    return float(sum(x)) / len(x) 
 
def pearson_def(x, y):
    """Calculate pearson correlation between list x and y, lists need to have the same length"""
    assert len(x) == len(y) 
    n = len(x) 
    assert n > 0 
    avg_x = average(x) 
    avg_y = average(y) 
    diffprod = 0 
    xdiff2 = 0 
    ydiff2 = 0 
    for idx in range(n): 
        xdiff = x[idx] - avg_x 
        ydiff = y[idx] - avg_y 
        diffprod += xdiff * ydiff 
        xdiff2 += xdiff * xdiff 
        ydiff2 += ydiff * ydiff 
    if (xdiff2 * ydiff2) != 0:   # checks if one of the pixels is 0  intensity, avoids div0 error
        return round((diffprod / math.sqrt(xdiff2 * ydiff2) ),3)
    else:
        return "n/a" #returns "n/a" if one pixel value is 0
        

# function to get the pixel values in a ROI as a list 
# gets the bounding box and the corresponding mask for polygon ROI, then retrieves the intensity values of all pixels within the ROI as a list 
# Code adapted from Java implementation in Burger and Burge "Digital image processing" 
 
def pixel_values(roi): 
    """extract each pixel value from a polygon roi into a list
    does not work for square rois!"""
    pixel = [] 
    mask =  roi.getMask()    # polygon rois are defined by a mask
    box = roi.getBounds() 
    boxLeft = box.x 
    boxRight = boxLeft + box.width 
    boxTop = box.y 
    boxBottom = boxTop + box.height 
    for v in range (boxTop, boxBottom): 
        for u in range (boxLeft, boxRight):       
            if mask.getPixel(u - boxLeft, v - boxTop) > 0: 
                pixel.append(imp.getProcessor().getPixel(u,v)) 
    return pixel 
 
def pixel_values_rect(roi): 
    """extract each pixel value from a square roi into a list"""
    pixel = [] 
    mask =  roi.getMask() 
    box = roi.getBounds() 
    boxLeft = box.x 
    boxRight = boxLeft + box.width 
    boxTop = box.y 
    boxBottom = boxTop + box.height 
    for v in range (boxTop, boxBottom): 
        for u in range (boxLeft, boxRight):
            #if mask.getPixel(u - boxLeft, v - boxTop) > 0: 
            pixel.append(imp.getProcessor().getPixel(u,v)) 
    return pixel 


imp_height = imp.getHeight()
imp_width = imp.getWidth()
channelnumber = imp.getNChannels()
slicenumber = imp.getNSlices()
timepoints = imp.getNFrames()
if subst_mean_sd:
    for times in range(1,timepoints+1):
        imp.setT(times)
        imp.setC(1)
        stats = imp.getStatistics(Measurements.MEAN |Measurements.STD_DEV)  
        means = stats.mean
        standard_dev = stats.stdDev
        sub_value = means+2*standard_dev
        IJ.run(imp, "Select None", "");
        imp.getProcessor().subtract(sub_value)
        imp.setC(2)
        stats = imp.getStatistics(Measurements.MEAN |Measurements.STD_DEV)  
        means = stats.mean
        standard_dev = stats.stdDev
        sub_value = means+2*standard_dev
        IJ.run(imp, "Select None", "");
        imp.getProcessor().subtract(sub_value)
        imp.setC(3)
        stats = imp.getStatistics(Measurements.MEAN |Measurements.STD_DEV)  
        means = stats.mean
        standard_dev = stats.stdDev
        sub_value = means+2*standard_dev
        IJ.run(imp, "Select None", "");
        imp.getProcessor().subtract(sub_value)
    
# Extact channel to Threshold, set automatic threshold
imp_DoG1 = DoG(imp,1,3)
imp_DoG1.show()
#IJ.run(imp_DoG, "Z Project...", "projection=[Max Intensity] all")
imp_DoG_zMaxC1 = IJ.getImage()
imp_DoG_zMaxC1.setTitle("Difference_of_Gaussian C1")

#IJ.run(imp_DoG, "Z Project...", "projection=[Max Intensity] all")

# # Duplicate the original image in case a ROI was used to mark the thresholded image

# # channelnumber = imp1.getNChannels()
# # slicenumber = imp1.getNSlices()
# # timepoints = imp1.getNFrames()
# # imp_measure =  Duplicator().run(imp1, 1, channelnumber, 1, slicenumber, 1, timepoints)
# # imp_measure.show()
IJ.run("Clear Results", "");

ort = ResultsTable() 
ort.setPrecision(0) 
#print ort.getCounter 
ort.setHeading(0, "Frame") 
ort.setHeading(1, "Spots Ch1") 
ort.setHeading(2, "Spots Ch2")
ort.setHeading(3, "Spots Ch3")
ort.setHeading(4, "Coloc_Spots_Ch1_Ch2")
ort.setHeading(5, "Coloc_Spots_Ch1_Ch3")
ort.setHeading(6, "Coloc_Spots_Ch2_Ch3")

time.sleep(0.5)

IJ.run(imp_DoG1, "Select None", "")

imp_DoG1.show()


## iterating htough timepoints

imp_height = imp.getHeight()
imp_width = imp.getWidth()
channelnumber = imp.getNChannels()
slicenumber = imp.getNSlices()
timepoints = imp.getNFrames()





for times in range(1,timepoints+1):
    imp_DoG1.setT(times) 
    imp_DoG1.setC(1) 
    points_C1 = []
    IJ.run(imp_DoG1, "Find Maxima...", noisec1_1)    # Finds the maxima in Channel 1, gets them as array of point ROIs
    proi = IJ.getImage().getRoi() 
    if proi.getClass() == PointRoi: 
        #### For each point ROI identified by FindMaxima, the coordinates are added to a list
        px = proi.getXCoordinates() 
        py = proi.getYCoordinates() 
        bounds = proi.getBounds() 
        #points_C1 = [] 
        for i in range(proi.getNCoordinates()): 
           points_C1.append((bounds.x + px[i], bounds.y + py[i])) 
           #points.append((px[i], py[i]))
    #IJ.run(imp_DoG1, "Draw", "");
    IJ.run(imp_DoG1, "Select None", "");
    imp_DoG1.setC(2)
    IJ.run(imp_DoG1 , "Find Maxima...", noisec2_1)
    proi2 =  IJ.getImage().getRoi()
    points_C2 = []
    if proi2.getClass() == PointRoi:
        px2 = proi2.getXCoordinates()
        py2 = proi2.getYCoordinates()
        bounds2 = proi2.getBounds()
        #points_C2 = []
        for i in range(proi2.getNCoordinates()):
           points_C2.append((bounds2.x + px2[i], bounds2.y + py2[i]))
           #points.append((px[i], py[i]))
        #print points_C2
    imp_DoG1.setC(3)
    IJ.run(imp_DoG1 , "Find Maxima...", noisec3_1)
    proi3 =  IJ.getImage().getRoi()
    points_C3 = []
    if proi3.getClass() == PointRoi:
        px3 = proi3.getXCoordinates()
        py3 = proi3.getYCoordinates()
        bounds3 = proi3.getBounds()
        #points_C2 = []
        for i in range(proi3.getNCoordinates()):
           points_C3.append((bounds3.x + px3[i], bounds3.y + py3[i]))
           #points.append((px[i], py[i]))
        #print points_C2

    if testrun:
        if points_C1 != []:
            for item1 in points_C1:
                imp_DoG1.setC(1)
                roi1 = OvalRoi(item1[0]-2, item1[1]-2,5,5)
                imp_DoG1.setRoi(roi1)
                IJ.run("Overlay Options...", "stroke=Red width=0 fill=none set")
                IJ.run(imp_DoG1, "Add Selection...", "")
                IJ.run(imp_DoG1, "Select None", "")

        if points_C2 != []:
            for item2 in points_C2:
                imp_DoG1.setC(2)
                roi2 = OvalRoi(item2[0]-2, item2[1]-2,5,5)
                imp_DoG1.setRoi(roi2)
                IJ.run("Overlay Options...", "stroke=Green width=0 fill=none set")
                IJ.run(imp_DoG1, "Add Selection...", "")
                IJ.run(imp_DoG1, "Select None", "")
        if points_C3 != []:
            for item3 in points_C3:
                imp_DoG1.setC(3)
                roi3 = OvalRoi(item3[0]-2, item3[1]-2,5,5)
                imp_DoG1.setRoi(roi3)
                IJ.run("Overlay Options...", "stroke=White width=0 fill=none set")
                IJ.run(imp_DoG1, "Add Selection...", "")
                IJ.run(imp_DoG1, "Select None", "")

    print times, len(points_C1), len(points_C2), len(points_C3)
    colocalized_spots_c1c2_C1 = []
    colocalized_spots_c1c2_C2 = []    
    if points_C1 != [] and points_C2 != []:
        for item1 in points_C1:
            for item2 in points_C2:
                distance = dist(item1, item2)
                if distance < spot_max_distance:
                    colocalized_spots_c1c2_C1.append(item1)                    
                    colocalized_spots_c1c2_C2.append(item2)
                    if show_coloc:
                        imp_DoG1.setC(1)
                        roi1 = OvalRoi(item1[0]-4, item1[1]-4,8,8)
                        imp_DoG1.setRoi(roi1)
                        IJ.run("Overlay Options...", "stroke=Yellow width=0 fill=none set")
                        IJ.run(imp_DoG1, "Add Selection...", "")
                        IJ.run(imp_DoG1, "Select None", "")

    print len(colocalized_spots_c1c2_C1), len(colocalized_spots_c1c2_C2)     

    colocalized_spots_c1c3_C1 = []
    colocalized_spots_c1c3_C3 = []

    if points_C1 != [] and points_C3 != []:
        for item1 in points_C1:
            for item2 in points_C3:
                distance = dist(item1, item2)
                if distance < spot_max_distance:
                    colocalized_spots_c1c3_C1.append(item1)                    
                    colocalized_spots_c1c3_C3.append(item2)
                    if show_coloc:
                        imp_DoG1.setC(1)
                        roi1 = OvalRoi(item1[0]-4, item1[1]-4,8,8)
                        imp_DoG1.setRoi(roi1)
                        IJ.run("Overlay Options...", "stroke=Magenta width=0 fill=none set")
                        IJ.run(imp_DoG1, "Add Selection...", "")
                        IJ.run(imp_DoG1, "Select None", "")

    print len(colocalized_spots_c1c3_C1), len(colocalized_spots_c1c3_C3)         
    colocalized_spots_c2c3_C2 = []
    colocalized_spots_c2c3_C3 = []
    if points_C2 != [] and points_C3 != []:
        for item1 in points_C2:
            for item2 in points_C3:
                distance = dist(item1, item2)
                if distance < spot_max_distance:
                    colocalized_spots_c2c3_C2.append(item1)                    
                    colocalized_spots_c2c3_C3.append(item2)
                    if show_coloc:
                        imp_DoG1.setC(1)
                        roi1 = OvalRoi(item1[0]-4, item1[1]-4,8,8)
                        imp_DoG1.setRoi(roi1)
                        IJ.run("Overlay Options...", "stroke=Cyan width=0 fill=none set")
                        IJ.run(imp_DoG1, "Add Selection...", "")
                        IJ.run(imp_DoG1, "Select None", "")

    print len(colocalized_spots_c2c3_C3), len(colocalized_spots_c2c3_C3)
    ort.incrementCounter()
    ort.addValue("Frame", times) 
    ort.addValue("Spots Ch1", len(points_C1)) 
    ort.addValue("Spots Ch2", len(points_C2))
    ort.addValue("Spots Ch3", len(points_C3))
    ort.addValue("Coloc_Spots_Ch1_Ch2", len((colocalized_spots_c1c2_C1)))
    ort.addValue("Coloc_Spots_Ch1_Ch3", len((colocalized_spots_c1c3_C1)))
    ort.addValue("Coloc_Spots_Ch2_Ch3", len((colocalized_spots_c2c3_C2)))
    

ort.show("Colocalized Spots")

#####  Cleaning up... ####

imp_DoG1.changes = False
#imp_DoG1.close()






# #    IJ.run(imp_measure, "Make Band...", "band=0.63")    # values are in um, assumes pixelsize of 0.21

#   # imp_measure.setRoi(roi)
#   # ROIFrame = roi.getPosition()
#   # imp_measure.setPosition(ROIFrame)
#  #    imp_measure.setT(roi.getTPosition())
#  #    imp_measure.setZ(roi.getZPosition())
#  #    imp_measure.setC(1)
#     IJ.run(imp_measure, "Measure", "")

dataname = imp0.getShortTitle()
#ort = ResultsTable.getResultsTable()
if automatic_save_results:
    # Gather filenames of the savedirectory
    filename_ort = dataname+"_001.csv"
    files_ort = glob.glob(savepath+"/"+dataname+"*.csv")

    files_ort.sort() # sort by numbering, needed to get the last filenname number
    #print files
    # if len(files_ort) == 0: # check if a file exists, if not, simply use the existing filename
    #     cur_num_ort = 0  # do we need this?
    # else:
        # Check if filenames already exists, if so, get the last available number and increment by 1
    if len(files_ort) != 0:
        cur_num_ort = int(os.path.basename(files_ort[-1])[-7:-4]) # get the curtrent file number
        filename_ort = os.path.basename(files_ort[-1][:-7]) # get the current file name
        cur_num_ort += 1   # increment file number by 1
        cur_num_ort = str(cur_num_ort).zfill(3)  # pad it to 3 digits
        #print cur_num
        filename_ort = filename_ort+cur_num_ort+str(os.path.basename(files_ort[-1][-4:])) # generate final filename
    savename_ort = savepath+filename_ort # Generate complete savepath
    print savename_ort
    ort.saveAs(savename_ort) # save


