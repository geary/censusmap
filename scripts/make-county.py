# -*- coding: utf-8 -*-

import pg


def process():
	target = 'county'
	level = ''
	for source in ( 'bg', 'tabblock' ):
	#for source in ( 'bg' ):
		for state in ( '34', '36' ):
		#for state in ( '34', ):
			sourceTable = pg.censusTableName( '10', state, source )
			sourceGeom = 'the_geom'
			targetTable = pg.censusTableName( '10', state, target )
			targetGeom = 'the_geom_land_' + source
			#db.indexGeometryColumn( sourceTable, sourceGeom )
			db.addCountyLandGeometry( sourceTable, sourceGeom, targetTable, targetGeom )
			#db.addGoogleGeometry( sourceTable, sourceGeom, sourceGoogGeom )
			#db.addGoogleGeometry( targetTable, targetGeom, targetGoogGeom )


def main():
	global db
	db = pg.Database( database='census' )
	process()
	db.connection.close()
	print 'Done!'
	

if __name__ == "__main__":
	main()
