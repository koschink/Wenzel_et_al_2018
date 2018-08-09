# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:42:59 2015

@author: kaysch
"""

from __future__ import division

from pandas import *
import pandas as pd
from math import *
import matplotlib.pyplot as plt
import numpy
import glob
import os

   
datapath = os.path.dirname(__file__)
dir_name = os.path.basename(datapath)
print dir_name
print datapath
splits = dir_name.split('_')
print splits[0]
print splits[1]
print splits[2]

savepath = datapath + "/Measurements"

## To normalize to different starting points, add the frame of the starting point to the list below, separated by " , "
## Then set the value "do_timewarp" to "True"
## While doing this, you might want to sing 
## "Let's do the timewarp again" from the Rocky Horror Picture show :-)



shifting_matrix = [0,0,0,0,-10,-10,5]

do_timewarp = True


#if do_timewarp:
#    chance = random(100)
#    if chance == (25):
#        print """
#    
#    
#It’s just a jump to the left,
#and then a step to the right,
#with your hands on your hips,
#and bring your knees in tight!
#But it's the pelvic thrust
#that really drives you insane!
#Let's do the time warp again!
#Let's do the time warp again!
#
#
#"""


Channel_1 = []
Channel_2 = []
Channel_3 = []

coloc_C1_C2 = []
coloc_C1_C3 = []
coloc_C2_C3 = []

norm_egf_C1 = []
norm_egf_C2 = []
files = glob.glob(savepath+"/*.csv")

#files = files[1:29]

print files

f = lambda x: ((x-x.min())/(x.max()-x.min())*100)
f2 = lambda x: (x/x.max()*100)
f3 = lambda x: (x/x.min())
f4 = lambda x: (x-x.min())
f5 = lambda x: (x/x.mean())

Normalize_percent = lambda x: (100/x)

normalisation = f

for csvfiles in files:
    df = pd.read_csv(csvfiles, sep=',', decimal='.', index_col=0)
    df["Norm_EGF_C1"] = df["Spots Ch3"].apply(Normalize_percent)*df["Coloc_Spots_Ch1_Ch3"]
    df["Norm_EGF_C2"] = df["Spots Ch3"].apply(Normalize_percent)*df["Coloc_Spots_Ch2_Ch3"]
    
    
    df_Channel1= df["Spots Ch1"]
    df_Channel2 = df["Spots Ch2"]
    df_Channel3 = df["Spots Ch3"]
    Coloc_1_2 = df["Coloc_Spots_Ch1_Ch2"]
    Coloc_1_3 = df["Coloc_Spots_Ch1_Ch3"]    
    Coloc_2_3 = df["Coloc_Spots_Ch2_Ch3"]    
    
    
    
    Norm_Coloc_C1C3 = df["Norm_EGF_C1"]
    Norm_Coloc_C2C3 = df["Norm_EGF_C2"]
    
    #df11 = df2.apply(f2)
 #   df1["Norm"] = df1["Mean_Intensity"] - df1["Center_Intensity_Channel1"]
#    df1["Norm2"] = df11["Mean_Intensity_Perimeter"]
#    df1["Norm3"] = df11["Center_Intensity_Channel1"]
#        
    #print df1["Mean_Intensity"]    
    Channel_1.append(df_Channel1)
    Channel_2.append(df_Channel2)
    Channel_3.append(df_Channel3)
    coloc_C1_C2.append(Coloc_1_2)
    coloc_C1_C3.append(Coloc_1_3)
    coloc_C2_C3.append(Coloc_2_3)
    norm_egf_C1.append(Norm_Coloc_C1C3)
    norm_egf_C2.append(Norm_Coloc_C2C3)    
    #list2.append(df11)

SpotsC1 = pd.concat(Channel_1, axis=1)
SpotsC2 = pd.concat(Channel_2, axis=1)
SpotsC3 = pd.concat(Channel_3, axis=1)

ColocC1vsC2 = pd.concat(coloc_C1_C2, axis=1)
ColocC1vsC3 = pd.concat(coloc_C1_C3, axis=1)
ColocC2vsC3 = pd.concat(coloc_C2_C3, axis=1)


Norm_to_EGF_ColC1_C3 = pd.concat(norm_egf_C1, axis=1)

Norm_to_EGF_ColC2_C3 = pd.concat(norm_egf_C2, axis=1)


