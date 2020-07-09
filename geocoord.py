# Classification:  UNCLASSIFIED
###############################################################
# Title:  (U) Geodetic Coordinate Parser
# Source:  (U) Dimitry Dukhovny
# Version:  (U) 20100519.1756
# 
# Purpose:  (U) Module for coordinate manipulation (more later)
# Contact me on with any comments, requests, or mockery.
# Constants shamelessly stolen from a PERL standard script that
#  I lost

import os
import re
import string
import mgrs2geo

def DEBUG(*args):
	print "\nDEBUG:  " + str(args)

def CONSOLE(*args):
	print "\nGEOCOORD:  " + str(args)

class geodetic:
	def __init__(self,coord='0.00000N/0.00000E',coordtype=''):
		## (U) coordtype can be MGRS, DMS, DM, or DD; DD is our goal; MGRS is unusable for now
		self.input=coord
		self.coordtype=coordtype
		self.muddled=0
		## (U) keeping these as public attributes in case debugging becomes necessary
		self.lat='0'
		self.latmin='0'
		self.latsec='0'
		self.lathem=''
		self.long='0'
		self.longmin='0'
		self.longsec='0'
		self.longhem=''
		self.ddlat='0.00000'
		self.ddlong='0.00000'
		self.dd=''

		coord=coord.replace('-',' ')

		while (not re.search('(?i)^[0-9nsew]',coord)): coord=coord[1:]
		while (not re.search('(?i)[0-9nsew]$',coord)): coord=coord[:-1]

		## (U) set hemispheres -- and probable break points
		lathemIndex=re.search('(?i)[ns]',coord)
		longhemIndex=re.search('(?i)[ew]',coord)
		if lathemIndex==None:  self.lathem='N'
		else:
			lathemIndex=lathemIndex.start()
			self.lathem=coord[lathemIndex]
		if longhemIndex==None:  self.longhem='E'
		else:
			longhemIndex=longhemIndex.start()
			self.longhem=coord[longhemIndex]

		## (U) hem-coord or coord-hem format?
		if lathemIndex==None:
			coordIterator=re.finditer('(\d){1,}(\.(\d){1,}){0,1}',coord)
			latitude=coordIterator.next().group()
			longitude=coordIterator.next().group()
		if lathemIndex>0:
			latitude=coord[:lathemIndex]
			longitude=coord[lathemIndex+1+re.search('\d',coord[lathemIndex+1:]).start():longhemIndex]
		if lathemIndex==0:
			latitude=coord[1:longhemIndex]
			longitude=coord[longhemIndex+1:]

		## (U) remove extra characters from latitude and longitude
		for samplechar in latitude:
			if (not re.search('[0-9\.]',samplechar)): latitude=latitude.replace(samplechar,' ')
		for samplechar in longitude:
			if (not re.search('[0-9\.]',samplechar)): longitude=longitude.replace(samplechar,' ')

		self.lat, self.latmin, self.latsec = self.assignvals(string.split(latitude))
		self.long, self.longmin, self.longsec = self.assignvals(string.split(longitude))

		self.sanitycheck()

		## (U) begin grueling guesswork
		if self.muddled:
			if (re.search('^(\d\.|\d\d\.)',latitude)):
				self.coordtype='DD'
				self.ddlat=latitude
				self.ddlong=longitude
			else:
				if (re.search('^(\d){6,7}',latitude)):
					self.coordtype='DMS'
					self.lat=latitude[:-4]
					self.latmin=latitude[-4:-2]
					self.latsec=latitude[-2:]
					self.long=longitude[:-4]
					self.longmin=longitude[-4:-2]
					self.longsec=longitude[-2:]
				else:
					if (re.search('^(\d){4,5}',latitude)):
						self.coordtype='DM'
						latitude=string.split(latitude,'.')
						self.lat=latitude[0][:-2]
						self.latmin=latitude[0][-2:]
						if (len(latitude)>1):  self.latmin=self.latmin+'.'+latitude[1]
						longitude=string.split(longitude,'.')
						self.long=longitude[0][:-2]
						self.longmin=longitude[0][-2:]
						if (len(longitude)>1):  self.longmin=self.longmin+'.'+longitude[1]
			self.muddled=0

		if ((self.coordtype=='DMS') or (self.coordtype=='DM')):
			ilat=string.atof(self.lat)
			ilatmin=string.atof(self.latmin)
			ilatsec=string.atof(self.latsec)
			ilong=string.atof(self.long)
			ilongmin=string.atof(self.longmin)
			ilongsec=string.atof(self.longsec)
			self.ddlat = str(round(((ilatmin*60 + ilatsec)/3600 + ilat),5))
			self.ddlong = str(round(((ilongmin*60 + ilongsec)/3600 + ilong),5))
		elif (self.coordtype=='DD'):
			self.ddlat = self.lat
			self.ddlong = self.long

		## (U) admit failure by leaving self.dd equal to self.input
		self.sanitycheck()
		if self.muddled:  self.dd=coord.replace(' ','')
		self.ddformat()
		self.dmformat()
		self.dmsformat()

	def sanitycheck(self):
		if self.coordtype=='':  self.muddled=1
		if abs(string.atof(self.lat))>180:  self.muddled=1
		if abs(string.atof(self.latmin))>60:  self.muddled=1
		if abs(string.atof(self.latsec))>60:  self.muddled=1
		if abs(string.atof(self.long))>180:  self.muddled=1
		if abs(string.atof(self.longmin))>60:  self.muddled=1
		if abs(string.atof(self.longsec))>60:  self.muddled=1

	def assignvals(self, valList):
		## (U) assign values based on the spacing
		coordinate=0
		coordinateMin=0
		coordinateSec=0
		if len(valList) >= 1:
			self.coordtype='DD'
			coordinate=valList[0]
		if len(valList) >= 2:
			self.coordtype='DM'
			coordinateMin=valList[1]
		if len(valList) == 3:
			self.coordtype='DMS'
			coordinateSec=valList[2]
		if len(valList) > 3:
			self.coordtype=''
			CONSOLE('WARNING:  possibly invalid coordinates ' + self.input + ' -- guessing from ' + str(valList))
			self.muddled=1
		return(coordinate,coordinateMin,coordinateSec)

	def ddformat(self, separator=None):
		## (U) sets the self.dd attribute to a list (e.g. [ 'latN', 'longE' ])
		## (U) ...or, with a specified separator (e.g. 'latN/longE')
		if separator:
			self.dd = self.ddlat + separator + self.ddlong
		else:
			self.dd = [ self.ddlat, self.ddlong ]

	def dmformat(self, separator=None):
		latFloat = string.atof(self.ddlat)
		longFloat = string.atof(self.ddlong)
		latMin = 60.0 * (latFloat - int(latFloat))
		longMin = 60.0 * (longFloat - int(longFloat))
		if separator:
			self.dm = str(int(latFloat)) + ' ' + str(round(latMin,5)) + self.lathem + separator + str(int(longFloat)) + ' ' + str(round(longMin,5)) + self.longhem
		else:
			self.dm = [ str(int(latFloat)) + ' ' + str(round(latMin,5)) + self.lathem, str(int(longFloat)) + ' ' + str(round(longMin,5)) + self.longhem ]

	def dmsformat(self, separator=None):
		latFloat = string.atof(self.ddlat)
		longFloat = string.atof(self.ddlong)
		latMin = 60.0 * (latFloat - int(latFloat))
		longMin = 60.0 * (longFloat - int(longFloat))
		latSec = 60 * (latMin - int(latMin))
		longSec = 60 * (longMin - int(longMin))
		if separator:
			self.dms = str(int(latFloat)) + ' ' + str(int(latMin)) + ' ' + str(round(latSec,5)) + self.lathem + separator + str(int(longFloat)) + ' ' + str(int(longMin)) + ' ' + str(round(longSec,5)) + self.longhem
		else:
			self.dms = [ str(int(latFloat)) + ' ' + str(int(latMin)) + ' ' + str(round(latSec,5)) + self.lathem, str(int(longFloat)) + ' ' + str(int(longMin)) + ' ' + str(round(longSec,5)) + self.longhem ]

