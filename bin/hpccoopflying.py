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
import getopt
from datetime import datetime
from math import cos, sin, radians, sqrt, pow
from mpi4py import MPI
from time import sleep

# sys.path.insert(0,'') Uncomment and insert COFL root directory if necessary

######################################

### Imports from software modules
from cofl.etc.configuration import  TIME_STEP
from cofl.etc.info import DATA_ROOT_FOLDER, TRAJ_FOLDER, HPC_TRAJ_FOLDER, OUTPUT_FOLDER, LOGS_FOLDER, LOG_STD, LOG_ERR
from cofl.etc.info import STATUS_TAG, TELEMETRY_TAG, NM_CLUSTERS_TAG, AC_SLAVES_TAG, CLUSTERED_TAG, APPROACHING_TAG, VICSEK_TAG, SIM_SUMARY_TAG
from cofl.etc.eSO6DataFields import *
from cofl.lib.conflicts import discoverConflicts
from cofl.lib.clustering import fifo
from cofl.lib.ioFiles import readInfrastructureFile, readESO6Trajectory, readXMLInput, wrapIT, writeResultsFile, writePerformanceFile
from cofl.lib.ioFiles import writeCooperativeFlightsFile, writeSummaryFile
from cofl.lib.folders import createFolders
from cofl.lib.formationFlying import formationFlying
from cofl.lib.info import usage
from cofl.lib.kpis import computeFuel, computeKd
from cofl.lib.logging import logger
from cofl.lib.network import addEdges, calculateGRC, calculateLRC, setNetwork
from cofl.lib.pctime import calculateInitAndEndTime, getComputingTime, getDateAndTime, getFormattedDate, returnSeconds, returnSecondsFromEpoch
from cofl.lib.performance import checkBandwidth, checkLatency, getBytes
from cofl.lib.physics import calculateDistanceBetweenPoints, getPoint, roundUP, convertMtoNM, convertNMtoM
######################################

######################################################################################################################################################
######################################################################################################################################################

def approachCluster(nextPositionHPC, currentCluster):
	"""
	Initial approaching to cluster neighbours
	"""
	inPosition = False
	joined = False
	clusterSize = len(currentCluster)
	response = informNodes(nextPositionHPC,currentCluster,APPROACHING_TAG)
	myLat = nextPositionHPC['LAT']
	myLon = nextPositionHPC['LON']
	maxSeparation = 0.0
	for flight in response:
		fLat = response[flight]['LAT']
		fLon = response[flight]['LON']
		dist = calculateDistanceBetweenPoints(myLat,myLon,fLat,fLon)
		if dist > maxSeparation: maxSeparation = dist
	if maxSeparation <= clusterSize*float(approachedDistance): inPosition = True ## Potential conflicts -- Needs addressing
	response = informNodes(inPosition,currentCluster,APPROACHING_TAG)
	if all(flightReady for flightReady in response.values()) and inPosition: joined = True
	logger(myLogFile,rankMsg,LOG_STD,'JOINED - '+str(joined).upper())
	return joined

def calculateCruise():

	"""
	Calculate climbing timestep
	"""
	global cruiseTime
	cruiseTime = myInitTime
	line=0
	for segment in originalTrajectory:

		flInit = int(segment[SEGMENT_LEVEL_INIT])
		flEnd = int(segment[SEGMENT_LEVEL_END])
		status = segment[STATUS]
		if flInit == flEnd  and status == '2':
			stop=True
			for i in range(1,4):
				flInitAux = int(originalTrajectory[line+i][SEGMENT_LEVEL_INIT])
				flEndAux = int(originalTrajectory[line+i][SEGMENT_LEVEL_END])
				statAux = originalTrajectory[line+i][STATUS]
				if flInitAux == flEndAux  and statAux == '2': pass
				else: stop = False; break
			if stop: break
		else: cruiseTime+= TIME_STEP
		line+=1

	cruiseTime+= TIME_STEP
	logger(myLogFile,rankMsg,LOG_STD,'Cruise starts at time '+str(cruiseTime)+' [s]')
	return line

def calculateDescent():

	"""
	Calculate descent timestep
	"""
	global descentTime
	global tod
	descentTime = myEndTime
	line = len(originalTrajectory)
	for segment in reversed(originalTrajectory):
		flInit = int(segment[SEGMENT_LEVEL_INIT])
		flEnd = int(segment[SEGMENT_LEVEL_END])
		status = segment[STATUS]
		if flInit == flEnd  and status == '2':
			stop=True
			for i in range(1,4):
				flInitAux = int(originalTrajectory[line-i][SEGMENT_LEVEL_INIT])
				flEndAux = int(originalTrajectory[line-i][SEGMENT_LEVEL_END])
				statAux = originalTrajectory[line-i][STATUS]
				if flInitAux == flEndAux  and statAux == '2': pass
				else: stop = False; break
			if stop: break
		else: descentTime-= TIME_STEP
		line-=1
	tod = {}
	tod['LAT'] = originalTrajectory[line][SEGMENT_LAT_INIT]
	tod['LON'] = originalTrajectory[line][SEGMENT_LON_INIT]
	tod['ALT'] = originalTrajectory[line][SEGMENT_LEVEL_INIT]
	logger(myLogFile,rankMsg,LOG_STD,'Descending starts at time '+str(descentTime)+' [s]')
	return line

def checkAlone(currentCluster):

	"""
	Checking if I am alone in the assigned cluster
	"""
	clustered = True
	if len(currentCluster) == 1: clustered=False
	if clustered: logger(myLogFile,rankMsg,LOG_STD,'ALONE check - PASS')
	else: logger(myLogFile,rankMsg,LOG_STD,'ALONE check - FAIL')
	return clustered

def checkDescent():

	"""
	Checking if next position is descent
	"""
	clustered = True
	if currTime+TIME_STEP == descentTime: clustered=False
	if clustered: logger(myLogFile,rankMsg,LOG_STD,'DESCENT check - PASS')
	else: logger(myLogFile,rankMsg,LOG_STD,'DESCENT check - FAIL')
	return clustered

