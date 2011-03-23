# -*- coding: utf-8 -*-

import pg

state = '36'
kind = 'county'
table = pg.censusTableName( '10', state, kind )

source = 'blockgroup'
geom = 'the_geom_land'
googGeom = 'goog_geom_land'


def process():
	#db.addGoogleGeometry( table, geom, googGeom )
	#for level in ( '', '10', '100', '1000', '10000' ):
	#	db.makeGeoJSON( opt.table, level )
	filename = '../web/test/%s-%s%s.json' %( table, source, level )
	db.makeGeoJSON( filename, table, googGeom, '' )


def main():
	global db
	db = pg.Database( database = 'census' )
	process()
	db.connection.close()


if __name__ == "__main__":
	main()
