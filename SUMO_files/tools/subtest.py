import os
import sys
import argparse


def average(in_list):
    return sum(in_list) / len(in_list) if in_list else 0


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
parser.add_argument("--max-wait", type=int, default=30,
                    help="Optional: 30 by default, maximum time before mandatory phase change")
parser.add_argument("--min-wait", type=int, default=5,
                    help="Optional: 5 by default, minimum time before phase can change")
parser.add_argument("--use-lane-max", default=False, action="store_true", help="Optional: False by default. If true, "
                                                                               "traffic light looks at lane with most cars when determining timings")
parser.add_argument("--no-red-lane-check", default=False, action="store_true",
                    help="Optional: False by default, if true"
                         " program does not look at red lanes to determine switch times")
parser.add_argument("-w", "--weight", type=int, default=10,
                    help="Optional: 10 by default, each car in  a lane represents "
                         "this many seconds to the light.")

args = parser.parse_args()
if args.gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')
sumoCmd = [sumoBinary, "-c", args.sumocfg]
traci.start(sumoCmd)
step = 0

lane_indices = {}
print("Building lane indices")

current_wait = {light_id: 0 for light_id in traci.trafficlight.getIDList()}
for light_id in traci.trafficlight.getIDList():
    num_vehicles = {}
    for lane_id in traci.trafficlight.getControlledLanes(light_id):
        traci.lane.subscribe(lane_id, [traci.constants.LAST_STEP_VEHICLE_NUMBER])
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    for light_id in traci.trafficlight.getIDList():
        num_vehicles = {}
        for lane_id in traci.trafficlight.getControlledLanes(light_id):
            vehicles = traci.lane.getSubscriptionResults(lane_id)[traci.constants.LAST_STEP_VEHICLE_NUMBER]
            print(vehicles)
    step += 1
    print("-------STEP %d OVER-------" % step)
traci.close()