def checkFuelCost(nextPositionHPC):

	"""
	Checking if the Fuel cost to stay in cluster
	is larger that the cost to separate
	"""
	clustered = True
	latTOD = float(tod['LAT'])/60
	lonTOD = float(tod['LON'])/60
	latCurrent=float(hpcTrajectory[timestep][SEGMENT_LAT_INIT])/60
	lonCurrent=float(hpcTrajectory[timestep][SEGMENT_LON_INIT])/60
	latHPC=nextPositionHPC['LAT']
	lonHPC=nextPositionHPC['LON']
	dist1 = calculateDistanceBetweenPoints(latCurrent,lonCurrent,latTOD,lonTOD)
	dist2 = calculateDistanceBetweenPoints(latCurrent,lonCurrent,latHPC,lonHPC)
	dist3 = calculateDistanceBetweenPoints(latHPC,lonHPC,latTOD,lonTOD)
	dist1 = convertMtoNM(dist1)
	dist2 = convertMtoNM(dist2)
	dist3 = convertMtoNM(dist3)
	fuel1 = myKd*dist1*float(alonefuelparameter)
	fuel2 = myKd*dist2*float(coopfuelparameter)
	fuel3 = myKd*dist3*float(alonefuelparameter)
	nominalFuel = fuel1
	hpcFuel = fuel2 + fuel3
	logger(myLogFile,rankMsg,LOG_STD,'Nominal fuel = '+str(nominalFuel))
	logger(myLogFile,rankMsg,LOG_STD,'HPC-'+model+' Fuel = '+str(hpcFuel))
	logger(myLogFile,rankMsg,LOG_STD,'Difference Fuel = '+str(nominalFuel-hpcFuel))
	if nominalFuel < hpcFuel: clustered = False
	if clustered: logger(myLogFile,rankMsg,LOG_STD,'FUEL COST check - PASS')
	else: logger(myLogFile,rankMsg,LOG_STD,'FUEL COST check - FAIL')
	return clustered

def checkMyStatus(currTime):

	"""
	Checking my current status
	"""
	if myInitTime <= currTime and currTime < myEndTime:
		########################################################################################
		### Aircraft is flying
		if currTime >= cruiseTime and currTime < descentTime: flightStatus='CRUISE'
		else:
			if currTime < cruiseTime: flightStatus='CLIMB'
			else: flightStatus='DESCENT'
		########################################################################################
	else:
		########################################################################################
		### Aircraft is not flying
		if myInitTime > currTime: flightStatus='NOT_STARTED'
		else: flightStatus='FINISHED'
		########################################################################################

	### Climbing
	if currTime == myInitTime:
		#dateFormatted = getFormattedDate(hpcTrajectory[timestep][SEGMENT_DATE_INIT],hpcTrajectory[timestep][SEGMENT_TIME_INIT])
		logger(myLogFile,rankMsg,LOG_STD,'I have started climbing at currTime: '+str(currTime))
	### Cruising
	elif currTime == cruiseTime:
		#dateFormatted = getFormattedDate(hpcTrajectory[timestep][SEGMENT_DATE_INIT],hpcTrajectory[timestep][SEGMENT_TIME_INIT])
		logger(myLogFile,rankMsg,LOG_STD,'I have started cruise phase at currTime: '+str(currTime))
	### Descending
	elif currTime == descentTime:
		#dateFormatted = getFormattedDate(hpcTrajectory[timestep][SEGMENT_DATE_INIT],hpcTrajectory[timestep][SEGMENT_TIME_INIT])
		logger(myLogFile,rankMsg,LOG_STD,'I have started descending at currTime: '+str(currTime))
	### Finishing
	elif currTime == myEndTime:
		#dateFormatted = getFormattedDate(hpcTrajectory[timestep-1][SEGMENT_DATE_INIT],hpcTrajectory[timestep-1][SEGMENT_TIME_INIT])
		logger(myLogFile,rankMsg,LOG_STD,'I have finished my flight at currTime: '+str(currTime))

	return flightStatus

def finishClock():

	"""
	Finishing clock
	"""
	global myClockEndTime, myCompEndTime, myEndDateTime
	global myClockTimes, myCompTimes
	myClockEndTime, myCompEndTime, myEndDateTime = returnSecondsFromEpoch(), getComputingTime(), getDateAndTime()
	myClockTimes=[myClockInitTime, myClockEndTime]
	myCompTimes=[myCompInitTime, myCompEndTime]
	logger(myLogFile,rankMsg,LOG_STD,'Stoping clock at '+str(myEndDateTime))

def finishSim():

	"""
	Finishing simulation
	"""
	writePerformanceFile(myPerformanceFile, rank, tcID, size, qOfMachines, myInitDateTime, False, myClockTimes, myCompTimes)

