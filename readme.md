# svg2GDS

Convert an SVG file to a GDS file.

**Current status:** Only rudimentary implementation. SVG path objects are converted to GDSII boundaries. 

* Native shapes not supported (i.e., Circle/Disk, Ellipse, Box/Rectangle).
* Curved paths not supported. Reccommended procedure is to add nodes to curved segments and straighten all nodes when sufficient resolution is achieved.
* Absolute linemoves not supported.
* Discontinuous paths not supported (i.e., shapes with holes).

*But they might be supported in the future!*