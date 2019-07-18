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

from mpi4py import MPI

######################################

### Imports from software modules
######################################

###############################################################################################################################
###############################################################################################################################

def receiveMPIMsg(comm,src=MPI.ANY_SOURCE,t=MPI.ANY_TAG): ### DONE

	"""
	Sending MPI messages
	"""
	dataDict={}
	status = MPI.Status()
	data=comm.recv(source=src, tag=t, status=status)
	dataDict['data']=data
	dataDict['sender']=int(status.Get_source())
	return dataDict

def sendMPIMsg(comm,destination,data): ### DONE

	"""
	Sending MPI messages
	"""
	comm.send(data, dest=destination)

###############################################################################################################################
###############################################################################################################################