def hprcFly(currentCluster):

	"""
	Flying cooperatively -- slaves function
	Flying cooperatively if a suitable cluster exists
	"""
	global hpcTrajectory, clustered, joined, myClusteredDuration
	clustered = True; nextPositionHPC = {}
	if len(currentCluster)>1:

		########################################################################################
		### New cluster logging
		logger(myLogFile,rankMsg,LOG_STD,'-------------------------------------------------------')
		########################################################################################

		########################################################################################
		### First check -- DESCENT
		clustered = checkDescent()
		response = informNodes(clustered,currentCluster,CLUSTERED_TAG)
		currentCluster = updateCluster(response, currentCluster)
		########################################################################################

		########################################################################################
		### Second check -- ALONE
		if clustered: clustered = checkAlone(currentCluster)
		########################################################################################

		########################################################################################
		### Third check -- Flying until proximity
		if clustered:
			nextPositionHPC, myNewFL = eval(model+'(currentCluster)')
			joined = approachCluster(nextPositionHPC, currentCluster)
			if joined:
				logger(myLogFile,rankMsg,LOG_STD,'I have been clustered :)')
				logger(myLogFile,rankMsg,LOG_STD,'Current cluster = '+str(currentCluster)+' , current time = '+str(currTime)+' , time step = '+str(timestep))
				logger(myLogFile,rankMsg,LOG_STD,'Model = '+str(model))
		########################################################################################

		########################################################################################
		### Fourth check -- VICSEK + DISTANCE COST
		if joined == True:
			while True:
				################################################################################
				### Copying current cluster
				testCluster = currentCluster[:]
				################################################################################

				################################################################################
				### Fifth check -- COST
				nextPositionHPC, myNewFL = eval(model+'(currentCluster)')
				clustered = checkFuelCost(nextPositionHPC)
				response = informNodes(clustered,currentCluster,CLUSTERED_TAG)
				currentCluster = updateCluster(response, currentCluster)
				if clustered == False: break
				################################################################################

				################################################################################
				### Sixth check -- ALONE
				clustered = checkAlone(currentCluster)
				if clustered == False: break
				################################################################################

				################################################################################
				### Seventh check -- Previous cluster
				if currentCluster == testCluster: break
				################################################################################
			########################################################################################
		########################################################################################

		########################################################################################
		### Updating next trajectory position
		if clustered == True:
			nextPositionHPC.update((x, round(y*60,6)) for x, y in nextPositionHPC.items())
			nextPositionHPC['ALT']=myNewFL
			nextPositionHPC.update((x,str(y)) for x,y in nextPositionHPC.items())
			logger(myLogFile,rankMsg,LOG_STD,'New HPC position calculated in current time: '+str(currTime))
			logger(myLogFile,rankMsg,LOG_STD,'New HPC position: '+str(nextPositionHPC))
			myClusteredDuration+=1
			for otherFlight in currentCluster:
				if otherFlight not in myClusteredFlights and otherFlight != rank: myClusteredFlights.append(otherFlight)
		else:
			joined = False
			nextPositionHPC['LAT'] = hpcTrajectory[timestep+1][SEGMENT_LAT_INIT]
			nextPositionHPC['LON'] = hpcTrajectory[timestep+1][SEGMENT_LON_INIT]
			nextPositionHPC['ALT'] = hpcTrajectory[timestep+1][SEGMENT_LEVEL_INIT]
			logger(myLogFile,rankMsg,LOG_STD,'Original trajectory is kept in current time: '+str(currTime))
		### Changes to current timestep
		hpcTrajectory[timestep][SEGMENT_LAT_END]=nextPositionHPC['LAT']
		hpcTrajectory[timestep][SEGMENT_LON_END]=nextPositionHPC['LON']
		hpcTrajectory[timestep][SEGMENT_LEVEL_END]=nextPositionHPC['ALT']
		### Changes to next timestep
		hpcTrajectory[timestep+1][SEGMENT_LAT_INIT]=nextPositionHPC['LAT']
		hpcTrajectory[timestep+1][SEGMENT_LON_INIT]=nextPositionHPC['LON']
		hpcTrajectory[timestep+1][SEGMENT_LEVEL_INIT]=nextPositionHPC['ALT']
		####################################################################################

		########################################################################################
		### Updating segment fuel
		latInit = float(hpcTrajectory[timestep][SEGMENT_LAT_INIT])/60
		lonInit = float(hpcTrajectory[timestep][SEGMENT_LON_INIT])/60
		latEnd = float(hpcTrajectory[timestep][SEGMENT_LAT_END])/60
		lonEnd = float(hpcTrajectory[timestep][SEGMENT_LON_END])/60
		segmentDistanceM = calculateDistanceBetweenPoints(latInit,lonInit,latEnd,lonEnd)
		segmentDistanceNM = convertMtoNM(segmentDistanceM)
		fuelFactor = float(coopfuelparameter) if clustered else float(alonefuelparameter)
		fuelSegment = myKd*segmentDistanceNM*fuelFactor
		testCoordinates = {'latInit':latInit,'lonInit':lonInit,'latEnd':latEnd,'lonEnd':lonEnd}
		logger(myLogFile,rankMsg,LOG_STD,'Test coordinates: '+str(testCoordinates))
		hpcTrajectory[timestep][SEGMENT_FUEL] = str(fuelSegment)
		logger(myLogFile,rankMsg,LOG_STD,'Distance in segment: '+str(segmentDistanceNM))
		logger(myLogFile,rankMsg,LOG_STD,'Fuel factor in segment: '+str(fuelFactor))
		logger(myLogFile,rankMsg,LOG_STD,'Fuel consumed in segment: '+str(fuelSegment))
		########################################################################################

		####################################################################################
		## Wrapping things up
		logger(myLogFile,rankMsg,LOG_STD,'-------------------------------------------------------')
		########################################################################################
	else: clustered = False

def informNodes(info,currentCluster,tag):

	"""
	Informing nodes in my cluster about my decision to
	remain in the cluster
	"""
	response={}
	for flight in currentCluster:
		if flight != rank: sendMPIMsg(flight,info,tag)
	for flight in currentCluster:
		if flight != rank:
			dataDict = receiveMPIMsg(flight,tag)
			sender = dataDict['sender']
			info = dataDict['data']
			response[sender] = info
	return response

def readParameters():

	"""
	Reading parameters
	"""
	### Arguments
	global tcID, flightsQ, scenario, model, grouping, radius, alonefuelparameter, coopfuelparameter, approachedDistance, infrastructureFile, log
	global machines, qOfMachines
	########################################################################################

	########################################################################################
	### Software arguments
	if len(sys.argv) != 2:
		if rank == 0: usage()
		sys.exit(0)
	testCaseFile=sys.argv[1]
	########################################################################################

	### Parameters reading
	tcID, flightsQ, scenario, model, grouping, radius, alonefuelparameter, coopfuelparameter, approachedDistance, infrastructureFile, log = readXMLInput(rankMsg,testCaseFile)
	machines, qOfMachines = readInfrastructureFile(infrastructureFile)
	########################################################################################

def receiveMPIMsg(src=MPI.ANY_SOURCE,t=MPI.ANY_TAG):

	"""
	Sending MPI messages
	"""
	global qOfMSGReceived, bytesReceived, receivingTime
	global qOfClusteredMSGReceived, bytesClusteredReceived, receivingClusteredTime
	dataDict={}
	status = MPI.Status()
	initT = datetime.now()
	data=comm.recv(source=src, tag=t, status=status)
	endT = datetime.now()
	dataDict['data']=data
	dataDict['sender']=int(status.Get_source())
	msgDuration = returnSeconds(initT,endT)
	msgBytes = getBytes(data)
	qOfMSGReceived+=1
	bytesReceived+=msgBytes
	receivingTime+=msgDuration
	if rank != nmRank and dataDict['sender'] != nmRank:
		qOfClusteredMSGReceived+=1
		bytesClusteredReceived+=msgBytes
		receivingClusteredTime+=msgDuration
	return dataDict

def sendMPIMsg(destination,data,t=MPI.ANY_TAG):

	"""
	Sending MPI messages
	"""
	global qOfMSGSent, bytesSent, sendingTime
	global qOfClusteredMSGSent, bytesClusteredSent, sendingClusteredTime
	initT = datetime.now()
	comm.send(data, dest=destination,tag=t)
	endT = datetime.now()
	msgDuration = returnSeconds(initT,endT)
	msgBytes = getBytes(data)
	qOfMSGSent+=1
	bytesSent+=msgBytes
	sendingTime+=msgDuration
	if rank != nmRank and destination != nmRank:
		qOfClusteredMSGSent+=1
		bytesClusteredSent+=msgBytes
		sendingClusteredTime+=msgDuration

def settingSimFiles():

	"""
	Setting simulation flights
	"""
	global myPerformanceFile
	global resultsFile, summaryFile, cooperativeFlightsFile
	myPerformanceFile=outputFolder+'/'+str(rank)+'_perf.txt'
	resultsFile = outputFolder+'/results.txt'
	summaryFile = outputFolder+'/summary.txt'
	cooperativeFlightsFile = outputFolder+'/cooperativeFlights.txt'
	writePerformanceFile(myPerformanceFile, rank, tcID, size, qOfMachines, myInitDateTime)
	if rank == nmRank:
		writeResultsFile(resultsFile)
		writeCooperativeFlightsFile(cooperativeFlightsFile)
		bandwidth = checkBandwidth(machines,rankMsg,myLogFile)
		latency = checkLatency(machines,rankMsg,myLogFile)
		perFile = open(myPerformanceFile,'a')
		perFile.write('Average bandwidth UDP: '+str(bandwidth['UDP'])+'\n')
		perFile.write('Average bandwidth TCP: '+str(bandwidth['TCP'])+'\n')
		perFile.write('Average Latency: '+str(latency)+'\n')
		perFile.close()

