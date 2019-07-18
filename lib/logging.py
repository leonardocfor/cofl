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

######################################

###############################################################################################################################
###############################################################################################################################

def logger(logFile,rankMsg,linetype,line):
	"""
	Logging messages
	"""
	log=open(logFile,'a')
	log.write(linetype+' '+line+'\n')
	log.close()
	print(rankMsg+line)

###############################################################################################################################
###############################################################################################################################
