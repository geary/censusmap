# -*- coding: utf-8 -*-

import pg

state = '36'
kind = 'county'
table = pg.censusTableName( '10', state, kind )

geom = 'the_geom_land'
googGeom = 'goog_geom_land'


def process():
	db.addGoogleGeometry( table, geom, googGeom )
	#for level in ( '', '10', '100', '1000', '10000' ):
	#	db.makeGeoJSON( opt.table, level )
	db.makeGeoJSON( table, googGeom, '' )


def main():
	global db
	db = pg.Database( database = 'census' )
	process()
	db.connection.close()


if __name__ == "__main__":
	main()
