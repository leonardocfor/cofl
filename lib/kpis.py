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

######################################

### Imports from software modules
from cofl.etc.info import LOG_STD
from cofl.etc.eSO6DataFields import SEGMENT_FUEL, SEGMENT_LENGTH
from cofl.lib.logging import logger
######################################

###############################################################################################################################
###############################################################################################################################

def computeFuel(trajectory):

	"""
	Computing eSo6 Trajectory fuel [Kg]
	"""
	fuel = 0.0
	for segment in trajectory: fuel+=float(segment[SEGMENT_FUEL])
	return fuel

def computeKd(myLogFile,rankMsg,trajectory,cruiseLine,descentLine):

	fuelCruise = 0.0
	distanceCruise = 0.0
	for i in range(cruiseLine,descentLine+1):
		fuelCruise+=float(trajectory[i][SEGMENT_FUEL])
		distanceCruise+=float(trajectory[i][SEGMENT_LENGTH])
	Kd = fuelCruise / distanceCruise
	logger(myLogFile,rankMsg,LOG_STD,'Cruise fuel [Kg]: '+str(fuelCruise))
	logger(myLogFile,rankMsg,LOG_STD,'Cruise distance [NM]: '+str(distanceCruise))
	logger(myLogFile,rankMsg,LOG_STD,'Distance constant [Kg/NM): '+str(Kd))
	return Kd

###############################################################################################################################
###############################################################################################################################
