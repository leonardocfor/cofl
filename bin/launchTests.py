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

######################################

### Imports from software modules
from cofl.etc.info import COFL_SW, TC_TEMPLATE, LAUNCHER_SCRIPT, TEST_CASE_PREFIX, DATA_ROOT_FOLDER, TRAJ_FOLDER
from cofl.etc.info import HPC_TRAJ_FOLDER, OUTPUT_FOLDER, LOGS_FOLDER, LINES_TC_TEMPLATE, INIT_LINES_LAUNCHER
from cofl.lib.folders import createFolders
from cofl.lib.split import splitESO6File, selectiveSplitESO6File
from cofl.lib.ioFiles import modifyFile
######################################

###############################################################################################################################
###############################################################################################################################

def createTCDataSpace(nm,fl):

	"""
	Create testcase data space
	"""
	print(rankMsg+' Creating data space for testcase NM = '+str(nm)+', Flights = '+str(fl))
	tcID = date+'_'+hour+'_'+str(nm)+'NM_'+str(fl)+'FL'
	tcFolder = DATA_ROOT_FOLDER+'/'+scenario+'/'+tcID
	trajectoriesFolder=tcFolder+'/'+TRAJ_FOLDER
	hpcTrajectoriesFolder=tcFolder+'/'+HPC_TRAJ_FOLDER
	outputFolder=tcFolder+'/'+OUTPUT_FOLDER
	logsFolder=tcFolder+'/'+LOGS_FOLDER
	folders=[tcFolder, trajectoriesFolder, hpcTrajectoriesFolder, outputFolder, logsFolder]
	createFolders(folders)
	return trajectoriesFolder

def editTemplate(tcFile,tcLog,nm,fl):

	"""
	Editing template
	"""
	os.popen('cp '+TC_TEMPLATE+' '+tcFile)
	print(rankMsg+' Editting template for testcase NM = '+str(nm)+', Flights = '+str(fl))
	print(rankMsg+' Template saved at '+tcFile)
	replaceLines = [
		'<id>'+date+'_'+hour+'_'+str(nm)+'NM_'+str(fl)+'FL'+'</id>',
		'<flights>'+str(fl)+'</flights>',
		'<scenario>'+scenario+'</scenario>',
		'<model>'+model+'</model>',
		'<grouping>'+grouping+'</grouping>',
		'<radius>'+str(nm)+'</radius>',
		'<alonefuelparameter>'+alonefuelparameter+'</alonefuelparameter>',
		'<coopfuelparameter>'+coopfuelparameter+'</coopfuelparameter>',
		'<approachedDistance>'+approachedDistance+'</approachedDistance>',
		'<infrastructureFile>'+infrastructureFile+'</infrastructureFile>',
		'<log>'+tcLog+'</log>'
	]

	for searchLine, replaceLine in zip(LINES_TC_TEMPLATE, replaceLines): modifyFile(tcFile,searchLine,replaceLine)

def readXML():

	"""
	Reading input XML file
	"""
	global testsFolder, infrastructureFile
	global minNM, intervalSizeNM, maxNM, minFlights, maxFlights, airport, departure
	global date, hour, eso6, scenario, model, grouping, alonefuelparameter, coopfuelparameter, approachedDistance
	try:
		### Simulation parameters
		tree=ET.parse(testsXML)
		root=tree.getroot()
		testsFolder = root.find('testsFolder').text
		if testsFolder is None: print(rankMsg+' Incomplete parameters -- testsFolder'); sys.exit(1)
		infrastructureFile = root.find('infrastructureFile').text
		if infrastructureFile is None: print(rankMsg+' Incomplete parameters -- infrastructureFile'); sys.exit(1)
		minNM = root.find('minNM').text
		if minNM is None: print(rankMsg+' Incomplete parameters -- minNM'); sys.exit(1)
		intervalSizeNM = root.find('intervalSizeNM').text
		if intervalSizeNM is None: print(rankMsg+' Incomplete parameters -- intervalSizeNM'); sys.exit(1)
		maxNM = root.find('maxNM').text
		if maxNM is None: print(rankMsg+' Incomplete parameters -- maxNM'); sys.exit(1)
		minFlights = root.find('minFlights').text
		if minFlights is None: print(rankMsg+' Incomplete parameters -- minFlights'); sys.exit(1)
		maxFlights = root.find('maxFlights').text
		if maxFlights is None: print(rankMsg+' Incomplete parameters -- maxFlights'); sys.exit(1)
		airport = root.find('airport').text
		if airport is None: print(rankMsg+' Incomplete parameters -- airport'); sys.exit(1)
		departure = root.find('departure').text
		if departure is None: print(rankMsg+' Incomplete parameters -- departure'); sys.exit(1)
		date = root.find('date').text
		if date is None: print(rankMsg+' Incomplete padatetimerameters -- date'); sys.exit(1)
		hour = root.find('hour').text
		if hour is None: print(rankMsg+' Incomplete padatetimerameters -- hour'); sys.exit(1)
		eso6 = root.find('eso6').text
		if eso6 is None: print(rankMsg+' Incomplete parameters -- eso6'); sys.exit(1)
		scenario = root.find('scenario').text
		if scenario is None: print(rankMsg+' Incomplete parameters -- scenario'); sys.exit(1)
		model = root.find('model').text
		if model is None: print(rankMsg+' Incomplete parameters -- model'); sys.exit(1)
		grouping = root.find('grouping').text
		if grouping is None: print(rankMsg+' Incomplete parameters -- grouping'); sys.exit(1)
		alonefuelparameter = root.find('alonefuelparameter').text
		if alonefuelparameter is None: print(rankMsg+' Incomplete parameters -- alonefuelparameter'); sys.exit(1)
		coopfuelparameter = root.find('coopfuelparameter').text
		if coopfuelparameter is None: print(rankMsg+' Incomplete parameters -- coopfuelparameter'); sys.exit(1)
		approachedDistance = root.find('approachedDistance').text
		if approachedDistance is None: print(rankMsg+' Incomplete parameters -- approachedDistance'); sys.exit(1)
		minNM = int(minNM)
		intervalSizeNM = int(intervalSizeNM)
		maxNM = int(maxNM)
		minFlights = int(minFlights)
		maxFlights = int(maxFlights)
		if departure == 'true': departure = True
		else: departure = False
		####################################################################################
	except Exception, e: raise

