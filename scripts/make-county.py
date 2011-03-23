# -*- coding: utf-8 -*-

import pg

state = '36'
bgTable = pg.censusTableName( '10', state, 'bg' )
countyTable = pg.censusTableName( '10', state, 'county' )

bgGeom = 'the_geom'
bgGoogGeom = 'goog_geom'

countyGeom = 'the_geom_land'
countyGoogGeom = 'goog_geom_land'

def process():
	db.addCountyLandGeometry( bgTable, bgGeom, countyTable, countyGeom )
	db.addGoogleGeometry( bgTable, bgGeom, bgGoogGeom )
	db.addGoogleGeometry( countyTable, countyGeom, countyGoogGeom )


def main():
	global db
	db = pg.Database( database='census' )
	process()
	db.connection.close()
	

if __name__ == "__main__":
	main()
