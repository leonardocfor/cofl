#!/usr/bin/env python
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

"""
eSO6 data fields
"""

SEGMENT_ID=0
DEPARTURE=1
ARRIVAL=2
AIRCRAFT=3
SEGMENT_TIME_INIT=4
SEGMENT_TIME_END=5
SEGMENT_LEVEL_INIT=6
SEGMENT_LEVEL_END=7
STATUS=8
CALLSIGN=9
SEGMENT_DATE_INIT=10
SEGMENT_DATE_END=11
SEGMENT_LAT_INIT=12
SEGMENT_LON_INIT=13
SEGMENT_LAT_END=14
SEGMENT_LON_END=15
FLIGHT_ID=16
SEQUENCE=17
SEGMENT_LENGTH=18
SEGMENT_PARITY=19
SEGMENT_GROUND_SPEED=20 # [kt]
SEGMENT_TRACK=21 # [degrees]
SEGMENT_ROC=22 # [ft/min]
SEGMENT_FUEL=23 # [Kg]
SEGMENT_CI=24 # [Kg/min]
SEGMENT_ROUTE_CHARGES=25 # [Eur]
SEGMENT_TRAJ_TYPE=26
