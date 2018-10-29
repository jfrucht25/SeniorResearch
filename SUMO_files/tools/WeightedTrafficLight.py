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
parser.add_argument("--nogui", default=True, action="store_true", help="Optional: True by default, write 0 for no GUI",)

args = parser.parse_args()
if args.nogui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, "-c", args.sumocfg]
traci.start(sumoCmd)
step = 0
num_vehicles = {}
lane_indices = {}
print("Building lane indices")
for light_id in traci.trafficlight.getIDList():
    temp_dict = {}
    for link_tuple in traci.trafficlight.getControlledLinks(light_id):
        link_tuple = link_tuple[0]
        index = link_tuple[2].split("_")[1][0]
        print(index)
        lane = traci.trafficlight.getControlledLanes(light_id)[int(index)]
        if lane in temp_dict:
            temp_dict[lane].append(index)
        else:
            temp_dict[lane] = [index]
    lane_indices[light_id] = temp_dict
print(lane_indices)
while traci.simulation.getMinExpectedNumber() > 0 or step > 100:
    traci.simulationStep()
    step += 1
    for light_id in traci.trafficlight.getIDList():
        for lane_id in traci.trafficlight.getControlledLanes(light_id):
            num_vehicles[lane_id] = traci.lane.getLastStepVehicleNumber(lane_id)
        print(traci.trafficlight.getRedYellowGreenState(light_id))
        print(traci.trafficlight.getControlledLanes(light_id))
        print(traci.trafficlight.getControlledLinks(light_id))
        print(traci.trafficlight.getPhase(light_id))
        cars_in_green = [num_vehicles[k] for k in num_vehicles
                            if traci.trafficlight.getRedYellowGreenState(light_id)[lane_indices[light_id][k]] in "Gg"]

    print("\n".join(["%s cars in lane %s" % (num_vehicles[k], k) for k in num_vehicles.keys()]))
    print("-------STEP %d OVER-------" % step)
        #print(traci.trafficlight.getControlledLinks(light_id))

        #TODO: get all controlled links, sum up cars in the lanes that are currently green and change timings based on that
        #TODO: switch phases once some threshold of cars in other lanes is reached or there are few cars in green lanes
    step += 1
traci.close()