## (U) convert from MGRS to DD
def mgrs2dd(coordinates):
	latlongreply = [0, 0]
	latlongreply[0], latlongreply[1] = mgrs2geo.mgrs2geo(coordinates)
	if (latlongreply[0] >= 0):  latlongreply[0]=str(latlongreply[0])+'N'
	elif (latlongreply[0] < 0):  latlongreply[0]=str(latlongreply[0])+'S'
	if (latlongreply[1] >= 0):  latlongreply[1]=str(latlongreply[1])+'E'
	elif (latlongreply[1] < 0):  latlongreply[1]=str(latlongreply[1])+'W'
	return(string.join(latlongreply,'/'))

def main():
	import sys
	if (len(sys.argv) <= 1):
		inputcoordinates = string.strip(str(raw_input('Enter coordinate string:  ')))
	else:  inputcoordinates = string.join(sys.argv[1:])
	mgrstest = inputcoordinates.replace(' ','').replace('-','')
	if re.search('\d\d([A-Za-z]){3}(\d\d){2,6}', mgrstest):  inputcoordinates=mgrs2dd(mgrstest)
	inputcoordinates = geodetic(inputcoordinates)
	inputcoordinates.ddformat('/')
	inputcoordinates.dmformat('/')
	inputcoordinates.dmsformat('/')
	print 'DD format:  ' + inputcoordinates.dd
	print 'DM format:  ' + inputcoordinates.dm
	print 'DMS format:  ' + inputcoordinates.dms

if __name__=='__main__':  main()

###############################################################
# Classification:  UNCLASSIFIED
