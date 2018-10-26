import os
import sys
import traci
import argparse
from sumolib import checkBinary
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-s", "--sumocfg", help="input the filename of the SUMO config file")

args = parser.parse_args()
sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, "-c", args.sumocfg]
traci.start(sumoCmd)
step = 0
numVehicles = []
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    for light_id in traci.trafficlight.getIDList():
        for lane_id in traci.trafficlight.getControlledLanes(light_id):
            numVehicles.append(traci.lane.getLastStepVehicleNumber(lane_id))
        print(traci.trafficlight.getControlledLinks(light_id))
        #TODO: get all controlled links, sum up cars in the lanes that are currently green and change timings based on that
        #TODO: switch phases once some threshold of cars in other lanes is reached or there are few cars in green lanes
    step += 1
traci.close()