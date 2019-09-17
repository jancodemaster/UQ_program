#!/usr/bin/env python3

from sys import argv
import numpy as np
from PIL import Image

def open_file(filename):
    f = open(filename, "r")
    lines = f.readlines()
    header = lines[0]
    content = []
    for i in range(1, len(lines)-1):#last line is ['']
        line = lines[i].strip("\n")
        line = line.split(",")
        content.append(line)
    f.close()
    return header, content

def get_2d_array(header, content):
    headsplits = header.split()
    el = headsplits[0].strip(":")
    x = int(headsplits[1])
    y = int(headsplits[3])
    points = np.array(content).astype(float)
    max_array = np.max(points)
    points = points * (255/max_array)
    #points = points.astype(int)
    print(np.max(points))
    image = Image.fromarray(points)
    image = image.convert("RGB")
    #image.show()
    
    image.save("test.tif")

if __name__ == "__main__":
    filename = argv[1]
    header, content = open_file(filename)
    get_2d_array(header, content)
    