def setOriginalTrajectories(trajectoriesFolder,nm,fl):

	"""
	Setting original trajectories
	"""
	print(rankMsg+' Setting original trajectories for testcase NM = '+str(nm)+', Flights = '+str(fl))
	sys.stdout = open(os.devnull, "w")
	if airport == 'NA': splitESO6File(rankMsg, eso6, str(fl), trajectoriesFolder)
	else: selectiveSplitESO6File(rankMsg, airport, departure, eso6, str(fl), trajectoriesFolder)
	sys.stdout = sys.__stdout__
	trajectoriesFiles = os.listdir(trajectoriesFolder)
	print(rankMsg+' Quantity of trajectory files is '+str(len(trajectoriesFiles)))

def updateLauncherScript(tcFile,tcLog,fl):

	"""
	Updating launcher script
	"""

	launcher = open(launchScript,'a')
	line = 'mpirun -np '+str(fl+1)+' --hostfile '+infrastructureFile+' python '+COFL_SW+' '+tcFile+' &> '+tcLog
	launcher.write(line+'\n')
	launcher.write('sleep 20'+'\n')
	launcher.close()

###############################################################################################################################
###############################################################################################################################

def main():


	global testsXML, rankMsg, templatesFolder, runninglogsFolder, launchScript

	rankMsg = '[Rank 0 msg]:'
	if len(sys.argv) != 2: print('Only XML template required'); sys.exit(0)
	testsXML=sys.argv[1]
	readXML()
	templatesFolder = testsFolder+'/templates'
	runninglogsFolder = testsFolder+'/logs'
	os.popen('mkdir -p '+templatesFolder+' '+runninglogsFolder)
	launchScript = testsFolder+'/'+LAUNCHER_SCRIPT
	launcher = open(launchScript,'a')
	for line in INIT_LINES_LAUNCHER: launcher.write(line+'\n')
	launcher.close()

	try:

		tCPrefix=TEST_CASE_PREFIX+airport+'_' if airport != 'NA' else TEST_CASE_PREFIX
		for nm in range(minNM, maxNM+1, intervalSizeNM):
			i = 0
			for fl in range(minFlights, maxFlights+1):
				print('-----------------------------------------------------------------------------------')
				fltc=minFlights*pow(2,i)
				tcFile = templatesFolder+'/'+tCPrefix+str(nm)+'_'+str(fltc)+'.xml'
				tcLog =  runninglogsFolder+'/'+tCPrefix+str(nm)+'_'+str(fltc)+'.log'
				trajectoriesFolder = createTCDataSpace(nm,fltc)
				setOriginalTrajectories(trajectoriesFolder,nm,fltc)
				editTemplate(tcFile,tcLog,nm,fltc)
				updateLauncherScript(tcFile,tcLog,fltc)
				print('-----------------------------------------------------------------------------------')
				if fltc == maxFlights: break
				i+=1

		os.popen('chmod +x '+launchScript)

	except Exception, e: raise


if __name__ == "__main__":

	"""
	Parallel cooperative flights
	"""
	main()
