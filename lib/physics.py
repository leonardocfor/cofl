#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 © Copyright, UbiHPC
 All rights reserved
 Developped by Leonardo Camargo Forero, UbiHPC CEO
 email: lecf.77@gmail.com
 2019
 High Performance Robotic Computing Cooperative Flying (COFL) simulator
 This simulator is based on The ARCHADE SimPlat
 For more information write us in https://ubihpc.com/contact-us
"""

### imports ##########################

from geographiclib.geodesic import Geodesic
from math import ceil

######################################

### Imports from software modules
from cofl.etc.configuration import TRACKS_DIFFERENCE, M_TO_NM, NM_TO_M
######################################

###############################################################################################################################
###############################################################################################################################

def calculateDistanceBetweenPoints(lat1,lon1,lat2,lon2):

	"""
	Calculate distance between flights [meters]
	"""
	return Geodesic.WGS84.Inverse(lat1,lon1, lat2, lon2)['s12']

def calculateFFBox(qOfFlights):

	"""
	Flying formation box calculation
	"""
	# if qOfFlights == 2: rows=2; columns=1
	# else:
	pass

def calculateTrackBetweenFlights(lat1,lon1,lat2,lon2):

	"""
	Calculate track [degrees] between flights [degrees]
	"""
	return Geodesic.WGS84.Inverse(lat1,lon1, lat2, lon2)['azi1']

def checkTracks(track1,track2):

	"""
	Checking if tracks match
	"""
	matched=True if abs(track1-track2) <= TRACKS_DIFFERENCE else False
	return matched

def convertMtoNM(meters):

	return meters*M_TO_NM

def convertNMtoM(nautical_miles):

	return nautical_miles*NM_TO_M

def convertMinuteDecimalToDregrees(toconvert):

	"""
	Convert minute decimal to degrees
	"""
	converted=[]
	for toc in toconvert:
		converted.append(float(toc)/60)
	return converted

def getPoint(lat,lon,deg,dist):

	"""
	Returns the latitude and longitude of a point at a distance dist [m] with a degree deg from lat,lon
	"""
	point={}
	point['LAT'] = Geodesic.WGS84.Direct(lat,lon,deg,dist)['lat2']
	point['LON'] = Geodesic.WGS84.Direct(lat,lon,deg,dist)['lon2']
	return point

def roundUP(x):

	"""
	Rounding up to next 10th
	"""
	return int(ceil(x / 10.0)) * 10



###############################################################################################################################
###############################################################################################################################
