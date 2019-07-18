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
##################################################################################################################################################
### Cooperative Flights -- HPRC -- Variables
COFL_HOME='' ## Fill in the root folder of the COFL software
COFL_SW = COFL_HOME+'/bin/hpccoopflying.py'
##################################################################################################################################################

##################################################################################################################################################
### Data space variables
DATA_ROOT_FOLDER='' ## Fill in to where you wish to store data
TRAJ_FOLDER='original'
HPC_TRAJ_FOLDER='hpc'
OUTPUT_FOLDER='output'
LOGS_FOLDER='logs'
##################################################################################################################################################

##################################################################################################################################################
### Templates and default files variables
TC_TEMPLATE = COFL_HOME+'/templates/tctemplate.xml'
TEST_CASE_PREFIX='tc_'
LAUNCHER_SCRIPT='launchHPC_COFL.sh'
RESULTS_FILE_BANNER='Current_time qOfCruiseFlights nmQOfClusters qOfClusters GRC'
COOPERATIVE_FLIGHTS_FILE_BANNER='Flight Cooperative_flights'
INIT_LINES=[
	'---------------------------------------------------------------------------',
	'---------------------------------------------------------------------------',
	'HPC cooperative flights',
 	'Developed by Leonardo Camargo Forero',
 	'Email: leonardo.camargo@upc.edu',
 	'2018',
 	'---------------------------------------------------------------------------',
 	'---------------------------------------------------------------------------']
LINES_TC_TEMPLATE=[
	'<id></id>',
	'<flights></flights>',
	'<scenario></scenario>',
	'<model></model>',
	'<grouping></grouping>',
	'<radius></radius>',
	'<alonefuelparameter></alonefuelparameter>',
	'<coopfuelparameter></coopfuelparameter>',
	'<approachedDistance></approachedDistance>',
	'<infrastructureFile></infrastructureFile>',
	'<log></log>']
INIT_LINES_LAUNCHER=[
	'#!/bin/bash',
	'# --------------------------------------------------------',
	'# HPC Cooperative Flights Tests launcher',
	'# Developped by Leonardo Camargo Forero, M.Sc',
	'# email: leonardo.camargo@upc.edu',
	'# 2018',
	'# --------------------------------------------------------']
DEFAULT_SUMMARY_LINES=[
	'Test case ID: ',
	'Scenario: ',
	'Quantity of aircraft: ',
	'MPI processes: ',
	'Quantity of nodes in the cluster: ',
	'Nodes: ',
	'Cooperatively flying model: ',
	'Clustering model: ',
	'Neighbouring radius [NM]: ',
	'Parameter for flying solo: ',
	'Parameter for flying cooperatively: ',
	'Joined distance [m]: ',
	'Total quantity of executed clusters: ',
	'Total quantity of possible clusters: ',
	'Cluster acceptance ratio: ',
	'Average GRC: ',
	'Max GRC: ',
	'Min GRC: ',
	'GRC updates: ',
	'Total fuel in original trajectory [Kg]: ',
	'Total fuel in HPC cooperative trajectory [Kg]: ',
	'Difference in fuel [Kg]: ',
	'Quantity of flights with fuel savings: ',
	'Flights with fuel savings: ',
	'Quantity of flights without fuel savings: ',
	'Flights without fuel savings: ',
	'Average quantity of clusters: ',
	'Maximum quantity of clusters: ',
	'Minimum quantity of clusters: ',
	'Average clustered time duration [s]: ',
	'Maximum clustered time duration [s]: ',
	'Minimum clustered time duration [s]: ',
	'Total bytes sent via MPI msgs [bytes]: ',
	'Average bytes sent via MPI msgs [bytes]: ',
	'Maximum bytes sent via MPI msgs [bytes]: ',
	'Minimum bytes sent via MPI msgs [bytes]: ',
	'Total bytes received via MPI msgs [bytes]: ',
	'Average bytes received via MPI msgs [bytes]: ',
	'Maximum bytes received via MPI msgs [bytes]: ',
	'Minimum bytes received via MPI msgs [bytes]: ',
	'Total time sending MPI msgs [s]: ',
	'Average time sending MPI msgs [s]: ',
	'Maximum time sending MPI msgs [s]: ',
	'Minimum time sending MPI msgs [s]: ',
	'Total time receiving MPI msgs [s]: ',
	'Average time receiving MPI msgs [s]: ',
	'Maximum time receiving MPI msgs [s]: ',
	'Minimum time receiving MPI msgs [s]: ',
	'Total quantity of MPI MSGs Sent: ',
	'Average quantity of MPI MSGs Sent: ',
	'Maximum quantity of MPI MSGs Sent: ',
	'Minimum quantity of MPI MSGs Sent: ',
	'Total quantity of MPI MSGs received: ',
	'Average quantity of MPI MSGs received: ',
	'Maximum quantity of MPI MSGs received: ',
	'Minimum quantity of MPI MSGs received: ',
	'Total bytes sent via MPI msgs withing clustered flights [bytes]: ',
	'Average bytes sent via MPI msgs withing clustered flights [bytes]: ',
	'Maximum bytes sent via MPI msgs withing clustered flights [bytes]: ',
	'Minimum bytes sent via MPI msgs withing clustered flights [bytes]: ',
	'Total bytes received via MPI msgs withing clustered flights [bytes]: ',
	'Average bytes received via MPI msgs withing clustered flights [bytes]: ',
	'Maximum bytes received via MPI msgs withing clustered flights [bytes]: ',
	'Minimum bytes received via MPI msgs withing clustered flights [bytes]: ',
	'Total time sending MPI msgs withing clustered flights [s]: ',
	'Average time sending MPI msgs withing clustered flights [s]: ',
	'Maximum time sending MPI msgs withing clustered flights [s]: ',
	'Minimum time sending MPI msgs withing clustered flights [s]: ',
	'Total time receiving MPI msgs withing clustered flights [s]: ',
	'Average time receiving MPI msgs withing clustered flights [s]: ',
	'Maximum time receiving MPI msgs withing clustered flights [s]: ',
	'Minimum time receiving MPI msgs withing clustered flights [s]: ',
	'Total quantity of MPI MSGs Sent withing clustered flights: ',
	'Average quantity of MPI MSGs Sent withing clustered flights: ',
	'Maximum quantity of MPI MSGs Sent withing clustered flights: ',
	'Minimum quantity of MPI MSGs Sent withing clustered flights: ',
	'Total quantity of MPI MSGs received withing clustered flights: ',
	'Average quantity of MPI MSGs received withing clustered flights: ',
	'Maximum quantity of MPI MSGs received withing clustered flights: ',
	'Minimum quantity of MPI MSGs received withing clustered flights: ']
##################################################################################################################################################

##################################################################################################################################################
### General variables
YEAR_PREFIX='20' ## Replace at the change of the century :P
TIME_ZONE='UTC'  ## Replace accordingly
##################################################################################################################################################

##################################################################################################################################################
### Logging variables
LOG_STD='[STD]'
LOG_ERR='[ERR]'
##################################################################################################################################################

##################################################################################################################################################
### MPI message exchange TAGs
STATUS_TAG = 1
TELEMETRY_TAG = 2
NM_CLUSTERS_TAG = 3
AC_SLAVES_TAG = 4
CLUSTERED_TAG = 5
APPROACHING_TAG = 6
VICSEK_TAG = 7
SIM_SUMARY_TAG = 8
##################################################################################################################################################
