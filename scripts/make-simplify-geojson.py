# -*- coding: utf-8 -*-

import pg, private, runspec


def process():
	kind = 'county'
	schema = 'c2010'
	table = 'c2010.' + kind
	fullGeom = 'full_geom'
	googGeom = 'goog_geom'
	boxGeom = googGeom
	tolerance = 100000
	simpleGeom = '%s_%d' %( googGeom, tolerance )
	
	#db.addGoogleGeometry( table, fullGeom, googGeom )
	db.simplifyGeometry( table, googGeom, simpleGeom, tolerance )
	
	filename = '%s/%s-%s.json' %(
		private.GEOJSON_PATH, table, simpleGeom
	)
	db.makeGeoJSON( filename, table, boxGeom, simpleGeom, '' )

def main():
	global db
	db = pg.Database( database = 'census' )
	process()
	db.connection.close()


if __name__ == "__main__":
	main()
