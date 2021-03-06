# -*- coding: utf-8 -*-
"""Convert an SVG file to a GDSII file
"""

import sys
#import numpy as np
from gdsCAD import *
import xml.etree.ElementTree as ET

global height

def main(fileName, sizeOfTheCell, outName):
    """Convert an SVG file (fileName) to a GDSII file
    """
    print("Convert an SVG file to a GDSII file.")
    # Read an SVG file
    svgxml_tree = ET.parse(fileName)
    root = svgxml_tree.getroot()

    global height
    width = float(root.attrib['width'][:-2])
    height = float(root.attrib['height'][:-2])

    # Fetch namespaces (xmlns:)
    svg_namespaces = dict([node for _, node in ET.iterparse(fileName, events=['start-ns'])])

    # Fetch all layers (assuming top g's are layers)
    layers = root.findall('svg:g', svg_namespaces)

    pathcells = []
    for layerNum, layer in enumerate(layers):
        # Add all paths 
        for pathNum, path in enumerate(layer.iter('{'+svg_namespaces['svg']+'}path')):
            newcell = core.Cell('L{}-p{}'.format(layerNum, pathNum))
            pathToCell(newcell, path, layerNum)
            pathcells.append(newcell)
        # Add all circles (as disks)
        for circNum, circle in enumerate(layer.iter('{'+svg_namespaces['svg']+'}circle')):
            newcell = core.Cell('L{}-disk{}'.format(layerNum, circNum))
            circleToCell(newcell, circle, layerNum)
            pathcells.append(newcell)
        print('Layer {} done.'.format(layerNum))

    # TODO: Implement routines for Circle/Disk, Ellipse, Box/Rectangle 

    top = core.Cell("TOP")
    top.add(pathcells)

    # Add the top-cell to a layout and save
    layout = core.Layout("LAYOUT")
    layout.add(top)
    layout.save(outName)

def pathToCell(cell, path, layerNum):

    print('Adding path to cell')
    pathid = path.attrib['id']
    print(pathid)
    directions = path.attrib['d'].split()
    
    # Small sanity check. Currently, only straight, continuous lines are supported.
    curved_segments = ['c','s','q','t','a']
    curved_segments += [c.upper() for c in curved_segments]
    if any(x in directions for x in curved_segments):
        print('ERROR: Curved lines in path {} not supported. Skipping.'.format(pathid))
        return
    if 'm' in directions[1:] or 'M' in directions[1:]:
        print('ERROR: Discontinuous paths in path {} not supported. Skipping.'.format(pathid))
        return

    # Hardcoded conversion of straight lines, can be more sophisticated.
    x, y = map(float, directions[1].split(','))
    points = [(x,y)]
    vertmove, horizmove, absmove = False, False, False
    for d in directions[2:]:
        if d.isupper():
            absmove = True
        elif d.islower():
            absmove = False
        if d.lower() == 'l':
            vertmove, horizmove = False, False
            continue
        elif d.lower() == 'v': 
            vertmove, horizmove = True, False
            continue
        elif d.lower() == 'h':
            vertmove, horizmove = False, True
            continue
        elif d.lower() == 'z':
            break

        if not vertmove and not horizmove: 
            dx, dy = map(float, d.split(','))
            x, y = (not absmove)*x+dx, (not absmove)*y+dy
        elif vertmove: 
            dy = float(d)
            y = (not absmove)*y+dy
        else:
            dx = float(d)
            x = (not absmove)*x+dx
        points.append((x,y))
        #print('x:',x,'y:',y)

    # Flip ys in order to adhere to Inkscape coordinate system
    global height
    points_flip_y = [(x,height-y) for (x,y) in points]
    boundary = core.Boundary(points_flip_y, layer=layerNum)
    cell.add(boundary)

def circleToCell(cell, circle, layerNum):
    # Technically a filled circle is a disk in GDSII
    print('Adding circle to cell')
    circleid = circle.attrib['id']
    print(circleid)
    cx = float(circle.attrib['cx'])
    cy = float(circle.attrib['cy'])
    r = float(circle.attrib['r'])

    # Flip y in order to adhere to Inkscape coordinate system
    global height
    cy_flip = height-cy

    disk = shapes.Disk((cx,cy_flip), r, layer=layerNum)
    cell.add(disk)

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