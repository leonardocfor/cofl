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
from multiprocessing import Process

######################################

### Imports from software modules
from cofl.etc.info import LOG_STD, LOG_ERR
from cofl.lib.commands import executeCommand, executeCommandInNode
from cofl.lib.logging import logger
######################################

###############################################################################################################################
###############################################################################################################################

def calculateOperationTime(initTime,endTime):

	"""
	Returns operation time [secs]
	initTime and endTime --> secs
	"""
	return endTime - initTime

def checkBandwidth(nodes,rankMsg,myLogFile):
	"""
	Checking average bandwidth between nodes in the cluster
	"""
	try:
		qOfNodes = len(nodes)
		protocols = ['UDP','TCP']
		user=os.popen('whoami').read()[0:-1]
		IPS = []
		for node in nodes: IPS.append(os.popen("cat /etc/hosts | grep "+node+" | tail -1 | awk '{print $1}'").read()[0:-1])

		logger(myLogFile,rankMsg,LOG_STD,'Checking average bandwith between nodes in COFL simulation cluster')
		averageBandwidth={'UDP':0.0, 'TCP':0.0}
		for protocol in protocols:
			bandwidth = 0.0
			for IP in IPS:
				for otherIP in filter(lambda otherIP: otherIP!=IP, IPS):
					server=IP
					client=otherIP
					commandServer='iperf -s'
					commandClient='iperf -c'+' '+server
					if(protocol=='UDP'): [commandServer,commandClient]=[x+y for x,y in zip([commandServer,commandClient],[' -u',' -u | grep sec'])]
					proc=Process(target=executeCommandInNode,args=(server,user,commandServer,))
					proc.daemon=True
					proc.start()
					executeCommand('sleep 2','',True)
					out=executeCommandInNode(client,user,commandClient)[0]
					bValue=out.split(' ')[-2]
					units=out.split(' ')[-1][0:-1]
					if(units=='Gbits/sec'): bValue=float(bValue)*1024
					if(units=='Kbits/sec'): bValue=float(bValue)/1024
					bandwidth+=float(bValue)
					killProcess(user,server,'iperf')
					killProcess(user,server,'iperf')
					executeCommandInNode(server,user,'killall iperf')
					logger(myLogFile,rankMsg,LOG_STD,'Bandwith between '+str(IP)+' and '+str(otherIP)+', protocol '+str(protocol)+' = '+str(bValue)+' [MB]')
			averageBandwidth[protocol] = bandwidth / (qOfNodes*(qOfNodes-1))
		logger(myLogFile,rankMsg,LOG_STD,'Average bandwith between nodes in COFL simulation cluster = '+str(averageBandwidth)+' [MB]')
		return averageBandwidth

	except Exception as e: raise

def checkLatency(nodes,rankMsg,myLogFile):
	"""
	Checking average latency between nodes in the cluster
	"""

	try:

		qOfNodes = len(nodes)
		user=os.popen('whoami').read()[0:-1]
		IPS = []
		for node in nodes: IPS.append(os.popen("cat /etc/hosts | grep "+node+" | tail -1 | awk '{print $1}'").read()[0:-1])
		logger(myLogFile,rankMsg,LOG_STD,'Checking average latency between nodes in COFL simulation cluster')
		averageLatency=0.0
		for IP in IPS:
			for otherIP in filter(lambda otherIP: otherIP!=IP, IPS):
				lat=executeCommand('ssh '+user+'@'+otherIP+' -C "ping -c 4 '+IP+'" | grep from | awk {\'print $7\'} | cut -d \'=\' -f2 ','',True)[0][0:-1].split('\n')
				latency=sum([float(x) for x in lat])/len(lat)
				averageLatency+=float(latency)
				logger(myLogFile,rankMsg,LOG_STD,'Latency between '+str(otherIP)+' and '+str(IP)+' = '+str(latency)+' [mS]')

		averageLatency=averageLatency / (qOfNodes*(qOfNodes-1))
		logger(myLogFile,rankMsg,LOG_STD,'Average latency between nodes in COFL simulation cluster = '+str(averageLatency)+' [mS]')
		return averageLatency

	except Exception as e: raise

def getBytes(data):

	"""
	Returns size of data [bytes]
	"""
	return sys.getsizeof(data)

def killProcess(user,server,command):

	"""
	Kill a process in a remote machine
	"""
	try:
		process = executeCommand('ssh '+user+'@'+server+' -C "ps aux | grep '+command+' | head -1 | awk {\'print $2\'}"','',True)[0][0:-1]
		executeCommand('ssh '+user+'@'+server+' -C "kill -9 '+process+'"','',True)
	except Exception as e: raise

###############################################################################################################################
###############################################################################################################################
