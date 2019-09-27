#!/usr/bin/env python3
"""Functions needed to run UQ_GUI_code.py

Author: Jan Aarts and Wieske de Swart
Email: yannickaarts96@gmail.com;wieskedeswart@gmail.com
"""
#imports
from sys import argv
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

#functions
def balanced_hist_thresholding(b):#source: https://theailearner.com/tag/image-thresholding/
    """Balanced histogram thresholding to automatically find a threshold.
    
    Input: b, a plt histogram
    Returns: i_m a integer value as threshold.
    """
    i_s = np.min(np.where(b[0]>0))
    i_e = np.max(np.where(b[0]>0))
    i_m = (i_s + i_e)//2
    w_l = np.sum(b[0][0:i_m+1])
    w_r = np.sum(b[0][i_m+1:i_e+1])
    while (i_s != i_e):
        if (w_r > w_l):
            w_r -= b[0][i_e]
            i_e -= 1
            if ((i_s+i_e)//2) < i_m:
                w_l -= b[0][i_m]
                w_r += b[0][i_m]
                i_m -= 1
        else:
            w_l -= b[0][i_s]
            i_s += 1
            if ((i_s+i_e)//2) >= i_m:
                w_l += b[0][i_m+1]
                w_r -= b[0][i_m+1]
                i_m += 1
    return i_m

def hist_thresholding(array):
    """Histogram thresholding which sets a threshold to filter the first peak in the histogram.
    
    Input: array, a numpy array of an image.
    Returns: th, a integer value with the threshold.
    """
    #vals, counts = np.unique(array, return_counts=True)
    hist, bins = np.histogram(array, bins=25)
    lastval = 0
    down = False
    th = None
    i = 0
    while th == None:
        curval = hist[i]
        if curval != 0:  
            if down == True:
                if curval > lastval:
                    th = bins[i]
            if curval < lastval:
                down = True
            lastval = curval
        i += 1
    return th

def load_image(filename):
    """Loads a image file from .tif or .txt/.csv
    
    Input: filename, a string containing the path to the image file.
    Returns: image, a cv image as numpy array
    Returns: name, the name of the image
    Returns: array, the actual array loaded from a .txt or .csv file. None if input is an image. 
    """
    filename = Path(filename)
    if filename.suffix in [".tif", ".tiff", ".png", ".jpeg", ".jpg"]:
        image = cv2.imread(filename.as_posix(), 0)
        name = filename.name
        return image, name, None
    elif filename.suffix in [".txt"]:
        #convert txt to tif
        array = np.loadtxt(filename, delimiter = ",", skiprows = 1, dtype = "uint16")
        max_array = np.max(array)
        img = array * (255/max_array)
        img = img.astype("uint8")
        name = filename.name
        return img, name, array
    elif filename.suffix in [".csv"]:
        array = np.loadtxt(filename, delimiter = ",", skiprows = 0, dtype = "uint16")
        max_array = np.max(array)
        img = array * (255/max_array)
        img = img.astype("uint8")
        name = filename.name
        return img, name, array
    else:
        print("Select an image file!")
        exit(0)

def contouring(img):
    """Use open-cv contouring to get contours of a binary image.
    
    This function calculates all contours but will return only the contours
    larger than 1 percent of the image to avoid noise.
    Input: img, a numpy array containing a binary image.
    Returns: large_contours, open-cv contours larger than 1 percent of the image.
    """
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = []
    x , y = np.shape(img)
    total_area = x * y
    for c in contours:
        if cv2.contourArea(c) > int(total_area * 0.01): #1 percent of total image
            large_contours.append(c)
    large_contours = np.array(large_contours)
    return large_contours

def create_mask(img, contours):
    """This function will create a mask based on the contours and the original image.
    
    Input: img, a numpy array with an image.
    Input: contours, open-cv contours.
    Returns: binary_mask, the contours drawn on a black image. Not actually binary since black is 0 and white is 255.
    """
    binary_mask = np.zeros(np.shape(img), dtype=np.uint8)
    cv2.drawContours(binary_mask, contours, -1, (255,255,255), -1)
    return binary_mask

def create_hist(img):
    """creates a pyplot histogram
    
    Input: img, a numpy array with an image.
    Returns: b1, a pyplot histogram.
    """
    b1 = plt.hist(img.ravel(),256,[0,256])
    return b1

def load_images_directory(dirname):
    """Loads all files in a directory.
    
    Input: dirname, a string containing the path to the directory.
    Returns: files, a list of string containing the paths of all files in the directory.
    """
    dirname = Path(dirname)
    files = [str(x) for x in dirname.iterdir() if not x.is_dir()]
    return files

def mask_from_threshold(imgname, th_value):
    """Creates a mask based on a threshold value.
    
    Input: imgname, the filename of an image.
    Input: th_value, an integer containing the threshold value.
    Returns: binary_mask, a numpy array with the white contours drawn on a black image.
    Returns: con, open-cv contours based on the threshold.
    """
    img, name, _ = load_image(imgname)
    _, th1 = cv2.threshold(img, th_value, 255, cv2.THRESH_BINARY)
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask, con

def mask_from_k(kfile):
    """Creates a mask from an element image.
    
    For example create a mask for all plants with name x based on x-K.txt
    K is generally a good element to create a mask from.
    
    Input: kfile, a string containing the path to a image file.
    Returns: binary_mask, a numpy array with the white contours drawn on a black image.
    Returns: con, open-cv contours based on the threshold.
    """
    img, name, _ = load_image(kfile)
    
    #b1 = create_hist(img)
    #thresh_value = balanced_hist_thresholding(b1)
    
    thresh_value = hist_thresholding(img)
    _, th1 = cv2.threshold(img, thresh_value, 255, cv2.THRESH_BINARY)
    
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask, con

def names_dict_from_filenames(f_list, dic):
    """This function creates a dictionary with key:plantname, value:element
    
    Input: f_list, a list of files to add to the dictionary.
    Input: dic, a dictionary with key:plantname, value:element or an empty dictionary.
    Returns: names, a list of names of the plants.
    Returns: dic, the updated or created dictionary.
    """
    names = []
    for f in f_list:
        fp = Path(f)
        fp = fp.with_suffix('')
        name = fp.name
        names.append(name)
        plant, el = plantname_from_filename(f)
        dic = update_dict(dic, plant, el)
    return names, dic

def update_dict(dic, key, value):
    """Updates a list in a dictionary
    
    This function updates a list in a dictionary or creates a new list with the value.
    Input: dic, the dictionary to be updated.
    Input: key, the key for the dictionary
    Input: value, the value given to the key.
    Returns the updated dictionary containing lists as values
    """
    if key in dic:
        oldvalue = dic[key]
        oldvalue.append(value)
        dic[key] = oldvalue
        return dic
    else:
        dic[key] = [value]
        return dic

def filename_from_pathname(pathname):
    """Extracts the file name from a whole path.
    
    Input: pathname, a string with a path name.
    Returns: pathname.name, the file name as a string.
    """
    pathname = Path(pathname)
    return pathname.name

def plantname_from_filename(f):
    """Extracts the plantname and element from a filename.
    
    The filename must be of format <plantname> - <element>.<suffix>
    Input:f, a string with a filename.
    Returns: plantname, a string with the plantname
    Returns: el, a string with the element for example "K" or "Zn"
    """
    f = Path(f)
    f = f.with_suffix('')
    name = f.name
    splits = name.split(" - ")
    if len(splits) == 2:
        plantname = splits[0]
        el = splits[1]
    elif len(splits) == 3:
        plantname = splits[1]
        el = splits[2]
    return plantname, el

def calc_area_using_mask(mask):
    """Calculates the area of the mask in pixels.
    
    Input: mask, a numpy array containing a mask.
    Returns: the sum of all pixels in the mask.
    """
    return int(np.sum(mask)/255) # all black pixels are 255 instead of 1

def string_to_paths(files):
    """Function to convert strings with a path to pathlib Paths.
    
    Input: files, a list of strings containing filenames.
    Returns: path_files, a list of Paths.
    """
    path_files = []
    for f in files:
        f = Path(f)
        path_files.append(f)
    return path_files

def calc_area_element(img):#not precise unless a txt file with actual counts is loaded
    """Function to calculate total color value of an image.
    
    This will essentially give a relative value of the total element in this picture.
    Input: img, a numpy array with an open-cv image
    Returns: An int with the sum of all values in the image.
    """
    return int(np.sum(img))

def group_plants_files(files):
    """Function to group plants based on name.
    
    This function creates a dictionary which has key: plantname without element
    and values a list of all plants with that name.
    Example key:smallplant, value:[smallplant K.tiff, smallplant Ca.tiff]
    Input: files, a list of plantfiles.
    returns: plantdict - a dictionary with key:plantname, value: list of plant paths
    """
    plantdict = {}
    pathfiles = string_to_paths(files)
    for f in pathfiles:
        plantname, _ = plantname_from_filename(f)
        update_dict(plantdict, plantname, str(f))
    return plantdict

def get_mask(th_mode, th_manual, cur_path, files):
    """Makes a mask from the current file based on the mode.
    
    Input:th_mode, either Manual or a selected element.
    Input:th_manual, if th_mode is Manual then this contains the threshold value as integer.
    Input:cur_path, a string with the path of the current file selected.
    Input:files, a list of all filepaths loaded.
    Returns: mask, the mask of the plant.
    Returns:con, the open-cv contours of the plant.
    """
    plantdict = group_plants_files(files)
    cur_path = Path(cur_path)
    curplantname, _ = plantname_from_filename(cur_path)
    working_files = plantdict[curplantname]
    if th_mode =="Manual":
        mask, con = mask_from_threshold(cur_path, th_manual)
        return mask, con
    else:
        el_file = get_el_file_from_working_files(working_files, th_mode)
        mask, con = mask_from_k(el_file)
        return mask, con
        
def get_el_file_from_working_files(working_files, th_mode):
    """Gets the needed element from all plant files.
    
    Input: working_files, a list of filenames of the selected plant.
    Input:th_mode, the required element.
    Returns: the file which contains the required element.
    """
    for f in working_files:
        fp = Path(f)
        temp = fp.with_suffix('')
        name = temp.name
        if name.endswith("{}".format(th_mode)):
            return f
    return "Element not found"

def create_mask_dict(masks):
    """Creates a dictionary with the mask for every plantname.
    
    Input: masks, all masks made from the selected files.
    Returns: maskdict, a dictionary with {key:"name" , value: mask}
    """
    maskdict = {}
    for (path, mask) in masks:
        plantname, el = plantname_from_filename(path)
        maskdict[plantname] = mask
    return maskdict

def is_valid_filename(filename):#
    """A check if the selected filename contains a valid image file.
    
    Input: filename, a string with the selected filename.
    Returns: True if the filename is valid, False otherwise.
    """
    f = Path(filename)
    if f.suffix in [".tif", ".txt", ".csv"]:
        name = f.name
        if " - " in name:
            splits = name.split(" - ")
            if len(splits) == 2:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def calc_shape(filename):
    """Gets the shape of the image belonging to the filepath.
    
    Input: filename, a string containing the path to an image file.
    Returns: np.shape(img), the np.shape of the given image file.
    """
    img, _, _ = load_image(filename)
    return np.shape(img)

def get_contour_precedence(contour, cols):#maybe change tolerance factor based on input image.
    """Tries to order the contours from left to right. Top to bottom.
    
    Tolerance factor can be different based on the image. 50 tested good in most images.
    Input: contour, an open-cv contour
    Input: cols, the columns of the shape of the image.
    Returns: the precedence of the contours.
    """
    tolerance_factor = 50
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]

def area_contours(contours, filepaths):
    """
    Calculated the area of each contours and gives them a number to order them.
    
    Input: contours, open-cv contours
    Input:filepaths, a list containing strings of image files.
    Returns: results, a list of tuples with (element, index, sum)
    Returns: img, the images with the drawn order on it.
    """
    results = []
    shape = calc_shape(filepaths[0])
    #sort contours on (x, y)
    contours = sorted(contours, key=lambda x:get_contour_precedence(x, shape[1]))
    
    for i in range(0, len(contours)):
        empty_mask = np.zeros(shape, dtype=np.uint8)
        cv2.drawContours(empty_mask, contours, i, (255,255,255), -1)
        for f in filepaths:
            img, name, array = load_image(f)
            #check if array is not None
            if array is not None:
                img = array
            plantname, el = plantname_from_filename(name)
            con_on_image = img * empty_mask
            total = calc_area_element(con_on_image)
            sum_real = int(total/255)
            entry = (el, i, sum_real)
            results.append(entry)


    #only if new picture is needed for frontend
    img = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(img, contours, -1, (255,255,255), -1)
    for i in range(0, len(contours)):
        img = cv2.putText(img, str(i),cv2.boundingRect(contours[i])[:2], cv2.FONT_HERSHEY_COMPLEX, 3, [125], 5)#cv2.boundingRect(contours[i])[:2]
    #cv2.namedWindow("drawn contours", cv2.WINDOW_NORMAL)
    #cv2.imshow("drawn contours", img)
    #cv2.waitKey()
    return results, img

#main
if __name__ == "__main__":
    filename = argv[1]
    img, _, _ = load_image(filename)
    hist = create_hist(img)
    #files = load_images_directory(argv[1])
    #group_plants_files(files)
    
