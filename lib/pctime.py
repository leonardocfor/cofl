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
from datetime import datetime
from calendar import timegm
from time import gmtime, strptime
from timeit import default_timer

######################################

### Imports from software modules
from cofl.etc.info import YEAR_PREFIX, TIME_ZONE
from cofl.etc.eSO6DataFields import SEGMENT_DATE_INIT, SEGMENT_DATE_END, SEGMENT_TIME_INIT, SEGMENT_TIME_END
######################################

###############################################################################################################################
###############################################################################################################################

def calculateInitAndEndTime(trajectoriesFolder, size, flightsQ):

	"""
	Calculate init and end time of simulation
	"""
	initTimes=[]
	endTimes=[]
	for rank in range(1,size):
		trajFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(flightsQ)))+'.eSo6'
		firstLine=os.popen('head -1 '+trajFile).read().split()
		endLine=os.popen('tail -1 '+trajFile).read().split()
		## Init time seconds from EPOCH
		initTimes.append(calculateSecFromEpoch(firstLine[SEGMENT_DATE_INIT],firstLine[SEGMENT_TIME_INIT]))
		## End time seconds from EPOCH
		endTimes.append(calculateSecFromEpoch(endLine[SEGMENT_DATE_END],endLine[SEGMENT_TIME_END]))

	initTime=min(initTimes)
	endTime=max(endTimes)
	return initTime, endTime

def calculateSecFromEpoch(date,hour):

	"""
	Calculates seconds from EPOCH
	"""

	months={
		'01':'Jan',
		'02':'Feb',
		'03':'Mar',
		'04':'Apr',
		'05':'May',
		'06':'Jun',
		'07':'Jul',
		'08':'Aug',
		'09':'Sep',
		'10':'Oct',
		'11':'Nov',
		'12':'Dec'
	}
	year=YEAR_PREFIX+date[0:2]
	month=months[date[2:4]]
	day=date[4:6]
	hourF=hour[0:2]+':'+hour[2:4]+':'+hour[4:6]
	dateFormatted=month+' '+day+','+' '+year+' @ '+hourF+' '+TIME_ZONE
	secs=timegm(strptime(dateFormatted, '%b %d, %Y @ %H:%M:%S '+TIME_ZONE))
	return secs

def getComputingTime():

	"""
	Get computing time [s]
	"""
	return default_timer()

def getDateAndTime():

	"""
	Function to get the time in format: "%Y-%m-%d_%H-%M"
	"""
	return datetime.now().strftime('%Y-%m-%d @ %H:%M')

def getFormattedDate(date,hour):

	"""
	Get formatted date
	"""
	months={
		'01':'Jan',
		'02':'Feb',
		'03':'Mar',
		'04':'Apr',
		'05':'May',
		'06':'Jun',
		'07':'Jul',
		'08':'Aug',
		'09':'Sep',
		'10':'Oct',
		'11':'Nov',
		'12':'Dec'
	}
	year=YEAR_PREFIX+date[0:2]
	month=months[date[2:4]]
	day=date[4:6]
	hourF=hour[0:2]+':'+hour[2:4]+':'+hour[4:6]
	dateFormatted=month+' '+day+','+' '+year+' @ '+hourF
	return dateFormatted

def returnSeconds(initTime,endTime):

	"""
	Returns seconds with very small time periods
	Requires two datetimes
	"""
	duration = endTime - initTime
	seconds = duration.seconds
	microSeconds = duration.microseconds
	return seconds + 1e-6*microSeconds

def returnSecondsFromEpoch():

	"""
	Function to get seconds from the Epochs
	"""
	return timegm(gmtime())

###############################################################################################################################
###############################################################################################################################
