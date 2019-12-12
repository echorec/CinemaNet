import os 
import csv   
import argparse
import PIL.Image
import PIL.ImageOps
import numpy as np
import random
import math
import time


parser = argparse.ArgumentParser(description='Create an RGB Dominant color data set from downloaded Color Palette Cinema images')
parser.add_argument('-i', '--inputdir', type=str, help="input folder containing unmodified color pallete cinema images", required=True)
parser.add_argument('-o', '--outputdir', type=str, help='output folder containining cropped color palette cinema images and a CSV data set of RGB tuples ordered by luminance',required=True)

args = parser.parse_args()

start = time.time()

dir_path = os.getcwd()

input_path = os.path.normpath( os.path.join(dir_path, args.inputdir) )

print('Loading input images from: ' + input_path)

input_files = os.listdir(input_path)
input_files.sort()


# our output CSV data, of image file name, r1, b1, g1, r2, b2, g2, etc 
csv_rows = []

for filename in input_files:
	if filename.endswith('.jpg'):	

		image_path = (os.path.join(input_path, filename))

		#load image with PIL
		image = PIL.Image.open(image_path)

		rgb_im = image.convert('RGB')

		#our array of pixels to introspect is the palette colors
		width, height = rgb_im.size

		coords = []

		ycoord = height * 0.85 
		width_stride = float(width) / float(10)

		for i in range(10):
			xcoord = (width_stride * i) + 60
			coords.append( [ xcoord, ycoord])

		# coords = [ [1020, 710], 
		# 			[910, 710],
		# 			[800, 710],
		# 			[690, 710],
		# 			[580, 710],
		# 			[480, 710],
		# 			[380, 710],
		# 			[270, 710],
		# 			[160, 710],
		# 			[60,  710],
		# 			]

		# print coords

		rgb_arrays = []
		for coord in coords:
			r, g, b = rgb_im.getpixel((coord[0], coord[1]))

			rgb_arrays.append([r, g, b])

		#convert our 10 RGB pixels to LAB, and then sort them by L
		def sort_lab(a, b):

			l1 = math.sqrt( math.pow(0.299 * a[0], 2) + math.pow(0.587 * a[1], 2) + math.pow(0.114 * a[2], 2) )
			l2 = math.sqrt( math.pow(0.299 * b[0], 2) + math.pow(0.587 * b[1], 2) + math.pow(0.114 * b[2], 2) )
	
			if l1 > l2:
				return 1
			else:
				return -1

		#sort with our custum RGB LAB lambda
		rgb_arrays.sort(sort_lab)

		# print rgb_arrays

		csv_row = []
		csv_row.append(filename)
		for rgb_array in rgb_arrays:
			csv_row.append(rgb_array[0] / 255.0)
			csv_row.append(rgb_array[1] / 255.0)
			csv_row.append(rgb_array[2] / 255.0)

		csv_rows.append(csv_row)

		# crop our image
		# area = (11, 11, 1071, 600)
		# cropped_img = rgb_im.crop(area)


		# palette image is ~25% the height of the original
		crop_bottom = height * 0.26;
		crop_top = height * 0.012
		crop_left = width * 0.012
		crop_right = width * 0.012

		border = (crop_left, crop_top, crop_right, crop_bottom) # left, up, right, bottom
		cropped_img = PIL.ImageOps.crop(rgb_im, border)

		output_location = (os.path.join(args.outputdir, filename))

		cropped_img.save(output_location, "JPEG", quality=100, optimize=True, progressive=True)

print csv_rows

output_csv = os.path.join(args.outputdir, "color_dominant.csv")

with open(output_csv,  mode='w') as file:
		csv_writer = csv.writer(file)

		csv_writer.writerow(["image", "r0", "g0", "b0", "r1", "g1", "b1", "r2", "g2", "b2", "r3", "g3", "b3", "r4", "g4", "b4", "r5", "g5", "b5", "r6", "g6", "b6", "r7", "g7", "b7", "r8", "g8", "b8", "r9", "g9", "b9"])
		for csv_row in csv_rows:
			print  csv_row
			csv_writer.writerow(csv_row)

		file.close()

end = time.time()

processingtime = end - start

print("Completed Processing")
print("Took " + str(processingtime) + " seconds")

