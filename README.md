##Analysis scripts for Wenzel et al, Nature Communications 2018, DOI:


#Individual Vesicle Tracking

Open movie in FIJI
Make RGB image and keep source image
Open ”MeasureTracks_Gallery.py” in FIJI
		roisize = 7
		GalleryROI = 15
		Pixelsize = 0.080
		framerate = 0.33
Use point tool to track one vesicle in the RGB image (Activate “auto next slice” and “add to ROI manager”)
ROIs will be added to the ROI manager
Activate original three channel movie and click on “run”
Results table: Mark everything (CTRL+a) and copy everything (CTRL+c)
Paste the values in an Excel sheet
Replace . for , in Excel and plot the normalized intensities
Save ROIs: Roi manager => More => Save




#Frame by frame analysis


Directory structure: See folder "Example Directory structure "


Open movie in FIJI
Open ”Colocalize_Spots.py” in FIJI
Find suitable threshold for spot segmentation: Testrun
=> Testrun: True 
=> show coloc: True
=> automatic save results: False
=> Enter correct path to save the analysis results later
Run
Check whether segmentation looks reasonable in all three channels (ch1: red, ch2: green, ch3: blue/EGF)
Too many spots => increase number in ”noise”
Too few spots => decrease number in ”noise”
Measuring: 
=> Testrun: False
=> show coloc: False
=> automatic save results: True
Activate movie file to be analyzed and click on ”run”
Check whether .csv is saved in correct ”Measurements” folder

Process measurements:
Open Python(x,y) => Run Spider
Open ”Process_Measurements.py”
Use shifting matrix to account for delays after EGF pulse 
Check whether Excel-files saved 

#Make grayscale images from Excel values:
Open ”Lists_to_tiff.py”
Insert numbers (save transposed values from Excel as .csv (comma delimited))
Change savename
Run
Open Tiff:
Edit => invert
Process => Filters => Gaussian Blur => 6
Adjust levels to 20 (min) and 80 (max)