if do_timewarp:
    headings = range(1, (len(shifting_matrix)+1))

    SpotsC1.columns = headings
    
    SpotsC2.columns = headings
    SpotsC3.columns = headings
    ColocC1vsC2.columns = headings
    ColocC1vsC3.columns = headings
    ColocC2vsC3.columns = headings
    Norm_to_EGF_ColC1_C3.columns = headings
    Norm_to_EGF_ColC2_C3.columns = headings
    
    
    for position, movement in enumerate(shifting_matrix):
        print position 
        print movement
        SpotsC1.iloc[:, position] = SpotsC1.iloc[:,position].shift(movement)
        SpotsC2.iloc[:, position] = SpotsC2.iloc[:,position].shift(movement)
        SpotsC3.iloc[:, position] = SpotsC3.iloc[:,position].shift(movement)
        ColocC1vsC2.iloc[:, position] = ColocC1vsC2.iloc[:,position].shift(movement)
        ColocC1vsC3.iloc[:, position] = ColocC1vsC3.iloc[:,position].shift(movement)
        ColocC2vsC3.iloc[:, position] = ColocC2vsC3.iloc[:,position].shift(movement)
        Norm_to_EGF_ColC1_C3.iloc[:, position] = Norm_to_EGF_ColC1_C3.iloc[:,position].shift(movement)
        Norm_to_EGF_ColC2_C3.iloc[:, position] = Norm_to_EGF_ColC2_C3.iloc[:,position].shift(movement)
                
                

#
###df12 = df3.apply(f2)
plt.figure()
SpotsC1.mean(axis=1).plot(legend=True)
legend_points = ["Channel1"]
plt.legend(legend_points)


plt.figure()
SpotsC2.mean(axis=1).plot()
legend_points = ["Channel2"]
plt.legend(legend_points)

plt.figure()
SpotsC3.mean(axis=1).plot()
legend_points = ["Channel3"]
plt.legend(legend_points)

#
plt.figure()
ColocC1vsC2.mean(axis=1).plot()
legend_points = ["Coloc C1 vs C2"]
plt.legend(legend_points)

plt.figure()
ColocC1vsC3.mean(axis=1).plot()
legend_points = ["Coloc C1 vs C3"]
plt.legend(legend_points)


plt.figure()
ColocC2vsC3.mean(axis=1).plot()
legend_points = ["Coloc C2 vs C3"]
plt.legend(legend_points)

plt.figure()
Norm_to_EGF_ColC1_C3.plot()
legend_points = ["Single Experiments normC1C3"]
plt.legend(legend_points)



plt.figure()
Norm_to_EGF_ColC2_C3.plot()
legend_points = ["Single Experiments normC2C3"]
plt.legend(legend_points)


plt.figure()
SpotsC1.mean(axis=1).plot()
SpotsC2.mean(axis=1).plot()
SpotsC3.mean(axis=1).plot()
legend_points = ["Channel1" ,"Channel2", "Channel3"]
plt.legend(legend_points)
legend_points = ["Channel1"]
save_plot = datapath + "/Plots/plot1.png"
plt.savefig(save_plot)

plt.figure()

ColocC1vsC2.mean(axis=1).plot()
ColocC1vsC3.mean(axis=1).plot()
ColocC2vsC3.mean(axis=1).plot()
legend_points = ["Coloc C1 vs C2" ,"Coloc C1 vs C3", "Coloc C2 vs C3"]
plt.legend(legend_points)
save_plot = datapath + "/Plots/plot2.png"
plt.savefig(save_plot)

plt.figure()
Norm_to_EGF_ColC1_C3.mean(axis=1).plot()
Norm_to_EGF_ColC2_C3.mean(axis=1).plot()
legend_points = ["Norm. Coloc C1 vs C3" ,"Norm. Coloc C2 vs C3"]
plt.legend(legend_points)
save_plot = datapath + "/Plots/plot3.png"
plt.savefig(save_plot)





ColumnNames = []

for file in files:
    ColumnNames.append(os.path.basename(file))

print ColumnNames

SpotsC1.columns = ColumnNames
SpotsC2.columns = ColumnNames
SpotsC3.columns = ColumnNames
ColocC1vsC2.columns = ColumnNames
ColocC1vsC3.columns = ColumnNames
ColocC2vsC3.columns = ColumnNames
Norm_to_EGF_ColC1_C3.columns = ColumnNames
Norm_to_EGF_ColC2_C3.columns = ColumnNames
    
#print "Analysed tracks: " + str(len(df6.columns))

save_excel = datapath +"/excel/" + "Spots_"+splits[0]+ ".xls"
#print save_excel
SpotsC1.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Spots_"+splits[1]+ ".xls"
#print save_excel
SpotsC2.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Spots_"+splits[2]+ ".xls"
#print save_excel
SpotsC3.to_excel(save_excel)


save_excel = datapath +"/excel/" + "Coloc_"+splits[0]+"_vs_"+splits[1]+".xls"
#print save_excel
ColocC1vsC2.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Coloc_"+splits[0]+"_vs_"+splits[2]+".xls"
ColocC1vsC3.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Coloc_"+splits[1]+"_vs_"+splits[2]+".xls"
ColocC2vsC3.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Norm_EGF_Coloc_"+splits[0]+"_vs_"+splits[2]+".xls"
Norm_to_EGF_ColC1_C3.to_excel(save_excel)

save_excel = datapath +"/excel/" + "Norm_EGF_Coloc_"+splits[1]+"_vs_"+splits[2]+".xls"
Norm_to_EGF_ColC2_C3.to_excel(save_excel)



#save_excel = datapath +"/excel/" + splits[1]+ ".xls"
#print save_excel
#df6[:60].apply(normalisation).to_excel(save_excel)

