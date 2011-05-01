# -*- coding: utf-8 -*-

from optparse import OptionParser

import pg, private #, runspec


def process():
	#db.addGoogleGeometry( opt.table, opt.llgeom, opt.googeom )
	for level in ( '100000', '10000', '1000', '100' ):
		polyGeom = boxGeom = opt.googeom
		if level: polyGeom += '_' + level
		filename = '%s/%s-%s.json' %(
			private.GEOJSON_PATH, opt.table, polyGeom
		)
		db.makeGeoJSON( filename, opt.table, boxGeom, polyGeom )


def main():
	global db
	db = pg.Database(
		host = opt.hostname,
		database = opt.database,
		user = opt.username,
		password = opt.password
	)
	process()
	db.connection.close()


def options():
	parser = OptionParser()
	parser.add_option(
		'-H', '--hostname', dest='hostname',
		default='localhost',
		help='Database hostname'
	)
	parser.add_option(
		'-P', '--port', dest='port',
		default='5432',
		help='Database port'
	)
	parser.add_option(
		'-u', '--username', dest='username',
		default='postgres',
		help='Database username'
	)
	parser.add_option(
		'-p', '--password', dest='password',
		default='',
		help='Database password'
	)
	parser.add_option(
		'-d', '--database', dest='database',
		help='Database name'
	)
	parser.add_option(
		'-t', '--table', dest='table',
		help='Table name'
	)
	parser.add_option(
		'-g', '--googeom',
		action='store', type='string', dest='googeom',
		default='goog_geom',
		help='Google geometry column name'
	)
	parser.add_option(
		'-l', '--llgeom',
		action='store', type='string', dest='llgeom',
		default='full_geom',
		help='Latitude/Longitude geometry column name'
	)
	global opt, args
	( opt, args ) = parser.parse_args()
	

if __name__ == "__main__":
	options()
	main()
