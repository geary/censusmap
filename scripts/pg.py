# -*- coding: utf-8 -*-

import json, os, os.path, shutil, tempfile, time
import psycopg2
from zipfile import ZipFile

import private


def censusTableName( year, fips, kind ):
	return 'tl_2010_%s_%s%s' %( fips, kind, year )


class Database:
	
	def __init__( self, **kw ):
		self.database = kw.get( 'database' )
		self.connection = psycopg2.connect(
			host = kw.get( 'host', 'localhost' ),
			port = kw.get( 'port', '5432' ),
			database = self.database,
			user = kw.get( 'user', private.POSTGRES_USERNAME ),
			password = kw.get( 'password', private.POSTGRES_PASSWORD ),
		)
		self.cursor = self.connection.cursor()
	
	def loadShapeZip( self, zipfile, tablename ):
		zipname = os.path.basename( zipfile )
		basename = os.path.splitext( zipname )[0]
		shpname = basename + '.shp'
		sqlname = basename + '.sql'
		unzipdir = tempfile.mkdtemp()
		print 'Unzipping %s' % zipname
		ZipFile( zipfile, 'r' ).extractall( unzipdir )
		shpfile = os.path.join( unzipdir, shpname )
		sqlfile = os.path.join( unzipdir, sqlname )
		t1 = time.clock()
		print 'Running shp2pgsql'
		os.system(
			'shp2pgsql %s %s %s >%s' %(
				shpfile, tablename, self.database, sqlfile
			)
		)
		t2 = time.clock()
		print 'shp2pgsql %.1f seconds' %( t2 - t1 )
		print 'Running psql'
		os.system(
			'psql -q -U postgres -d census -f %s' %(
				sqlfile
			)
		)
		t3 = time.clock()
		print 'psql %.1f seconds' %( t3 - t2 )
		shutil.rmtree( unzipdir )
		print 'loadShapeZip done'
	
	def getSRID( self, table, column ):
		self.cursor.execute('''
			SELECT Find_SRID( 'public', '%(table)s', '%(column)s');
		''' % {
			'table': table,
			'column': column,
		})
		return self.cursor.fetchone()[0]
	
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
	
	def addGeometryColumn( self, table, geom, srid=-1, always=False ):
		print 'addGeometryColumn %s %s' %( table, geom )
		t1 = time.clock()
		vars = { 'table':table, 'geom':geom, 'srid':srid, }
		if self.columnExists( table, geom ):
			if not always:
				return
			self.cursor.execute('''
				ALTER TABLE %(table)s DROP COLUMN %(geom)s;
			''' % vars )
		self.cursor.execute('''
			SELECT
				AddGeometryColumn(
					'public', '%(table)s', '%(geom)s',
					%(srid)d, 'MULTIPOLYGON', 2
				);
		''' % vars )
		self.connection.commit()
		t2 = time.clock()
		print 'addGeometryColumn %.1f seconds' %( t2 - t1 )
	
	def indexGeometryColumn( self, table, geom, index=None ):
		index = index or ( 'idx_' + geom )
		print 'indexGeometryColumn %s %s %s' %( table, geom, index )
		vars = { 'table':table, 'geom':geom, 'index':index, }
		t1 = time.clock()
		self.cursor.execute('''
			CREATE INDEX %(index)s ON %(table)s
			USING GIST ( %(geom)s );
		''' % vars )
		self.connection.commit()
		t2 = time.clock()
		print 'CREATE INDEX %.1f seconds' %( t2 - t1 )
		self.analyzeTable( table )
	
	def analyzeTable( self, table ):
		print 'analyzeTable %s' %( table )
		t1 = time.clock()
		isolation_level = self.connection.isolation_level
		self.connection.set_isolation_level(
			psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
		)
		self.cursor.execute('''
			VACUUM ANALYZE %(table)s;
		''' % { 'table':table } )
		self.connection.set_isolation_level( isolation_level )
		t2 = time.clock()
		print 'VACUUM ANALYZE %.1f seconds' %( t2 - t1 )
	
	def addGoogleGeometry( self, table, llgeom, googeom ):
		print 'addGoogleGeometry %s %s %s' %( table, llgeom, googeom )
		self.addGeometryColumn( table, googeom, 3857, True )
		t1 = time.clock()
		self.cursor.execute('''
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
			'llgeom': llgeom,
			'googeom': googeom,
		})
		self.connection.commit()
		t2 = time.clock()
		print 'UPDATE ST_Transform %.1f seconds' %( t2 - t1 )
	
	def addCountyLandGeometry( self,
		sourceTable, sourceGeom,
		countyTable, countyGeom
	):
		print 'addCountyLandGeometry %s %s %s %s' %(
			sourceTable, sourceGeom, countyTable, countyGeom
		)
		self.addGeometryColumn( countyTable, countyGeom, -1, True )
		t1 = time.clock()
		self.cursor.execute('''
			UPDATE
				%(countyTable)s
			SET
				%(countyGeom)s = (
					SELECT
						ST_Multi( ST_Union( %(sourceGeom)s ) )
					FROM
						%(sourceTable)s
					WHERE
						%(countyTable)s.countyfp10 = %(sourceTable)s.countyfp10
						AND
						aland10 > 0
					GROUP BY
						countyfp10
				);
			
			SELECT Populate_Geometry_Columns();
		''' % {
			'sourceTable': sourceTable,
			'sourceGeom': sourceGeom,
			'countyTable': countyTable,
			'countyGeom': countyGeom,
		})
		self.connection.commit()
		t2 = time.clock()
		print 'UPDATE ST_Union %.1f seconds' %( t2 - t1 )
	
	def makeGeoJSON( self, filename, table, geom, level ):
		
		srid = self.getSRID( table, geom )
		digits = [ 0, 6 ][ srid == -1 ]  # integer only if google projection
		
		## Temp filter for NYC test
		#filter = '''
		#	(
		#		countyfp10 = '005' OR
		#		countyfp10 = '047' OR
		#		countyfp10 = '061' OR
		#		countyfp10 = '081' OR
		#		countyfp10 = '085'
		#	)
		#'''
		
		## Test for the simplify error
		#filter = '''
		#	(
		#		geoid10 = '360050504000'
		#	)
		#'''
		
		# Don't filter
		filter = ''
		
		t1 = time.clock()
		self.cursor.execute('''
			SELECT
				ST_AsGeoJSON( ST_Centroid( ST_Extent( %(geom)s ) ), %(digits)s ),
				ST_AsGeoJSON( ST_Extent( %(geom)s ), %(digits)s, 1 )
			FROM 
				%(table)s
			--WHERE
			--	%(filter)s
			;
		''' % {
			'table': table,
			'geom': geom,
			'filter': filter,
			'digits': digits,
		})
		( extentcentroidjson, extentjson ) = self.cursor.fetchone()
		extentcentroid = json.loads( extentcentroidjson )
		extent = json.loads( extentjson )
		t2 = time.clock()
		print 'ST_Extent %.1f seconds' %( t2 - t1 )
		
		self.cursor.execute('''
			SELECT
				geoid10, namelsad10,
				intptlat10, intptlon10, 
				ST_AsGeoJSON( ST_Centroid( %(geom)s ), %(digits)s, 1 ),
				ST_AsGeoJSON( %(geom)s%(level)s, %(digits)s, 1 )
			FROM 
				%(table)s
			WHERE
				aland10 > 0
				-- AND %(filter)s
			;
		''' % {
			'table': table,
			'geom': geom,
			'level': level or '',
			'filter': filter,
			'digits': digits,
		})
		t3 = time.clock()
		print 'SELECT rows %.1f seconds' %( t3 - t2 )
		
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
		if srid != -1:
			featurecollection['crs'] = {
				'type': 'name',
				'properties': {
					'name': 'urn:ogc:def:crs:EPSG::%d' % srid
				},
			}
		t4 = time.clock()
		print 'Make featurecollection %.1f seconds' %( t4 - t3 )
		fcjson = json.dumps( featurecollection )
		file( filename, 'wb' ).write( fcjson )
		t5 = time.clock()
		print 'Write JSON %.1f seconds' %( t5 - t4 )


if __name__ == "__main__":
	pass  # TODO?