def settingOriginalTrajectory():

	"""
	Setting original trajectory
	"""
	global rankTrajectoryFile, rankTrajectoryHPCFile
	global originalTrajectory, hpcTrajectory
	global myInitTime, myEndTime

	########################################################################################
	### Setting original trajectoty and setting initial variables
	rankTrajectoryFile=trajectoriesFolder+'/'+str(rank).zfill(len(str(flightsQ)))+'.eSo6'
	rankTrajectoryHPCFile=hpcTrajectoriesFolder+'/'+str(rank).zfill(len(str(flightsQ)))+'.eSo6'
	logger(myLogFile,rankMsg,LOG_STD,'Reading original trajectory')
	originalTrajectory, myInitTime, myEndTime = readESO6Trajectory(rankTrajectoryFile)
	########################################################################################

	########################################################################################
	### Replacing original trajectory for hpc trajectory
	hpcTrajectory=[x[:] for x in originalTrajectory]
	########################################################################################

	logger(myLogFile,rankMsg,LOG_STD,'Original trajectory has been read') ###

def settingWorkingSpace():

	"""
	Setting working directories
	"""
	### Folders
	global tcFolder, trajectoriesFolder, hpcTrajectoriesFolder, outputFolder, logsFolder, myLogFile
	########################################################################################

	### Folders and files setting
	tcFolder=DATA_ROOT_FOLDER+'/'+scenario+'/'+tcID
	trajectoriesFolder=tcFolder+'/'+TRAJ_FOLDER
	hpcTrajectoriesFolder=tcFolder+'/'+HPC_TRAJ_FOLDER
	outputFolder=tcFolder+'/'+OUTPUT_FOLDER
	logsFolder=tcFolder+'/'+LOGS_FOLDER
	myLogFile=logsFolder+'/'+str(rank)+'.log' ###
	########################################################################################

	########################################################################################
	### Setting work space
	if rank == nmRank:
		logger(myLogFile,rankMsg,LOG_STD,'Setting work space')
		folders=[tcFolder, trajectoriesFolder, hpcTrajectoriesFolder, outputFolder, logsFolder]
		createFolders(folders)
	####################################################################################### ###

def startClock():

	"""
	Starting clock
	"""
	global myClockInitTime, myCompInitTime, myInitDateTime
	global myClockTimes, myCompTimes
	global initTime, endTime, currTime
	myClockInitTime, myCompInitTime, myInitDateTime = returnSecondsFromEpoch(), getComputingTime(), getDateAndTime()
	myClockTimes=[]; myCompTimes=[]
	initTime, endTime = calculateInitAndEndTime(trajectoriesFolder, size, flightsQ)
	currTime=initTime
	if rank == nmRank:
		logger(myLogFile,rankMsg,LOG_STD,' Calculating simulation init and end time')
		logger(myLogFile,rankMsg,LOG_STD,'Init time: '+str(initTime)+' , End time = '+str(endTime))
	else: logger(myLogFile,rankMsg,LOG_STD,'Init date time: '+str(myInitDateTime))

def updateCluster(response, currentCluster):

	"""
	Updating cluster
	"""
	for flight in response:
		logger(myLogFile,rankMsg,LOG_STD,'Flight '+str(flight)+', clustered status: '+str(response[flight]))
		if response[flight] == False:
			logger(myLogFile,rankMsg,LOG_STD,'Deleting Flight '+str(flight)+' from my current cluster')
			if flight in currentCluster: del(currentCluster[currentCluster.index(flight)])
	return currentCluster

def vicsek(currentCluster):

	"""
	Flying in Vicsek model mode
	Noise excluded
	Returns the next position according to Vicsek model
	"""
	clusterSize=len(currentCluster)
	track=float(hpcTrajectory[timestep][SEGMENT_TRACK])
	flightLevel=int(hpcTrajectory[timestep][SEGMENT_LEVEL_INIT])
	groundSpeed=float(hpcTrajectory[timestep][SEGMENT_GROUND_SPEED])
	info = [track,flightLevel,groundSpeed]
	response = informNodes(info,currentCluster,VICSEK_TAG)
	myNewTrack=0.0
	myNewFL=flightLevel
	myNewGS=groundSpeed
	for flight in response:
		if flight != rank:
			fTrack=response[flight][0]
			fLevel=response[flight][1]
			fGroSp=response[flight][2]
			myNewTrack+=fTrack
			myNewFL+=fLevel
			myNewGS+=fGroSp
	myNewTrack = myNewTrack/(clusterSize-1)
	myNewFL = roundUP(myNewFL/clusterSize)
	myNewGS = myNewGS/clusterSize
	deltaT = float(TIME_STEP)/3600
	dx=myNewGS*deltaT*cos(radians(myNewTrack))
	dy=myNewGS*deltaT*sin(radians(myNewTrack))
	dist=sqrt(pow(dx,2)+pow(dy,2))
	dist = convertNMtoM(dist)
	latCurrent=float(hpcTrajectory[timestep][SEGMENT_LAT_INIT])/60
	lonCurrent=float(hpcTrajectory[timestep][SEGMENT_LON_INIT])/60
	nextPositionHPC=getPoint(latCurrent,lonCurrent,myNewTrack,dist)
	testCoordinates = {'latInit':latCurrent,'lonInit':lonCurrent,'latEnd':nextPositionHPC['LAT'],'lonEnd':nextPositionHPC['LON']}
	logger(myLogFile,rankMsg,LOG_STD,'Vicsek -- Test coordinates: '+str(testCoordinates))
	return nextPositionHPC, myNewFL

def writeTrajectoryFile():

	"""
	Writing trajectory file
	"""
	logger(myLogFile,rankMsg,LOG_STD,'Writing cooperative trajectory')
	if originalTrajectory == hpcTrajectory:
		logger(myLogFile,rankMsg,LOG_STD,'My original trajectory was not modified')
		os.system('cp '+rankTrajectoryFile+' '+rankTrajectoryHPCFile)
	else:
		logger(myLogFile,rankMsg,LOG_STD,'My original trajectory was modified')
		newTrajFile=open(rankTrajectoryHPCFile,'a')
		for segment in hpcTrajectory:
			line=''
			for data in segment: line+=data+' '
			newTrajFile.write(line+'\n')
		newTrajFile.close()
	logger(myLogFile,rankMsg,LOG_STD,'Trajectory file created')

