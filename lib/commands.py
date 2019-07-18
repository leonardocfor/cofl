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

import subprocess

######################################

### Imports from software modules
######################################

###############################################################################################################################
###############################################################################################################################

def executeCommand(command,args='',console=True):

	"""
	Execute command
	"""
	try:
		result=subprocess.Popen([command,args],shell=console, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		stdout, stderr = result.communicate()
		exitcode = result.wait()
		output = [stdout, stderr, exitcode]
		return output

	except Exception as e: raise

def executeCommandInNode(ip,user,command):

	"""
	Execute command in a node
	"""
	try:
		command = 'ssh '+user+'@'+ip+' -C "'+command+'"'
		return executeCommand(command,'',True)

	except Exception as e: raise

###############################################################################################################################
###############################################################################################################################
