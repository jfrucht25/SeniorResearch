import os
import sys
import argparse
def average(in_list):
    return sum(in_list)/len(in_list) if in_list else 0
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from sumolib import checkBinary


parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-s", "--sumocfg", help="input the filename of the SUMO config file")
parser.add_argument("--gui", default=False, action="store_true", help="Optional: True by default, use for GUI")
parser.add_argument("--max-wait", default=30, help="Optional: 30 by default, maximum time before mandatory phase change")
parser.add_argument("--use-car-max", default=False, action="store_true", help="Optional: False by default. If true, "
                                        "traffic light looks at lane with most cars when determining timings")
parser.add_argument("-w", "--weight", default=10, help="Optional: 10 by default, each car in  a lane represents "
                                                       "this many seconds to the light.")


args = parser.parse_args()
if args.gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')
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
        index = int(link_tuple[2].split("_")[1][0])
        lane = traci.trafficlight.getControlledLanes(light_id)[int(index)]
        if lane in temp_dict:
            temp_dict[lane].append(index)
        else:
            temp_dict[lane] = [index]
    lane_indices[light_id] = temp_dict
print(lane_indices)
current_wait = {light_id: 0 for light_id in traci.trafficlight.getIDList()}
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1
    for light_id in traci.trafficlight.getIDList():
        for lane_id in traci.trafficlight.getControlledLanes(light_id):
            num_vehicles[lane_id] = traci.lane.getLastStepVehicleNumber(lane_id)
        print("\n")
        print(traci.trafficlight.getRedYellowGreenState(light_id))
        print(lane_indices[light_id])
        #print(traci.trafficlight.getControlledLanes(light_id))
        #print(traci.trafficlight.getControlledLinks(light_id))
        #print(traci.trafficlight.getPhase(light_id))
        print(num_vehicles)
        cars_in_green = {lane:num_vehicles[lane] for lane in num_vehicles.keys() for link in lane_indices[light_id][lane]
                            if traci.trafficlight.getRedYellowGreenState(light_id)[link] in "Gg"}
        print(cars_in_green)
        current_wait[light_id] += 1
        if current_wait[light_id] > args.max_wait:
            current_wait[light_id] = 0
            new_duration = 0
            reason = "the max duration of this phase was exceeded"
        else:
            new_duration = args.weight * (max(cars_in_green.values()) if args.use_car_max else average(cars_in_green.values()))
            if args.use_car_max:
                reason = "there are %d cars in lane %s" % (max(cars_in_green.values()), max(cars_in_green, key=cars_in_green.get))
            else:
                reason = "there are an average of %f cars in all green lanes" % (average(cars_in_green.values()))
        print("New duration set to %d because %s" % (new_duration, reason))
        traci.trafficlight.setPhaseDuration(light_id, new_duration)


    print("\n".join(["%s cars in lane %s" % (num_vehicles[k], k) for k in num_vehicles.keys()]))
    print("-------STEP %d OVER-------" % step)
        #print(traci.trafficlight.getControlledLinks(light_id))

        #TODO: add intelligent switching that looks at red lanes too and changes phase so that lanes with most cars are green
    step += 1
traci.close()
