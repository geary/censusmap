# -*- coding: utf-8 -*-

import json
from optparse import OptionParser
import psycopg2


def columnExists( table, column ):
	cursor.execute('''
		SELECT
			attname
		FROM
			pg_attribute
		WHERE
			attrelid = (
				SELECT oid FROM pg_class WHERE relname = '%(table)s'
			) AND attname = '%(column)s'
		;
	''' % {
		'table': table,
		'column': column,
	})
	return cursor.fetchone() is not None


def process():
	
	cursor.execute('''
		SELECT
			ST_AsGeoJSON( ST_Centroid( ST_Extent( %(geometry)s ) ), 0 ),
			ST_AsGeoJSON( ST_Extent( %(geometry)s ), 0, 1 )
		FROM 
			%(table)s
		;
	''' % {
		'table': opt.table,
		'geometry': opt.geometry,
	})
	( extentcentroidjson, extentjson ) = cursor.fetchone()
	extentcentroid = json.loads( extentcentroidjson )
	extent = json.loads( extentjson )
	
	cursor.execute('''
		SELECT
			geoid10, namelsad10,
			intptlat10, intptlon10, 
			ST_AsGeoJSON( ST_Centroid( %(geometry)s ), 0, 1 ),
			ST_AsGeoJSON( %(geometry)s, 0, 1 )
		FROM 
			%(table)s
		WHERE
			aland10 > 0
		;
	''' % {
		'table': opt.table,
		'geometry': opt.geometry,
	})
	features = []
	for fips, name, lat, lng, centroidjson, geomjson in cursor.fetchall():
		geometry = json.loads( geomjson )
		centroid = json.loads( centroidjson )
		features.append({
			'type': 'Feature',
			'bbox': geometry['bbox'],
			'properties': {
				'kind': 'TODO',
				'fips': fips,
				'name': name,
				'center': 'TODO',
				'centroid': centroid['coordinates'],
			},
			'geometry': geometry,
		})
		del geometry['bbox']
	featurecollection = {
		'type': 'FeatureCollection',
		'crs': {
			'type': 'name',
			'properties': {
				'name': 'urn:ogc:def:crs:EPSG::3857'
			},
		},
		'properties': {
			'kind': 'TODO',
			'fips': 'TODO',
			'name': 'TODO',
			'center': 'TODO',
			'centroid': extentcentroid['coordinates'],
		},
		'bbox': extent['bbox'],
		'features': features,
	}
	fcjson = json.dumps( featurecollection )
	file( '../web/test/geotest.json', 'wb' ).write( fcjson )


def main():
	global connection, cursor
	connection = psycopg2.connect(
		host = opt.hostname,
		database = opt.database,
		user = opt.username,
		password = opt.password
	)
	cursor = connection.cursor()
	process()
	connection.close()


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
		'-g', '--geometry',
		action='store', type='string', dest='geometry',
		help='Geometry column name'
	)
	global opt, args
	( opt, args ) = parser.parse_args()
	

if __name__ == "__main__":
	options()
	main()
