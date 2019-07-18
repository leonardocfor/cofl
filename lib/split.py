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

import os
import sys

######################################

### Imports from software modules
from cofl.etc.eSO6DataFields import ARRIVAL, DEPARTURE, FLIGHT_ID
######################################

###############################################################################################################################
###############################################################################################################################

def splitESO6File(rankMsg, eso6File, qOfFlights, trajectoriesFolder):

	"""
	Split eS06 Trajectories file
	198988435
	"""
	start=True
	try:
		rank = 1
		files=1
		currFlightID = os.popen('head -1 '+eso6File).read().split()[FLIGHT_ID]
		rankTrajectoryFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(qOfFlights)))+'.eSo6'
		print(rankMsg+' Creating rank flight file: '+rankTrajectoryFile.split('/')[-1])
		for line in open(eso6File):
			if line.split()[FLIGHT_ID] != currFlightID:
				rank+=1
				rankTrajectoryFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(qOfFlights)))+'.eSo6'
				print(rankMsg+' Creating rank fight file: '+rankTrajectoryFile.split('/')[-1])
				currFlightID=line.split()[FLIGHT_ID]
				files+=1
			rankFile=open(rankTrajectoryFile,'a')
			rankFile.write(line[0:-1]+'\n')
			rankFile.close()
			if str(files) == qOfFlights: break
	except Exception, e: raise
	return start, rank

def selectiveSplitESO6File(rankMsg, airport, departure, eso6File, qOfFlights, trajectoriesFolder):

	"""
	Split eS06 Trajectories file
	"""
	try:
		rank = 1
		nF=True
		airportType=DEPARTURE if departure  else ARRIVAL
		qOfFlights = int(qOfFlights)

		flightsLines =[]
		for line in open(eso6File):
			if airport in line.split()[airportType]: flightsLines.append(line)

		currFlightID=flightsLines[0].split()[FLIGHT_ID]
		rankTrajectoryFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(qOfFlights)))+'.eSo6'
		print(rankMsg+' Creating rank flight file: '+rankTrajectoryFile.split('/')[-1])

		for line in flightsLines:
			if line.split()[FLIGHT_ID] != currFlightID:
				currFlightID = line.split()[FLIGHT_ID]
				rank+=1
				if rank == qOfFlights+1: break
				rankTrajectoryFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(qOfFlights)))+'.eSo6'
				print(rankMsg+' Creating rank flight file: '+rankTrajectoryFile.split('/')[-1])
			rankFile=open(rankTrajectoryFile,'a')
			rankFile.write(line[0:-1]+'\n')
			rankFile.close()

	except Exception, e: raise

###############################################################################################################################
###############################################################################################################################
