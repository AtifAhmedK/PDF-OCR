# import the necessary packages
from sklearn.cluster import AgglomerativeClustering
from pytesseract import Output
from tabulate import tabulate
from PIL import Image, ImageTk, ImageDraw, ImageOps
from tkinter import Tk, Canvas
from tkinter import messagebox
from pdf2image import convert_from_path
import pandas as pd
import numpy as np
import pytesseract
import argparse
import imutils
import cv2
import sys, fitz  # import the bindings

global coordinates_list
global cropped_image
global results
coordinates_list=[]


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
#ap.add_argument("-o", "--output", required=True,
	#help="path to output CSV file")
ap.add_argument("-c", "--min-conf", type=int, default=0,
	help="minimum confidence value to filter weak text detection")
ap.add_argument("-d", "--dist-thresh", type=float, default=25.0,
	help="distance threshold cutoff for clustering")
ap.add_argument("-s", "--min-size", type=int, default=2,
	help="minimum cluster size (i.e., # of entries in column)")
args = vars(ap.parse_args())


fname = args["image"]  # get filename from command line
doc = fitz.open(fname)  # open document
for page in doc:  # iterate through the pages
	pix = page.get_pixmap()  # render page to an image
	pix.save("page-%i.png" % page.number)  # store image as a PNG
image = cv2.imread("page-0.png")

#gets the coordinates of the bounding rectangle of ROI
def get_coor(e):
	global x,y
	x=e.x
	y=e.y
	coordinates_list.append(x)
	coordinates_list.append(y)
	print("Pointer is currently at %d, %d" %(x,y))
	print (len(coordinates_list))
	if(len(coordinates_list)==4):
		canvas.unbind("<Button-1>")
		create_rec(coordinates_list[0], coordinates_list[1], coordinates_list[2], coordinates_list[3])
		return 

#draws a rectangle at the marked ROI
def create_rec(x1,y1,x2,y2):
	messagebox.showinfo("","bounding rectangle selected successfully, press OK to continue")
	canvas.create_rectangle(x1,y1,x2,y2, outline='black')
	crop_img(coordinates_list[0], coordinates_list[1], coordinates_list[2], coordinates_list[3],image)
	return

#crops the ROI from the whole image, performs OCR, saves the results
def crop_img(x1,y1,x2,y2,img):
	dimensions=(x1,y1,x2,y2)
	img = Image.fromarray(img)
	cropped_image=img.crop(dimensions)
	cropped_image.show()
	cropped_image=ImageOps.grayscale(cropped_image)
	cropped_image=cv2.resize((np.asarray(cropped_image)), None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)
	kernel = np.ones((2, 2), np.uint8)
	cropped_image = cv2.dilate(cropped_image, kernel, iterations=1)
	(Image.fromarray(cropped_image)).show()
	options = "--psm 6"
	pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
	results = pytesseract.image_to_data(cropped_image,config=options,output_type=Output.DICT)
	print(results['text'])
	with open("results.txt", 'w') as f:
		for word in results['text']:
			word = word + "\n"
			f.write(word)
	return


#main TK window
win = Tk()
# Define the geometry of the window
win.geometry("1000x1000")

#img=Image.open('sample7.jpg')

show_img=ImageTk.PhotoImage(Image.fromarray(image))
canvas=Canvas(win, height=5000, width=5000)
canvas.pack()
canvas.create_image(0,0,image = show_img, anchor="nw")
messagebox.showinfo("","Select the two points of the bounding rectangle(top-left & bottom right corners)")
canvas.bind("<Button-1>",get_coor)
win.mainloop()
