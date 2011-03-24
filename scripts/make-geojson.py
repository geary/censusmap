# -*- coding: utf-8 -*-

import pg


def process():
	kind = 'county'
	level = ''
	for source in ( 'bg', 'tabblock' ):
		for state in ( '34', '36' ):
			table = pg.censusTableName( '10', state, kind )
			geom = 'the_geom_land_' + source
			#db.addGoogleGeometry( table, geom, googGeom )
			#for level in ( '', '10', '100', '1000', '10000' ):
			#	db.makeGeoJSON( opt.table, level )
			filename = '../web/test/%s-%s.json' %( table, source )
			db.makeGeoJSON( filename, table, geom, '' )


def main():
	global db
	db = pg.Database( database = 'census' )
	process()
	db.connection.close()


if __name__ == "__main__":
	main()
