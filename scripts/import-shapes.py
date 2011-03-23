# -*- coding: utf-8 -*-

import os.path
from zipfile import ZipFile

import pg

import private


year = '10'
state = '36'
kind = 'tabblock'
table = pg.censusTableName( year, state, kind )


def process():
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
