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
sys.path.insert(0,'/local')

######################################

### Imports from software modules
from cofl.lib.commands import executeCommand, executeCommandInNode
######################################

######################################################################################################################################################
######################################################################################################################################################



######################################################################################################################################################
######################################################################################################################################################

def main():

	tcFolder ='/mnt/HDDextra2TB/cofl/scenarios/S2/'
	subFolders = os.listdir(tcFolder)
	subFolders=['/mnt/HDDextra2TB/cofl/scenarios/S2/'+f for f in subFolders]
	clustersInfoTestCases ={}
	for folder in subFolders:
		temp=folder.split('/')[6].split('_')
		idTC = temp[2]+'-'+temp[3]
		print('Calculating testcase '+idTC)
		command = 'ls '+folder+'/output/summary*'
		out = executeCommand(command)
		if out[2] == 0:

			logsFolder = folder+'/logs'
			logs = os.listdir(logsFolder)
			logs.remove('0.log')
			logs=[logsFolder+'/'+f for f in logs]

			cruiseTimes = []
			for log in logs: cruiseTimes.append(int(os.popen("cat "+log+" | grep 'Cruise starts at time'").read().split()[5]))
			clustersInfoTestCases[idTC] = max(cruiseTimes) - min(cruiseTimes)
			print('Cruise duration is '+str(clustersInfoTestCases[idTC]))
		else: print('Test case not done')
	for tc in clustersInfoTestCases:
		print(tc+': '+str(clustersInfoTestCases[tc]))


if __name__ == "__main__":

	"""
	Parallel cooperative flights
	"""
	main()

"""
{'10NM-16FL': 46720,
'10NM-256FL': 109830,
'20NM-128FL': 109830,
'5NM-32FL': 65770,
'15NM-256FL': 109830,
'15NM-128FL': 109830,
'5NM-64FL': 87240,
'5NM-16FL': 46720,
'10NM-128FL': 109830,
'20NM-256FL': 109830,
'20NM-16FL': 46720,
'5NM-256FL': 109830,
'15NM-16FL': 46720, '5NM-128FL': 109830, '10NM-32FL': 65770, '10NM-64FL': 87240, '20NM-32FL': 65770, '20NM-64FL': 87240, '15NM-32FL': 65770, '15NM-64FL': 87240}


"""
