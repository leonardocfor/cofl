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

import itertools

######################################

### Imports from software modules
from cofl.etc.configuration import NM_TO_M
from cofl.etc.eSO6DataFields import SEGMENT_LAT_INIT, SEGMENT_LON_INIT, SEGMENT_LAT_END, SEGMENT_LON_END, SEGMENT_TRACK
from cofl.lib.physics import convertMinuteDecimalToDregrees, calculateDistanceBetweenPoints, checkTracks
######################################

###############################################################################################################################
###############################################################################################################################

def fifo(clusters, vehiclesPosition ,cruiseFlights, radius, currTime):

	"""
	This function computes clusters at a specific timestep
	The FIFO approach clusters the flights according to the first analyzed flight
	Flights already clustered are not considered
	"""

	setClusters=False
	clusteredFlights=[]
	radius = float(radius)*NM_TO_M

	### Checking for clusterizable flights
	for flight in cruiseFlights:

		if len(clusters[flight])==0: ## Checking for non-clustered flight
			if flight not in clusteredFlights:
				lat1I, lon1I, lat1E, lon1E=convertMinuteDecimalToDregrees(
						[
						vehiclesPosition[flight][SEGMENT_LAT_INIT],
						vehiclesPosition[flight][SEGMENT_LON_INIT],
						vehiclesPosition[flight][SEGMENT_LAT_END],
						vehiclesPosition[flight][SEGMENT_LON_END]
						])
				track1= float(vehiclesPosition[flight][SEGMENT_TRACK])
				for otherFlight in filter(lambda otherFlight: otherFlight!=flight, cruiseFlights):
					lat2I, lon2I, lat2E, lon2E = convertMinuteDecimalToDregrees(
							[
							vehiclesPosition[otherFlight][SEGMENT_LAT_INIT],
							vehiclesPosition[otherFlight][SEGMENT_LON_INIT],
							vehiclesPosition[otherFlight][SEGMENT_LAT_END],
							vehiclesPosition[otherFlight][SEGMENT_LON_END]
							])
					track2=float(vehiclesPosition[otherFlight][SEGMENT_TRACK])
					dF1F2=calculateDistanceBetweenPoints(lat1I,lon1I,lat2I,lon2I) ## Calculating if the flights are within a specified radius
					matchedTracks=checkTracks(track1,track2) ## Checking if the flights are in the same direction relatively
					if  dF1F2 <= radius and matchedTracks: ## Conditions for clustering
						if len(clusters[flight]) == 0: clusters[flight].append(flight)
						clusteredFlights.append(flight)
						clusters[flight].append(otherFlight)
						if len(clusters[otherFlight]) > 1:
							for f in clusters[otherFlight]:
								if f not in clusters[flight]: clusters[flight].append(f)
						clusteredFlights.append(otherFlight)
		else: clusteredFlights.append(flight)

	### Matching the clusters of all flights in the MASTER flight
	for flight in clusters:
		for otherFlight in filter(lambda otherFlight: otherFlight!=flight, clusters[flight]): clusters[otherFlight]=clusters[flight]
	for flight in clusters:
		if len(clusters[flight])>0: setClusters=True; break
	for flight in clusters: clusters[flight] = list(set(clusters[flight]))
	clusteredFlights=list(set(clusteredFlights))

	# checkedFlights = []
	# qOfClusters = 0
	# for flight in clusters:
	# 	if len(clusters[flight]) > 0 and flight not in checkedFlights:
	# 		qOfClusters+=1
	# 		for otherFlight in clusters[flight]: checkedFlights.append(otherFlight)


	return clusters, clusteredFlights, setClusters

###############################################################################################################################
###############################################################################################################################
