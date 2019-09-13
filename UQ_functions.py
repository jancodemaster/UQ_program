#!/usr/bin/env python3

from sys import argv
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import os




def balanced_hist_thresholding(b):#source: https://theailearner.com/tag/image-thresholding/
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
#TODO kies de threshold op de eerste plek waar het histogram weer omhoog gaat. Voor donkere plaatjes.
def load_image(filename):
    filename = Path(filename)
    #print(filename)
    if filename.suffix in [".tif", ".tiff", ".png", ".jpeg", ".jpg"]:
        image = cv2.imread(filename.as_posix(), 0)
        name = filename.name
        return image, name
    else:
        print("Select an image file!")
        exit(0)

def contouring(img):
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
    binary_mask = np.zeros(np.shape(img), dtype=np.uint8)
    cv2.drawContours(binary_mask, contours, -1, (255,255,255), -1)
    return binary_mask

def create_hist(img):
    b1 = plt.hist(img.ravel(),256,[0,256])
    return b1

def load_images_directory(dirname):
    dirname = Path(dirname)
    files = [x for x in dirname.iterdir() if not x.is_dir()]
    return files

def load_images_directory_as_string(dirname):#TODO remove os
    files = []
    for f in os.listdir(dirname):
        files.append(os.path.join(dirname, f))
    return files

def mask_from_threshold(imgname, th_value):
    img, name = load_image(imgname)
    _, th1 = cv2.threshold(img, th_value, 255, cv2.THRESH_BINARY)
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask

def mask_from_k(kfile):
    img, name = load_image(kfile)
    b1 = create_hist(img)
    thresh_value = balanced_hist_thresholding(b1)
    _, th1 = cv2.threshold(img, thresh_value, 255, cv2.THRESH_BINARY)
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask

def el_files_from_files(files, el = "K"):#default K
    elements = ["K", "Ca", "Fe", "Zn", "Se"]#not recommended with Fe, Zn, Se
    if el in elements:
        el_files = []
        for f in files:
            temp = f.with_suffix('')
            name = temp.name
            if name.endswith("{}".format(el)):
                el_files.append(f)
        return el_files
    else:
        print("Element not supported")
        exit(0)

def names_dict_from_filenames(f_list, dic):
    """This function createa a dictionary with key:plantname, 
    
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
    pathname = Path(pathname)
    return pathname.name

def plantname_from_filename(f):#f must be a Path(f)
    #assumes name is always <plantname> - <el>.tif
    f = Path(f)
    f = f.with_suffix('')
    name = f.name
    splits = name.split(" - ")#pathsdfk/plantnaam - El.tif
    plantname = splits[0]
    el = splits[1]
    return plantname, el

def path_name_to_file_name(string_path_name):
    f = Path(string_path_name)
    print(f.name)
    return f.name

def calc_area_using_mask(mask):#counts the area of the total masks
    return int(np.sum(mask)/255) # all black pixels are 255 instead of 1

def string_to_paths(files):
    path_files = []
    for f in files:
        f = Path(f)
        path_files.append(f)
    return path_files

def calc_area_element(img):#not precise unless a txt file with actual counts is loaded
    """Function to calculate total color value of an image.
    
    This will essentially give a relative value of the total element in this picture.
    Returns: An int with the sum of all values in the image.
    """
    return int(np.sum(img))

def execute():
    files = load_images_directory(argv[1])#final version gets a list of strings containing paths
    el_files = el_files_from_files(files)
    masks = []
    for f in el_files:
        mask = mask_from_k(f)
        entry = (f, mask)
        masks.append(entry)
    
    maskdict = create_mask_dict(masks)
    for f in files:#loops over all files and applies mask
        plantname, el = plantname_from_filename(f)
        mask = maskdict[plantname]
        (image, name) = load_image(f)
        plant = cv2.bitwise_and(image, mask)
        amount_el = calc_area_element(plant)
        print("Area of {} in pixels: {}".format(plantname, calc_area_using_mask(mask)))
        print("Amount of {} in relative counts: {}".format(el, amount_el))
        
        #cv2.namedWindow("plantwithmask_{}".format(name), cv2.WINDOW_NORMAL)
        #cv2.imshow("plantwithmask_{}".format(name), plant)
        #cv2.waitKey()

def get_mask(th_mode, th_manual, files):
    pathfiles = string_to_paths(files)
    masks = []
    if th_mode =="Manual":
        for f in pathfiles:
            mask = mask_from_threshold(f, th_manual)
            entry = (f, mask)
            masks.append(entry)
        maskdict = create_mask_dict(masks)
        return maskdict
    else:
        el_files = el_files_from_files(pathfiles, th_mode )
        for f in el_files:
            mask = mask_from_k(f)
            entry = (f, mask)
            masks.append(entry)
        maskdict = create_mask_dict(masks)
        return maskdict

def get_single_mask(th_mode, th_manual, f):
    f = Path(f)
    if th_mode == "Manual":
        mask = mask_from_threshold(f, th_manual)
        return mask
    else:
        el_files = el_files_from_files([f], th_mode)
        for ff in el_files:
            mask = mask_from_k(ff)
            return mask

def create_mask_dict(masks):
    #create a dict which has {key:"name" , value: mask}
    maskdict = {}
    for (path, mask) in masks:
        plantname, el = plantname_from_filename(path)
        maskdict[plantname] = mask
    return maskdict

if __name__ == "__main__":
    #files = load_images_directory_as_string(argv[1])
    execute()
    #maskdict = get_mask("Manual", 30, files)
    #print(maskdict)
    #binary_mask = mask_from_k(kfile)
    #filename = argv[1]
    #img, name = load_image(filename)
    #b1 = plt.hist(img.ravel(),256,[0,256])
    #b1 = create_hist(img)
    #thresh_value = balanced_hist_thresholding(b1)
    
    #ret,th1 = cv2.threshold(img,thresh_value ,255,cv2.THRESH_BINARY)
    
    #cv2.namedWindow("histthreshhold", cv2.WINDOW_NORMAL)
    #cv2.imshow("histthreshhold", th1)
    #cv2.waitKey()
    
    #con = contouring(th1)
    
    
    #cv2.drawContours(img, con, -1, (255, 255, 255), -1)
    #cv2.namedWindow("con", cv2.WINDOW_NORMAL)
    #cv2.imshow("con", img)
    #cv2.waitKey()
    
    #_, binary_mask = cv2.threshold(copy_img, 254,255,cv2.THRESH_BINARY)
    #binary_mask = np.zeros(np.shape(img))
    #cv2.drawContours(binary_mask, con, -1, (255,255,255), -1)
    #cv2.namedWindow("mask", cv2.WINDOW_NORMAL)
    #cv2.imshow("mask", binary_mask)
    #cv2.waitKey()
    """
    blur = cv2.GaussianBlur(th1,(5,5),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    blur2 = cv2.GaussianBlur(th3,(15,15),0)
    b2 = plt.hist(blur2.ravel(),256,[0,256])
    thresh_value2 = balanced_hist_thresholding(b2)
    ret,th4 = cv2.threshold(blur2,thresh_value2 ,255,cv2.THRESH_BINARY)
    ret5,th5 = cv2.threshold(th4,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    large_contours = contouring(th5)
    
    cv2.drawContours(copy_img, large_contours, -1, (255, 255, 255), -1)
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, copy_img)
    cv2.waitKey()
    cv2.destroyAllWindows()
"""
