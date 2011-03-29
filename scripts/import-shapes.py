# -*- coding: utf-8 -*-

import os.path
from zipfile import ZipFile

import pg
import private
import states


year = '00'
kind = 'tabblock'


def process():
	for state in states.array:
		fips = state['fips']
		table = pg.censusTableName( year, state['fips'], kind )
		print 'Loading', fips, state['name']
		zipfile = os.path.join(
			private.SHAPEFILE_PATH, kind.upper(), '20' + year, table + '.zip'
		)
		db.loadShapeZip( zipfile, table )


def main():
	global db
	db = pg.Database( database='census' )
	process()
	db.connection.close()
	

if __name__ == "__main__":
	main()
