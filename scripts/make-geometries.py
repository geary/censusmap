# -*- coding: utf-8 -*-

import pg

import runspec


def process():
	level = ''
	#for state in ( '34', '36' ):
	for state in ( '06', ):
		for run in runspec.runs:
			( source, sourceGeom, target, targetGeom ) = run
			sourceTable = pg.censusTableName( '10', state, source )
			targetTable = pg.censusTableName( '10', state, target )
			#db.indexGeometryColumn( sourceTable, sourceGeom )
			db.addLandGeometry(
				sourceTable, sourceGeom,
				targetTable, targetGeom,
				runspec.idColumns[target]
			)
			
			
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
