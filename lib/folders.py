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

######################################

### Imports from software modules
######################################

###############################################################################################################################
###############################################################################################################################

def createFolders(folders):

	"""
	Create folders
	"""
	for folder in folders: os.popen('mkdir -p '+folder)

###############################################################################################################################
###############################################################################################################################
