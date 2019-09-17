#!/usr/bin/env python3

from sys import argv
import numpy as np
from pathlib import Path
import cv2

def open_txt_np(filename):
    array = np.loadtxt(filename, delimiter = ",", skiprows = 1, dtype = "uint16")
    return array

def save_image(array, filename):
    max_array = np.max(array)
    array = array * (255/max_array)
    array = array.astype("uint8")
    print(filename)
    f = Path(filename)
    f = f.with_suffix(".tif")
    f = f.name
    f = "{} - {}".format(max_array, f)
    cv2.imwrite(f, array)

if __name__ == "__main__":
    filename = argv[1]
    array = open_txt_np(filename)
    save_image(array, filename)
    