######################################################################################################################################################
######################################################################################################################################################

def main():

	"""
	Parallel cooperative flights
	"""
	##################################################################################################################################################
	### MPI parallel libraries
	global comm, rank, size, nmRank, slaveRank, slavesSize, rankMsg
	##################################################################################################################################################

	##################################################################################################################################################
	### General variables
	global currTime, timestep
	##################################################################################################################################################

	##################################################################################################################################################
	### Network Manager variables
	global vehiclesPosition, liveFlights, nmQOfClusters, qOfClusters, clusters, cruiseFlights, clusteredFlights, setClusters, aircraftNetwork
	global GRC_sum, GRC_updates, totalOriginalFuel, totalCooperatedFuel, aircraftQOfClusters, aircraftClusteredDuration, flightsClusteredFlights
	global procsBytesSent, procsBytesReceived, procsSendingTime, procsReceivingTime, procsQOfMSGSent, procsQOfMSGReceived
	global aircraftBytesClusteredSent, aircraftBytesClusteredReceived, aircraftSendingClusteredTime, aircraftReceivingClusteredTime, aircraftQOfClusteredMSGSent, aircraftQOfClusteredMSGReceived
	##################################################################################################################################################

	##################################################################################################################################################
	### Flight variables
	global clustered, currentCluster, timestep, joined, myQOfClusters, myClusteredDuration, myOriginalFuel, myCooperatedFuel, myKd, myClusteredFlights
	global bytesClusteredSent, bytesClusteredReceived, sendingClusteredTime, receivingClusteredTime, qOfClusteredMSGSent, qOfClusteredMSGReceived
	##################################################################################################################################################

	##################################################################################################################################################
	### Common variables
	global bytesSent, bytesReceived, sendingTime, receivingTime, qOfMSGSent, qOfMSGReceived
	##################################################################################################################################################

	##################################################################################################################################################
	### Parallel process rank assignment
	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()
	nmRank=0
	##################################################################################################################################################

	##################################################################################################################################################
	### Parallel process rank assignment in new communicator
	allProcs=comm.Get_group()
	slaves = allProcs.Excl([nmRank])
	slavesComm=comm.Create(slaves)
	if rank != nmRank:
		slaveRank=slavesComm.Get_rank()
		slavesSize=slavesComm.Get_size()
	rankMsg = '[Rank '+str(rank)+' msg]: '
	##################################################################################################################################################

	##################################################################################################################################################
	### Reading parameters
	readParameters()
	#sys.stdout = open(log, "w")
	comm.Barrier()
	##################################################################################################################################################

	##################################################################################################################################################
	### Setting working space
	settingWorkingSpace()
	comm.Barrier()
	##################################################################################################################################################

	##################################################################################################################################################
	### Starting clock
	startClock()
	comm.Barrier()
	##################################################################################################################################################

	##################################################################################################################################################
	### Setting performance and log files
	settingSimFiles()
	comm.Barrier()
	##################################################################################################################################################

	##################################################################################################################################################
	### Initialization Simulation variables
	logger(myLogFile,rankMsg,LOG_STD,'Setting simulation variables')
	if rank == nmRank:
		vehiclesPosition = {}
		liveFlights = [i for i in range(1,size)]
		nmQOfClusters = 0
		qOfClusters = 0
		clusters = {}
		for flight in liveFlights: clusters[flight] = []
		cruiseFlights = []
		clusteredFlights = []
		setClusters = False
		aircraftNetwork = None
		GRC_sum = 0.0
		GRC_updates = 0
		maxGRC = 0.0
		minGRC = 0.0
		totalOriginalFuel = 0.0
		totalCooperatedFuel = 0.0
		aircraftQOfClusters = []
		aircraftClusteredDuration = []
		flightsClusteredFlights = {}
		procsBytesSent = []
		procsBytesReceived = []
		procsSendingTime = []
		procsReceivingTime = []
		procsQOfMSGSent = []
		procsQOfMSGReceived = []
		aircraftBytesClusteredSent = []
		aircraftBytesClusteredReceived = []
		aircraftSendingClusteredTime = []
		aircraftReceivingClusteredTime = []
		aircraftQOfClusteredMSGSent = []
		aircraftQOfClusteredMSGReceived = []
	else:
		clustered = False
		currentCluster=[]
		timestep=0
		joined = False
		myQOfClusters = 0
		myClusteredDuration = 0
		myOriginalFuel = 0.0
		myCooperatedFuel = 0.0
		myClusteredFlights = []
		simulationSummary = []
		bytesClusteredSent = 0
		bytesClusteredReceived = 0
		sendingClusteredTime = 0
		receivingClusteredTime = 0
		qOfClusteredMSGSent = 0
		qOfClusteredMSGReceived = 0
	bytesSent  = 0
	bytesReceived = 0
	sendingTime = 0
	receivingTime = 0
	qOfMSGSent = 0
	qOfMSGReceived = 0
	comm.Barrier()
	##################################################################################################################################################

	##################################################################################################################################################
	### HPC cooperative flights simiulation
	#
	if rank == nmRank:
		##################################################################################################################################################
		### Simulation
		logger(myLogFile,rankMsg,LOG_STD,'Starting simulation')
		while currTime <= endTime:
			##################################################################################################################################################
			### Sending current time to live flights
			logger(myLogFile,rankMsg,LOG_STD,'-------------------------------------------------------')
			logger(myLogFile,rankMsg,LOG_STD,'Current time = '+str(currTime))
			##################################################################################################################################################

			##################################################################################################################################################
			### Get status of all flights -- MPI communication
			logger(myLogFile,rankMsg,LOG_STD,'Receiving flights current status')
			statuses={}
			for flight in liveFlights:
				msg=receiveMPIMsg(flight,STATUS_TAG)
				flight=msg['sender']
				flightStatus=msg['data']
				statuses[flight]=flightStatus
				logger(myLogFile,rankMsg,LOG_STD,'Flight: '+str(flight)+' -- '+str(flightStatus))
			##################################################################################################################################################

			##################################################################################################################################################
			### Updating centralized image of the aircraft network
			logger(myLogFile,rankMsg,LOG_STD,'Updating centralized image of the aircraft network')
			for flight in liveFlights:
				if statuses[flight] == 'CRUISE':
					if flight not in cruiseFlights: cruiseFlights.append(flight)
				elif statuses[flight] == 'DESCENT':
					if flight in cruiseFlights: del(cruiseFlights[cruiseFlights.index(flight)])
					if flight in clusteredFlights:
						del(clusteredFlights[clusteredFlights.index(flight)])
						clusters[flight]=[]
						for f in clusters:
							if flight in clusters[f]: del(clusters[f][clusters[f].index(flight)])
			qOfCruiseFlights = len(cruiseFlights)
			if qOfCruiseFlights > 0: aircraftNetwork = setNetwork(cruiseFlights)
			logger(myLogFile,rankMsg,LOG_STD,'Number of cruise flights are '+str(qOfCruiseFlights))
			logger(myLogFile,rankMsg,LOG_STD,'Cruise flights are '+str(cruiseFlights))
			##################################################################################################################################################

			##################################################################################################################################################
			### Get telemetry from cruise flights -- MPI communication
			if qOfCruiseFlights > 0: logger(myLogFile,rankMsg,LOG_STD,'Receiving telemetry from cruised flights')
			for flight in cruiseFlights:
				dataDict=receiveMPIMsg(flight,TELEMETRY_TAG)
				vehiclesPosition[dataDict['sender']]=dataDict['data']
			##################################################################################################################################################

			##################################################################################################################################################
			### Calculating NM clusters and updating possible (NM) quantity of clusters
			if qOfCruiseFlights >= 2:
				logger(myLogFile,rankMsg,LOG_STD,'Computing clusters using clustering = '+str(grouping)+' model')
				previousNMClusters = dict(clusters)
				if grouping == 'fifo': clusters, clusteredFlights, setClusters = fifo(clusters, vehiclesPosition ,cruiseFlights, radius, currTime)
				logger(myLogFile,rankMsg,LOG_STD,'Set clusters = '+str(setClusters))
				if setClusters:
					checkedFlights = []
					### Updating quantity of clusters calculated by NM
					for flight in clusters:
						if len(previousNMClusters[flight]) == 0 and len(clusters[flight]) > 0 and flight not in checkedFlights:
							nmQOfClusters+=1
							for f in clusters[flight]: checkedFlights.append(f)
					nmClusters = dict(clusters)
					nmClustersLine=''
					for flight in sorted(nmClusters): nmClustersLine+=str(flight)+':'+str(nmClusters[flight])+' '
					logger(myLogFile,rankMsg,LOG_STD,'Clusters calculated by Network Manager: '+nmClustersLine)
					logger(myLogFile,rankMsg,LOG_STD,'Current quantity of clusters calculated by network manager are '+str(nmQOfClusters))
			else: logger(myLogFile,rankMsg,LOG_STD,'Not enough cruise flights to run clustering = '+str(grouping)+' model')
			qOfClusteredFlights=len(clusteredFlights)
			logger(myLogFile,rankMsg,LOG_STD,'Number of clustered flights are '+str(qOfClusteredFlights))
			logger(myLogFile,rankMsg,LOG_STD,'Clustered flights are: '+str(clusteredFlights))
			##################################################################################################################################################

			##################################################################################################################################################
			### Sending NM clusters to cruise flights -- MPI communication
			for i in cruiseFlights: sendMPIMsg(i,clusters[i],NM_CLUSTERS_TAG)
			##################################################################################################################################################

			##################################################################################################################################################
			### Updating clusters and aircrat network with aircraft responses -- MPI communication
			unClusteredFlights = []
			for flight in clusteredFlights:
				dataDict=receiveMPIMsg(flight,AC_SLAVES_TAG)
				if not dataDict['data']: unClusteredFlights.append(dataDict['sender'])
			for flight in unClusteredFlights:
				del(clusteredFlights[clusteredFlights.index(flight)])
				clusters[flight]=[]
				for f in clusters:
					if flight in clusters[f]: del(clusters[f][clusters[f].index(flight)])
			##################################################################################################################################################

			##################################################################################################################################################
			### Calculating accepted clusters by flights
			if setClusters:
				if clusters == nmClusters: logger(myLogFile,rankMsg,LOG_STD,'All flights accepted its assigned NM clusters')
				else:
					clustersLine=''
					for flight in sorted(clusters): clustersLine+=str(flight)+':'+str(clusters[flight])+' '
					logger(myLogFile,rankMsg,LOG_STD,'Accepted clusters: '+clustersLine)
				checkedFlights = []
				for flight in clusters:
					if len(previousNMClusters[flight]) == 0 and len(clusters[flight]) > 0 and flight not in checkedFlights:
						qOfClusters+=1
						for f in clusters[flight]: checkedFlights.append(f)
			##################################################################################################################################################

			##################################################################################################################################################
			### Calculating GRC and storing results
			if qOfCruiseFlights > 1:
				aircraftNetwork=addEdges(aircraftNetwork,clusters)
				GRC = calculateGRC(calculateLRC(aircraftNetwork))
				if GRC > maxGRC: maxGRC = GRC
				if GRC < minGRC: minGRC = GRC
				GRC_sum += GRC
				GRC_updates+=1
				writeResultsFile(resultsFile, currTime, qOfCruiseFlights, nmQOfClusters, qOfClusters, GRC, False)
			##################################################################################################################################################

			##################################################################################################################################################
			### Next time step updating
			currTime+=TIME_STEP
			##################################################################################################################################################
		########################################################################################

		########################################################################################
		### Reading simulation summary for all flights and NM
		logger(myLogFile,rankMsg,LOG_STD,'Receiving flight simulation summaries')
		flightsWithFuelProfit = []
		flightsWithoutFuelProfit = []
		for flight in liveFlights:
			msg=receiveMPIMsg(flight,SIM_SUMARY_TAG)
			flightSummary=msg['data']
			flightOriginalFuel = flightSummary[0]
			flightCooperatedFuel = flightSummary[1]
			flightQOfClusters = flightSummary[2]
			flightClusteredDuration = flightSummary[3]
			flightClusteredFlights = flightSummary[4]
			flightBytesSent = flightSummary[5]
			flightBytesReceived = flightSummary[6]
			flightSendingTime = flightSummary[7]
			flightReceivingTime = flightSummary[8]
			flightQOfMSGSent = flightSummary[9]
			flightQOfMSGReceived = flightSummary[10]
			flightBytesClusteredSent = flightSummary[11]
			flightBytesClusteredReceived = flightSummary[12]
			flightSendingClusteredTime = flightSummary[13]
			flightReceivingClusteredTime = flightSummary[14]
			flightQOfClusteredMSGSent = flightSummary[15]
			flightQOfClusteredMSGReceived = flightSummary[16]
			if float(flightOriginalFuel) > float(flightCooperatedFuel): flightsWithFuelProfit.append(flight)
			elif float(flightOriginalFuel) < float(flightCooperatedFuel): flightsWithoutFuelProfit.append(flight)
			totalOriginalFuel += flightOriginalFuel
			totalCooperatedFuel += flightCooperatedFuel
			if flightQOfClusters > 0:
				aircraftQOfClusters.append(flightQOfClusters)
				aircraftClusteredDuration.append(flightClusteredDuration)
			flightsClusteredFlights[flight] = flightClusteredFlights
			procsBytesSent.append(flightBytesSent)
			procsBytesReceived.append(flightBytesReceived)
			procsSendingTime.append(flightSendingTime)
			procsReceivingTime.append(flightReceivingTime)
			procsQOfMSGSent.append(flightQOfMSGSent)
			procsQOfMSGReceived.append(flightQOfMSGReceived)
			if flightQOfClusters > 0:
				aircraftBytesClusteredSent.append(flightBytesClusteredSent)
				aircraftBytesClusteredReceived.append(flightBytesClusteredReceived)
				aircraftSendingClusteredTime.append(flightSendingClusteredTime)
				aircraftReceivingClusteredTime.append(flightReceivingClusteredTime)
				aircraftQOfClusteredMSGSent.append(flightQOfClusteredMSGSent)
				aircraftQOfClusteredMSGReceived.append(flightQOfClusteredMSGReceived)
		procsBytesSent.append(bytesSent)
		procsBytesReceived.append(bytesReceived)
		procsSendingTime.append(sendingTime)
		procsReceivingTime.append(receivingTime)
		procsQOfMSGSent.append(qOfMSGSent)
		procsQOfMSGReceived.append(qOfMSGReceived)
		########################################################################################

		########################################################################################
		### Computing and writing simulation summary
		logger(myLogFile,rankMsg,LOG_STD,'Computing and writing simulation summary')
		acceptanceRatio = float(qOfClusters * 100) / nmQOfClusters if nmQOfClusters >= 1 else 0
		averageQOfClusters = float(sum(aircraftQOfClusters)) / len(aircraftQOfClusters) if len(aircraftQOfClusters) > 0 else 0
		maxQOfClusters = max(aircraftQOfClusters) if len(aircraftQOfClusters) > 0 else 0
		minQOfClusters = min(aircraftQOfClusters) if len(aircraftQOfClusters) > 0 else 0
		averageClusteredDuration = float(sum(aircraftClusteredDuration)) / len(aircraftClusteredDuration) if len(aircraftClusteredDuration) > 0 else 0
		maxClusteredDuration = max(aircraftClusteredDuration) if len(aircraftClusteredDuration) > 0 else 0
		minClusteredDuration = min(aircraftClusteredDuration) if len(aircraftClusteredDuration) > 0 else 0
		averageBytesClusteredSent = float(sum(aircraftBytesClusteredSent)) / len(aircraftBytesClusteredSent) if len(aircraftBytesClusteredSent) > 0 else 0
		maxBytesClusteredSent = max(aircraftBytesClusteredSent) if len(aircraftBytesClusteredSent) > 0 else 0
		minBytesClusteredSent = min(aircraftBytesClusteredSent) if len(aircraftBytesClusteredSent) > 0 else 0
		averageBytesClusteredReceived = float(sum(aircraftBytesClusteredReceived)) / len(aircraftBytesClusteredReceived) if len(aircraftBytesClusteredReceived) > 0 else 0
		maxBytesClusteredReceived = max(aircraftBytesClusteredReceived) if len(aircraftBytesClusteredReceived) > 0 else 0
		minBytesClusteredReceived = min(aircraftBytesClusteredReceived) if len(aircraftBytesClusteredReceived) > 0 else 0
		averageSendingClusteredTime = float(sum(aircraftSendingClusteredTime)) / len(aircraftSendingClusteredTime) if len(aircraftSendingClusteredTime) > 0 else 0
		maxSendingClusteredTime = max(aircraftSendingClusteredTime) if len(aircraftSendingClusteredTime) > 0 else 0
		minSendingClusteredTime = min(aircraftSendingClusteredTime) if len(aircraftSendingClusteredTime) > 0 else 0
		averageReceivingClusteredTime = float(sum(aircraftReceivingClusteredTime)) / len(aircraftReceivingClusteredTime) if len(aircraftReceivingClusteredTime) > 0 else 0
		maxReceivingClusteredTime = max(aircraftReceivingClusteredTime) if len(aircraftReceivingClusteredTime) > 0 else 0
		minReceivingClusteredTime = min(aircraftReceivingClusteredTime) if len(aircraftReceivingClusteredTime) > 0 else 0
		averageQOfClusteredMSGSent = float(sum(aircraftQOfClusteredMSGSent)) / len(aircraftQOfClusteredMSGSent) if len(aircraftQOfClusteredMSGSent) > 0 else 0
		maxQOfClusteredMSGSent = max(aircraftQOfClusteredMSGSent) if len(aircraftQOfClusteredMSGSent) > 0 else 0
		minQOfClusteredMSGSent = min(aircraftQOfClusteredMSGSent) if len(aircraftQOfClusteredMSGSent) > 0 else 0

		averageQOfClusteredMSGReceived = float(sum(aircraftQOfClusteredMSGReceived)) / len(aircraftQOfClusteredMSGReceived) if len(aircraftQOfClusteredMSGReceived) > 0 else 0
		maxQOfClusteredMSGReceived = max(aircraftQOfClusteredMSGReceived) if len(aircraftQOfClusteredMSGReceived) > 0 else 0
		minQOfClusteredMSGReceived = min(aircraftQOfClusteredMSGReceived) if len(aircraftQOfClusteredMSGReceived) > 0 else 0

		summaryResults = [tcID,
						  scenario,
						  size-1,
						  size,
						  qOfMachines,
						  machines,
						  model,
						  grouping,
						  radius,
						  alonefuelparameter,
						  coopfuelparameter,
						  approachedDistance,
						  qOfClusters,
						  nmQOfClusters,
						  acceptanceRatio,
						  GRC_sum / GRC_updates,
						  maxGRC,
						  minGRC,
						  GRC_updates,
						  totalOriginalFuel,
						  totalCooperatedFuel,
						  totalOriginalFuel-totalCooperatedFuel,
						  len(flightsWithFuelProfit),
						  flightsWithFuelProfit,
						  len(flightsWithoutFuelProfit),
						  flightsWithoutFuelProfit,
						  averageQOfClusters,
						  maxQOfClusters,
						  minQOfClusters,
						  averageClusteredDuration,
						  maxClusteredDuration,
						  minClusteredDuration,
						  sum(procsBytesSent),
						  float(sum(procsBytesSent)) / len(procsBytesSent),
						  max(procsBytesSent),
						  min(procsBytesSent),
						  sum(procsBytesReceived),
						  float(sum(procsBytesReceived)) / len(procsBytesReceived),
						  max(procsBytesReceived),
						  min(procsBytesReceived),
				  		  sum(procsSendingTime),
						  float(sum(procsSendingTime)) / len(procsSendingTime),
						  max(procsSendingTime),
						  min(procsSendingTime),
						  sum(procsReceivingTime),
						  float(sum(procsReceivingTime)) / len(procsReceivingTime),
						  max(procsReceivingTime),
						  min(procsReceivingTime),
						  sum(procsQOfMSGSent),
						  float(sum(procsQOfMSGSent)) / len(procsQOfMSGSent),
						  max(procsQOfMSGSent),
						  min(procsQOfMSGSent),
						  sum(procsQOfMSGReceived),
						  float(sum(procsQOfMSGReceived)) / len(procsQOfMSGReceived),
						  max(procsQOfMSGReceived),
						  min(procsQOfMSGReceived),
						  sum(aircraftBytesClusteredSent),
						  averageBytesClusteredSent,
						  maxBytesClusteredSent,
						  minBytesClusteredSent,
					   	  sum(aircraftBytesClusteredReceived),
						  averageBytesClusteredReceived,
						  maxBytesClusteredReceived,
						  minBytesClusteredReceived,
						  sum(aircraftSendingClusteredTime),
						  averageSendingClusteredTime,
						  maxSendingClusteredTime,
						  minSendingClusteredTime,
						  sum(aircraftReceivingClusteredTime),
						  averageReceivingClusteredTime,
						  maxReceivingClusteredTime,
						  minReceivingClusteredTime,
						  sum(aircraftQOfClusteredMSGSent),
						  averageQOfClusteredMSGSent,
						  maxQOfClusteredMSGSent,
						  minQOfClusteredMSGSent,
						  sum(aircraftQOfClusteredMSGReceived),
						  averageQOfClusteredMSGReceived,
						  maxQOfClusteredMSGReceived,
						  minQOfClusteredMSGReceived]
		summaryResults=map(str, summaryResults)
		writeSummaryFile(summaryFile,summaryResults)
		########################################################################################

		########################################################################################
		### Writing cooperative flights file
		logger(myLogFile,rankMsg,LOG_STD,'Writing cooperative flights file')
		writeCooperativeFlightsFile(cooperativeFlightsFile,flightsClusteredFlights,False)
		########################################################################################

	else:

		########################################################################################
		### Setting original trajectory
		settingOriginalTrajectory()
		myOriginalFuel = computeFuel(originalTrajectory)
		logger(myLogFile,rankMsg,LOG_STD,'Original fuel = '+str(myOriginalFuel))
		slavesComm.Barrier()
		########################################################################################

		########################################################################################
		### Calculating cruise time
		cruiseLine = calculateCruise()
		slavesComm.Barrier()
		########################################################################################

		########################################################################################
		### Calculating descent time
		descentLine = calculateDescent()
		slavesComm.Barrier()
		########################################################################################

		########################################################################################
		### Computing Kd -- Constant for cooperative fuel calculation
		myKd = computeKd(myLogFile,rankMsg,originalTrajectory,cruiseLine,descentLine)
		########################################################################################

		########################################################################################
		timestep=0
		flightStatus='NOT_STARTED'
		########################################################################################

		### Simulation
		logger(myLogFile,rankMsg,LOG_STD,'Starting simulation')
		slavesComm.Barrier()
		while currTime <= endTime:

			########################################################################################
			### Checking my flight status (CLIMB, DESCENT, CRUISE)
			flightStatus = checkMyStatus(currTime)
			sendMPIMsg(nmRank,flightStatus,STATUS_TAG)
			slavesComm.Barrier()
			########################################################################################

			########################################################################################
			### Sending telemetry to Network Manager and receiving currentCluster
			previousCluster = currentCluster[:]
			if flightStatus == 'CRUISE':
				sendMPIMsg(nmRank,hpcTrajectory[timestep],TELEMETRY_TAG)
				dataDict=receiveMPIMsg(0,NM_CLUSTERS_TAG)
				currentCluster=dataDict['data']
				logger(myLogFile,rankMsg,LOG_STD,' NM Current cluster is '+str(currentCluster))
				if len(currentCluster) != 0:
					### Executing HPC flying model and sending acceptance of cluster
					hprcFly(currentCluster)
					sendMPIMsg(0,clustered,AC_SLAVES_TAG)
					if clustered and currentCluster != previousCluster: myQOfClusters+=1
					logger(myLogFile,rankMsg,LOG_STD,' Informing NM about my clustered decision -- clustered: '+str(clustered)+', joined: '+str(joined))
			slavesComm.Barrier()
			########################################################################################

			########################################################################################
			### timestep updating
			if flightStatus not in ['NOT_STARTED','FINISHED']: timestep+=1
			currTime+=TIME_STEP
			slavesComm.Barrier()
			########################################################################################
		########################################################################################

		########################################################################################
		### Calulating cooperated fuel
		logger(myLogFile,rankMsg,LOG_STD,'Calculating cooperated fuel')
		myCooperatedFuel = computeFuel(hpcTrajectory)
		logger(myLogFile,rankMsg,LOG_STD,'Cooperated fuel = '+str(myCooperatedFuel))
		logger(myLogFile,rankMsg,LOG_STD,'Difference in fuel = '+str(myOriginalFuel - myCooperatedFuel))
		slavesComm.Barrier()
		########################################################################################

		########################################################################################
		### Informing NM with complete statistics
		logger(myLogFile,rankMsg,LOG_STD,'Informing NM with simulation summary')
		simulationSummary = [myOriginalFuel,
							 myCooperatedFuel,
							 myQOfClusters,
							 myClusteredDuration*TIME_STEP,
							 sorted(myClusteredFlights),
							 bytesSent,
							 bytesReceived,
							 sendingTime,
							 receivingTime,
							 qOfMSGSent,
							 qOfMSGReceived,
							 bytesClusteredSent,
							 bytesClusteredReceived,
							 sendingClusteredTime,
							 receivingClusteredTime,
							 qOfClusteredMSGSent,
							 qOfClusteredMSGReceived]
		sendMPIMsg(0,simulationSummary,SIM_SUMARY_TAG)
		slavesComm.Barrier()
		########################################################################################

		########################################################################################
		### Writing HPC trajectory file
		writeTrajectoryFile()
		########################################################################################
	##################################################################################################################################################

	##################################################################################################################################################
	### Finishing
	logger(myLogFile,rankMsg,LOG_STD,'Finishing simulation')
	finishClock()
	finishSim()
	comm.Barrier() ## Check for the flights to finish
	if rank == 0:
		logger(myLogFile,rankMsg,LOG_STD,'Computing performance file')
		wrapIT(rankMsg,outputFolder, size)
	logger(myLogFile,rankMsg,LOG_STD,'I am done :)')
	##################################################################################################################################################

if __name__ == "__main__":

	"""
	Parallel cooperative flights
	"""
	main()
