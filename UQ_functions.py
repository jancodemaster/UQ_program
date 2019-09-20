#!/usr/bin/env python3

#imports
from sys import argv
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import txt_tobitmap

#functions
def balanced_hist_thresholding(b):#source: https://theailearner.com/tag/image-thresholding/
    """
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

def load_image(filename):
    filename = Path(filename)
    if filename.suffix in [".tif", ".tiff", ".png", ".jpeg", ".jpg"]:
        image = cv2.imread(filename.as_posix(), 0)
        name = filename.name
        return image, name, None
    elif filename.suffix in [".txt"]:
        #convert txt to tif
        array = txt_tobitmap.open_txt_np(filename)
        max_array = np.max(array)
        img = array * (255/max_array)
        img = img.astype("uint8")
        name = filename.name
        return img, name, array
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
    files = [str(x) for x in dirname.iterdir() if not x.is_dir()]#was x for x
    return files

def mask_from_threshold(imgname, th_value):
    img, name, _ = load_image(imgname)
    _, th1 = cv2.threshold(img, th_value, 255, cv2.THRESH_BINARY)
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask, con

def mask_from_k(kfile):
    img, name, _ = load_image(kfile)
    b1 = create_hist(img)
    thresh_value = balanced_hist_thresholding(b1)
    _, th1 = cv2.threshold(img, thresh_value, 255, cv2.THRESH_BINARY)
    con = contouring(th1)
    binary_mask = create_mask(img, con)
    return binary_mask, con

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
    if len(splits) == 2:
        plantname = splits[0]
        el = splits[1]
    elif len(splits) == 3:
        plantname = splits[1]
        el = splits[2]
    return plantname, el

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

def group_plants_files(files):
    """Function to group plants based on name.
    
    This function creates a dictionary which has key: plantname without element
    and values a list of all plants with that name.
    Example key:smallplant, value:[smallplant K.tiff, smallplant Ca.tiff]
    returns: plantdict - a dictionary with key:plantname, value: list of plant paths
    """
    plantdict = {}
    pathfiles = string_to_paths(files)
    for f in pathfiles:
        plantname, _ = plantname_from_filename(f)
        update_dict(plantdict, plantname, str(f))
    return plantdict

def get_mask(th_mode, th_manual, cur_path, files):
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
    for f in working_files:
        fp = Path(f)
        temp = fp.with_suffix('')
        name = temp.name
        if name.endswith("{}".format(th_mode)):
            return f
    return "Element not found"

def create_mask_dict(masks):
    #create a dict which has {key:"name" , value: mask}
    maskdict = {}
    for (path, mask) in masks:
        plantname, el = plantname_from_filename(path)
        maskdict[plantname] = mask
    return maskdict

def is_valid_filename(filename):#
    f = Path(filename)
    if f.suffix == ".tif":
        name = f.name
        if " - " in name:
            splits = name.split(" - ")
            if len(splits) == 2:
                return True
            else:
                return False
        else:
            return False
    elif f.suffix == ".txt":
        name = f.name
        if " - " in name:
            splits = name.split(" - ")
            if len(splits) == 2:
                return True
            else:
                return False
    else:
        return False

def calc_shape(filename):
    img, _, _ = load_image(filename)
    return np.shape(img)

def get_contour_precedence(contour, cols):#maybe change tolerance factor based on input image.
    tolerance_factor = 50
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]

def area_contours(contours, filepaths):
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
    #files = load_images_directory(argv[1])
    print(is_valid_filename(argv[1]))
    #group_plants_files(files)
    
