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

	folder ='/mnt/HDDextra2TB/cofl/scenarios/S2/'
	subFolders = os.listdir(folder)
	subFolders=['/mnt/HDDextra2TB/cofl/scenarios/S2/'+f for f in subFolders]
	clustersInfoTestCases ={}
	for folder in subFolders:

		command = 'ls '+folder+'/output/summary*'
		out = executeCommand(command)
		if out[2] == 0:
			temp=folder.split('/')[6].split('_')
			idTC = temp[2]+'-'+temp[3]
			clustersInfoTestCases[idTC] = {}
			clustersInfoTestCases[idTC]['ATST'] = {}
			clustersInfoTestCases[idTC]['CS'] = {}
			logsFolder = folder+'/logs'
			clustersSizes = []
			clustersATST = []
			lines = os.popen("cat "+logsFolder+"/0.log | grep 'Clusters calculated by Network Manager: '").read().split('\n')
			for line in lines:
				clustersline='{'+line.replace("[STD] Clusters calculated by Network Manager: ", "")[0:-1].replace(']','],')[0:-1]+'}'
				clusters = eval(clustersline)
				clusteredFlights = []
				atst = 0
				for flight in clusters:
					if flight not in clusteredFlights and len(clusters[flight])>0:
						clustersSizes.append(len(clusters[flight]))
						atst +=1
						for f in clusters[flight]: clusteredFlights.append(f)
				clustersATST.append(atst)
			maxSize = max(clustersSizes) if len(clustersSizes) > 0 else 0
			minSize = min(clustersSizes) if len(clustersSizes) > 0 else 0
			avgSize = float(sum(clustersSizes))/len(clustersSizes) if len(clustersSizes) > 0 else 0
			clustersInfoTestCases[idTC]['CS']['max'] = maxSize
			clustersInfoTestCases[idTC]['CS']['min'] = minSize
			clustersInfoTestCases[idTC]['CS']['avg'] = avgSize
			maxATST = max(clustersATST)
			minATST = min(clustersATST)
			avgATST = float(sum(clustersATST))/len(clustersATST)
			clustersInfoTestCases[idTC]['ATST']['max'] = maxATST
			clustersInfoTestCases[idTC]['ATST']['min'] = minATST
			clustersInfoTestCases[idTC]['ATST']['avg'] = avgATST

if __name__ == "__main__":

	"""
	Parallel cooperative flights
	"""
	main()

"""

5NM-16FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
5NM-32FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
5NM-64FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
5NM-128FL = {'CS': {'max': 2, 'avg': 2.0, 'min': 2}, 'ATST': {'max': 2, 'avg': 1.0208116545265349, 'min': 0}}
5NM-256FL = {'CS': {'max': 3, 'avg': 2.0058833417381075, 'min': 2}, 'ATST': {'max': 6, 'avg': 2.390116512655685, 'min': 0}}

10NM-16FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
10NM-32FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
10NM-64FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
10NM-128FL = {'CS': {'max': 2, 'avg': 2.0, 'min': 2}, 'ATST': {'max': 2, 'avg': 1.0582226762002043, 'min': 0}}
10NM-256FL = {'CS': {'max': 4, 'avg': 2.2819993771410774, 'min': 2}, 'ATST': {'max': 6, 'avg': 2.52437106918239, 'min': 0}}

15NM-16FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
15NM-32FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
15NM-64FL = {'CS': {'max': 2, 'avg': 2.0, 'min': 2}, 'ATST': {'max': 1, 'avg': 0.9411764705882353, 'min': 0}}
15NM-128FL = {'CS': {'max': 2, 'avg': 2.0, 'min': 2}, 'ATST': {'max': 2, 'avg': 1.1869585043319653, 'min': 0}}
15NM-256FL = {'CS': {'max': 4, 'avg': 2.32294751806658, 'min': 2}, 'ATST': {'max': 6, 'avg': 2.3617795187465025, 'min': 0}}

20NM-16FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
20NM-32FL = {'CS': {'max': 0, 'avg': 0, 'min': 0}, 'ATST': {'max': 0, 'avg': 0.0, 'min': 0}}
20NM-64FL = {'CS': {'max': 2, 'avg': 2.0, 'min': 2}, 'ATST': {'max': 1, 'avg': 0.9411764705882353, 'min': 0}}
20NM-128FL = {'CS': {'max': 3, 'avg': 2.000739098300074, 'min': 2}, 'ATST': {'max': 2, 'avg': 1.2096557890031292, 'min': 0}}
20NM-256FL = {'CS': {'max': 4, 'avg': 2.438774560014899, 'min': 2}, 'ATST': {'max': 7, 'avg': 2.8320147679324896, 'min': 0}}



"""
