# -*- coding: utf-8 -*-

import json
import psycopg2


def censusTableName( year, fips, kind ):
	return 'tl_2010_%s_%s%s' %( fips, kind, year )


class Database:
	
	def __init__( self, **kw ):
		self.connection = psycopg2.connect(
			host = kw.get( 'host', 'localhost' ),
			port = kw.get( 'port', 5432 ),
			database = kw.get( 'database' ),
			user = kw.get( 'user', 'postgis' ),
			password = kw.get( 'password', '' )
		)
		self.cursor = self.connection.cursor()
	
	def columnExists( self, table, column ):
		self.cursor.execute('''
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
		return self.cursor.fetchone() is not None
	
	def addGoogleGeometry( self, table, llgeom, googeom ):
		if self.columnExists( table, googeom ):
			return
		self.cursor.execute('''
			SELECT
				AddGeometryColumn(
					'public', '%(table)s', '%(googeom)s', 3857, 'MULTIPOLYGON', 2
				)
			;
			UPDATE
				%(table)s
			SET
				%(googeom)s = ST_Transform(
					ST_SetSRID( %(llgeom)s, 4269 ),
					3857
				)
			;
		''' % {
			'table': table,
			'googeom': googeom,
			'llgeom': llgeom,
		})
		self.connection.commit()
	
	def makeGeoJSON( self, table, level ):
		
		# Temp filter for NYC test
		filter = '''
			(
				countyfp10 = '005' OR
				countyfp10 = '047' OR
				countyfp10 = '061' OR
				countyfp10 = '081' OR
				countyfp10 = '085'
			)
		'''
		
		self.cursor.execute('''
			SELECT
				ST_AsGeoJSON( ST_Centroid( ST_Extent( goog_geom ) ), 0 ),
				ST_AsGeoJSON( ST_Extent( goog_geom ), 0, 1 )
			FROM 
				%(table)s
			WHERE
				%(filter)s
			;
		''' % {
			'table': table,
			'filter': filter,
		})
		( extentcentroidjson, extentjson ) = self.cursor.fetchone()
		extentcentroid = json.loads( extentcentroidjson )
		extent = json.loads( extentjson )
		
		self.cursor.execute('''
			SELECT
				geoid10, namelsad10,
				intptlat10, intptlon10, 
				ST_AsGeoJSON( ST_Centroid( goog_geom ), 0, 1 ),
				ST_AsGeoJSON( goog_geom%(level)s, 0, 1 )
			FROM 
				%(table)s
			WHERE
				%(filter)s
				AND aland10 > 0
			;
		''' % {
			'table': table,
			'level': level or '',
			'filter': filter,
		})
		features = []
		for fips, name, lat, lng, centroidjson, geomjson in self.cursor.fetchall():
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
		filename = '../web/test/%s-%s.json' %( table, level or '0' )
		file( filename, 'wb' ).write( fcjson )


if __name__ == "__main__":
	pass  # TODO?
