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
import xml.etree.ElementTree as ET
from calendar import timegm
from datetime import datetime
import fileinput
from time import gmtime
from timeit import default_timer

######################################

### Imports from software modules
from cofl.etc.info import RESULTS_FILE_BANNER, INIT_LINES, COOPERATIVE_FLIGHTS_FILE_BANNER, DEFAULT_SUMMARY_LINES
from cofl.etc.eSO6DataFields import SEGMENT_DATE_INIT, SEGMENT_DATE_END, SEGMENT_TIME_INIT, SEGMENT_TIME_END
from cofl.lib.pctime import calculateSecFromEpoch
######################################

###############################################################################################################################
###############################################################################################################################

def modifyFile(f,searchExp,replaceExp):

	"""
	Modify a file where searchExp is found
	args:
		file = The file to open in write mode
		searchExp: Lines matching this expression will be modified with
		replaceExp
	"""
	try:

		for line in fileinput.input(f, inplace=1):
			if searchExp in line: line = line.replace(searchExp,replaceExp)
			sys.stdout.write(line)

	except Exception, e: raise

def readInfrastructureFile(infrastructureFile):

	"""
	Reading infrastructure file
	"""
	machines=[]
	for line in open(infrastructureFile): machines.append(line.split()[0])
	return machines, len(machines)

def readESO6Trajectory(trajectoryFile): ### DONE

	"""
	Reading trajectory eS06 file
	trajectory [list]
	initTime [s]
	endTime [s]
	"""

	trajectory=[]
	for line in open(trajectoryFile): trajectory.append(line.split())
	firstLine=os.popen('head -1 '+trajectoryFile).read().split()
	endLine=os.popen('tail -1 '+trajectoryFile).read().split()
	initTime=calculateSecFromEpoch(firstLine[SEGMENT_DATE_INIT],firstLine[SEGMENT_TIME_INIT])
	endTime=calculateSecFromEpoch(endLine[SEGMENT_DATE_END],endLine[SEGMENT_TIME_END])
	return trajectory, initTime, endTime

def readXMLInput(rankMsg,testCaseFile):

	"""
	Reading input XML file
	"""
	try:
		### Simulation parameters
		tree=ET.parse(testCaseFile)
		root=tree.getroot()
		tcID = root.find('id').text
		if tcID is None: print(rankMsg+' Incomplete parameters -- id'); sys.exit(1)
		flightsQ = root.find('flights').text
		if flightsQ is None: print(rankMsg+' Incomplete parameters -- flights'); sys.exit(1)
		scenario = root.find('scenario').text
		if scenario is None: print(rankMsg+' Incomplete parameters -- scenario'); sys.exit(1)
		model = root.find('model').text
		if model is None: print(rankMsg+' Incomplete parameters -- model'); sys.exit(1)
		grouping = root.find('grouping').text
		if grouping is None: print(rankMsg+' Incomplete parameters -- grouping'); sys.exit(1)
		radius = root.find('radius').text
		if radius is None: print(rankMsg+' Incomplete parameters -- radius'); sys.exit(1)
		alonefuelparameter = root.find('alonefuelparameter').text
		if alonefuelparameter is None: print(rankMsg+' Incomplete parameters -- alonefuelparameter'); sys.exit(1)
		coopfuelparameter = root.find('coopfuelparameter').text
		if coopfuelparameter is None: print(rankMsg+' Incomplete parameters -- coopfuelparameter'); sys.exit(1)
		approachedDistance = root.find('approachedDistance').text
		if approachedDistance is None: print(rankMsg+' Incomplete parameters -- approachedDistance'); sys.exit(1)
		infrastructureFile = root.find('infrastructureFile').text
		if infrastructureFile is None: print(rankMsg+' Incomplete parameters -- infrastructureFile'); sys.exit(1)
		log = root.find('log').text
		if log is None: print(rankMsg+' Incomplete parameters -- log'); sys.exit(1)
		####################################################################################

		return tcID, flightsQ, scenario, model, grouping, radius, alonefuelparameter, coopfuelparameter, approachedDistance, infrastructureFile, log


	except Exception, e: raise

