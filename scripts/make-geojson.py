# -*- coding: utf-8 -*-

import pg, private, runspec

def process():
	level = ''
	for state in ( '06', '34', '36', ):
		for run in runspec.runs:
			( source, sourceGeom, target, targetGeom ) = run
			table = pg.censusTableName( '10', state, target )
			boxGeom = 'the_geom'
			#db.addGoogleGeometry( table, geom, googGeom )
			#for level in ( '', '10', '100', '1000', '10000' ):
			#	db.makeGeoJSON( opt.table, level )
			#filename = '../web/test/%s-%s.json' %( table, targetGeom )
			filename = '%s/%s-%s.json' %(
				private.GEOJSON_PATH, table, targetGeom
			)
			db.makeGeoJSON( filename, table, boxGeom, targetGeom, '' )


def main():
	global db
	db = pg.Database( database = 'census' )
	process()
	db.connection.close()


if __name__ == "__main__":
	main()
