# -*- coding: utf-8 -*-
"""Convert an SVG file to a GDS file
"""

import sys
#import numpy as np
from gdsCAD import *
import xml.etree.ElementTree as ET

def main(fileName, sizeOfTheCell, outName):
    """Convert an SVG file (fileName) to a GDS file
    """
    print("Convert an SVG file to a GDS file.")
    # Read an SVG file
    svgxml_tree = ET.parse(fileName)
    root = svgxml_tree.getroot()

    width = root.attrib['width']
    height = root.attrib['height']

    print("width:{0}".format(width))
    print("height:{0}".format(height))

    # Fetch namespaces (xmlns:)
    svg_namespaces = dict([node for _, node in ET.iterparse(fileName, events=['start-ns'])])

    # Fetch all layers (assuming top g's are layers)
    layers = root.findall('svg:g', svg_namespaces)

    pathcells = []
    for layerNum, layer in enumerate(layers):
        # Add all paths 
        for pathNum, path in enumerate(layer.iter('{'+svg_namespaces['svg']+'}path')):
            newcell = core.Cell('L{}-p{}'.format(layerNum, pathNum))
            pathToCell(newcell, path)
            pathcells.append(newcell)
        print('Layer {} done.'.format(layerNum))

    top = core.Cell("TOP")
    top.add(pathcells)

    # Add the top-cell to a layout and save
    layout = core.Layout("LAYOUT")
    layout.add(top)
    layout.save(outName)

def pathToCell(cell, path):
    curved_segments = ['c','s','q','t','a']
    curved_segments += [c.upper() for c in curved_segments]

    print('Adding path to cell')
    print(path.attrib['id'])
    directions = path.attrib['d'].split()
    
    if any(x in directions for x in curved_segments):
        print('ERROR: Curved lines in path not supported. Skipping.')
        return
    for d in directions:
        print(d)
        # TODO: implement creation of boundary


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 4:
        fileName = args[1]
        sizeOfTheCell = args[2]
        outName = args[3]
        main(fileName, sizeOfTheCell, outName)
    else:
        print(
            "usage: python svg2GDS.py <fileName> <sizeOfTheCell[um]> <outName>")
        quit()