#!/usr/bin/env python

import errno, os, re, sys, urllib
from ftplib import FTP
from zipfile import ZipFile

import private
from utility import chdirp, mkdirp


class Writer( object ):
	
	def __init__( self, filename, length ):
		self.file = open( filename, 'wb' )
		self.length = length
		self.done = 0
	
	def write( self, data ):
		self.done += len(data)
		sys.stdout.write( '%.1f%%\r' %( self.done * 100.0 / self.length ) )
		self.file.write( data )
	
	def close( self ):
		self.file.close()

class FtpGetter( object ):
	
	def __init__( self, host, ftpdir, localdir ):
		self.ftp = FTP( host )
		self.ftp.login()
		self.ftp.cwd( ftpdir )
		chdirp( localdir )
	
	def getdir( self, dir ):
		saveftpdir = self.ftp.pwd()
		self.ftp.cwd( dir )
		print '%s' % self.ftp.pwd()
		savelocaldir = os.getcwd()
		chdirp( dir )
		lines = []
		self.ftp.dir( lambda line: lines.append(line) )
		for line in lines:
			self._dirline( line )
		self.ftp.cwd( saveftpdir )
		os.chdir( savelocaldir )
	
	def getfile( self, name, length ):
		if re.search( '\d{5}', name ):
			return  # Ignore single-county files
		filename = name[:-4]
		shapefile = '%s/%s.shp' %( filename, filename )
		if not os.path.exists( name ):
			print 'Downloading %s/%s' %( self.ftp.pwd(), name )
			writer = Writer( name, length )
			result = self.ftp.retrbinary( 'RETR ' + name, writer.write )
			writer.close()
		if name.endswith('.zip'):
			if not os.path.exists( shapefile ):
				print 'Unzipping %s' % name
				mkdirp( filename )
				ZipFile( name, 'r' ).extractall( filename )
			print 'Loading table %s' % filename
			sqlfile = '%s.sql' % filename
			if not os.path.exists( sqlfile ):
				# TODO: use pipe or something better
				os.system( 'shp2pgsql %s %s census >%s' %( shapefile, filename, sqlfile ) )
				os.system( 'psql -q -U postgres -d census -f %s' %( sqlfile ) )
				os.remove( sqlfile )
	
	def _dirline( self, line ):
		parts = line.split()
		name = parts[-1]
		if parts[0][0] == 'd':
			self.getdir( name )
		else:
			self.getfile( name, int(parts[4]) )


def main():
	ftp = FtpGetter(
		'ftp2.census.gov', '/geo/tiger/TIGER2010',
		private.SHAPEFILE_PATH
	)
	ftp.getdir( 'STATE' )
	ftp.getdir( 'CD' )
	ftp.getdir( 'CONCITY' )
	ftp.getdir( 'COUNTY' )
	ftp.getdir( 'COUSUB' )
	ftp.getdir( 'PLACE' )
	ftp.getdir( 'TRACT' )
	ftp.getdir( 'BG' )
	#ftp.getdir( 'TABBLOCK' )
	print 'Done!'

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1] == '--go':  # for safety
		main()
