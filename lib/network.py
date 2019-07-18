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

from networkx import DiGraph, shortest_path_length

######################################

### Imports from software modules
######################################

###############################################################################################################################
###############################################################################################################################

def addEdges(aircraftNetwork,clusters):

	"""
	Addings edges from clusters
	"""
	for flight in clusters:
		for otherFlight in filter(lambda otherFlight: otherFlight!=flight, clusters[flight]): aircraftNetwork.add_edge(flight,otherFlight)
	return aircraftNetwork

def calculateGRC(LRC):

	"""
	Calculate GRC (Global Reaching Centrality)
	"""
	nodes=len(LRC)
	max_LRC = max(LRC)
	GRC = 0.0
	for lrc in LRC: GRC+=(max_LRC-lrc)
	GRC = GRC / (nodes -1)
	return GRC

def calculateLRC(aircraftNetwork):

	"""
	Calculate LRC (Local Reaching Centrality)
	Nodes are the network manager (0) and live flights
	"""
	nodes = list(sorted(aircraftNetwork.nodes()))
	qOfAircraft = aircraftNetwork.number_of_nodes() -1
	LRC = []
	for node in nodes:
		shortestPathsFromNode = shortest_path_length(aircraftNetwork, source=node)
		LRC.append(float(len(shortestPathsFromNode)-1)/float(qOfAircraft))
	return LRC

def setNetwork(flights):

	"""
	Setting network and hierarchy
	"""
	aircraftNetwork = DiGraph()
	aircraftNetwork.add_nodes_from(flights)
	return aircraftNetwork

###############################################################################################################################
###############################################################################################################################
