#!/usr/bin/python

import private

from StringIO import StringIO

from generate_tiles import render_tiles
#from generate_tiles_multiprocess import render_tiles

mapfile = 'poly-test.xml'

#mapfile = StringIO(
#	file(mapfile).read()
#)

# CONUS
bbox = ( -124.728, 24.546, -66.952, 49.383 )

render_tiles( bbox, mapfile, private.TILE_PATH, 0, 4, 'Lower 48', 1 )