def wrapIT(rankMsg,outputFolder, size):

	"""
	Wrapping things up
	"""

	performanceFile=outputFolder+'/0_perf.txt'
	pFile=open(performanceFile,'a')
	clockTimes={}
	computingTimes={}
	for i in range(1,size):
		performanceFileRank=outputFolder+'/'+str(i)+'_perf.txt'
		print(rankMsg+' Processing performance file '+performanceFileRank)
		for line in open(performanceFileRank):
			if 'Hostname' in line:
				hostname=line.split()[1]
				if hostname not in clockTimes: clockTimes[hostname]=0.0
				if hostname not in computingTimes: computingTimes[hostname]=0.0
			elif 'Clock' in line: clockTimes[hostname]+=float(line.split(':')[1].split()[0])
			elif 'Computing' in line: computingTimes[hostname]+=float(line.split(':')[1].split()[0])
			pFile.write(line[0:-1]+'\n')

	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.write('Simulation summary \n')
	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.write('Total clock times per hostname\n')
	for hostname in clockTimes: pFile.write(hostname+' '+str(clockTimes[hostname])+'\n')
	pFile.write('Slowest machine: '+str(max(clockTimes, key=clockTimes.get))+'\n')
	pFile.write('Fastest machine: '+str(min(clockTimes, key=clockTimes.get))+'\n')
	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.write('Total computing times per hostname\n')
	for hostname in computingTimes: pFile.write(hostname+' '+str(computingTimes[hostname])+'\n')
	pFile.write('Slowest machine: '+str(max(computingTimes, key=computingTimes.get))+'\n')
	pFile.write('Fastest machine: '+str(min(computingTimes, key=computingTimes.get))+'\n')
	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.close()
	os.popen('mv '+performanceFile+' '+outputFolder+'/performance.txt')
	os.popen('rm '+outputFolder+'/*_perf.txt')

def writeCooperativeFlightsFile(cooperativeFlightsFile,flightsClusteredFlights=None,init=True):

	"""
	Writing cooperative flights file
	"""
	cFFile = open(cooperativeFlightsFile,"a")
	if init: cFFile.write(COOPERATIVE_FLIGHTS_FILE_BANNER+'\n')
	else:
		for flight in flightsClusteredFlights:
			flightCoopFlights = ''
			for otherFlight in flightsClusteredFlights[flight]: flightCoopFlights+=str(otherFlight)+','
			cFFile.write(str(flight)+' '+flightCoopFlights[0:-1]+'\n')
	cFFile.close()

def writeResultsFile(resultsFile, currTime=None, qOfCruiseFlights=None, nmQOfClusters=None, qOfClusters=None, GRC=None, init=True):

	"""
	Write the clusters file at timestep
	"""

	cFile=open(resultsFile,'a')
	if init: cFile.write(RESULTS_FILE_BANNER+'\n')
	else:
		resultsLine=''
		resultsLine+=str(currTime)+' '+str(qOfCruiseFlights)+' '+str(nmQOfClusters)+' '+str(qOfClusters)+' '+str(GRC)
		cFile.write(resultsLine+'\n')
	cFile.close()

def writePerformanceFile(performanceFile, rank, tcID, size, qOfMachines, dateTime, init=True, secsFromEpoch=None, cTimes=None):

	"""
	Writing performance i.e. times file
	"""
	pFile=open(performanceFile,'a')
	if init:
		if rank==0:
			for line in INIT_LINES: pFile.write(line+'\n')
			pFile.write('Testcase: '+tcID+'\n')
			pFile.write('Quantity of flights: '+str(size-1)+'\n')
			pFile.write('Quantity of machines: '+str(qOfMachines)+'\n')
			pFile.write('Quantity of parallel processes: '+str(size+1)+'\n')
		pFile.write('---------------------------------------------------------------------------'+'\n')
		pFile.write('Rank: '+str(rank)+'\n')
		pFile.write('Hostname: '+os.popen('hostname').read()[0:-1]+'\n')
		pFile.write('Simulation init time: '+str(dateTime)+'\n')
	else:
		pFile.write('Simulation end time: '+str(dateTime)+'\n')
		if secsFromEpoch is not None: pFile.write('Clock total time [s]: '+str(secsFromEpoch[1]-secsFromEpoch[0])+'\n')
		if cTimes is not None: pFile.write('Computing total time [s]: '+str(cTimes[1]-cTimes[0])+'\n')
		pFile.write('---------------------------------------------------------------------------'+'\n')
	pFile.close()

def writeSummaryFile(summaryFile,summaryResults):

	"""
	Writing simulation summary
	"""
	sFile = open(summaryFile,"w")
	summaryLines = INIT_LINES + [''.join(map(str, i)) for i in zip(DEFAULT_SUMMARY_LINES, summaryResults)]
	for line in summaryLines: sFile.write(line+'\n')
	sFile.close()

###############################################################################################################################
###############################################################################################################################
