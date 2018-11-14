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


def calc_cars_in_red_green(cars_in_lanes_dict, light):
    green = {}
    red = {}
    for l in cars_in_lanes_dict.keys():
        for link in lane_indices[light][l]:
            if traci.trafficlight.getRedYellowGreenState(light)[link] in "Gg":
                green[l] = cars_in_lanes_dict[l]
            elif traci.trafficlight.getRedYellowGreenState(light)[link] in "Rr":
                red[l] = cars_in_lanes_dict[l]
    return green, red


def calculate_links():
    to_ret = {}
    for l in traci.trafficlight.getIDList():
        temp_dict = {}
        print("ALL LINKS: ", traci.trafficlight.getControlledLinks(l))
        print("ALL LANES: ", traci.trafficlight.getControlledLanes(l))
        print("-------------------------------------------------------------")
        for index, lane in enumerate(traci.trafficlight.getControlledLanes(l)):
            if lane in temp_dict:
                temp_dict[lane].append(index)
            else:
                temp_dict[lane] = [index]
        if temp_dict:
            to_ret[l] = temp_dict
    return to_ret


def create_subscribers():
    for light in traci.trafficlight.getIDList():
        for lane in traci.trafficlight.getControlledLanes(light):
            traci.lane.subscribe(lane, [traci.constants.LAST_STEP_VEHICLE_NUMBER])


default_max_wait = 30
default_min_wait = 5
default_weight = 10
parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-s", "--sumocfg", help="input the filename of the SUMO config file")
parser.add_argument("--gui", default=False, action="store_true", help="Optional: True by default, use for GUI")
parser.add_argument("--max-wait", type=int, default=default_max_wait, help="Optional: %d by default, maximum time before mandatory phase change" % default_max_wait)
parser.add_argument("--min-wait", type=int, default=default_min_wait, help="Optional: %d by default, minimum time before phase can change" % default_min_wait)
parser.add_argument("--use-lane-max", default=False, action="store_true", help="Optional: False by default. If true, "
                                        "traffic light looks at lane with most cars when determining timings")
parser.add_argument("--no-red-lane-check", default=False, action="store_true", help="Optional: False by default, if true"
                                                       " program does not look at red lanes to determine switch times")
parser.add_argument("-w", "--weight", type=int, default=default_weight, help="Optional: %d by default, each car in  a lane represents "
                                                       "this many seconds to the light." % default_weight)
parser.add_argument("--verbose", action="store_true", default=False, help="Use for more print statements")


args = parser.parse_args()
if args.gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')
sumoCmd = [sumoBinary, "-c", args.sumocfg, "--duration-log.statistics"]

traci.start(sumoCmd)
step = 0

lane_indices = calculate_links()

create_subscribers()

current_wait = {light_id: 0 for light_id in traci.trafficlight.getIDList()}

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    step += 1
    for light_id in traci.trafficlight.getIDList():
        num_vehicles = {}
        for lane_id in traci.trafficlight.getControlledLanes(light_id):
            num_vehicles[lane_id] = traci.lane.getSubscriptionResults(lane_id)[traci.constants.LAST_STEP_VEHICLE_NUMBER]

        cars_in_green, cars_in_red = calc_cars_in_red_green(num_vehicles, light_id)

        current_wait[light_id] += 1
        if current_wait[light_id] > args.min_wait:
            if current_wait[light_id] > args.max_wait and sum(cars_in_red.values()) > 0:
                current_wait[light_id] = 0
                new_duration = 0
                reason = "the max duration of this phase was exceeded"
            elif sum(cars_in_green.values()) < sum(cars_in_red.values()) and not args.no_red_lane_check:
                current_wait[light_id] = 0
                new_duration = 0
                reason = "there are more cars are in red lanes than green"
            else:
                if cars_in_green.values():
                    new_duration = int(args.weight * (max(cars_in_green.values()) if args.use_lane_max else average(cars_in_green.values())))
                    if args.use_lane_max:
                        reason = "there are %d cars in lane %s" % (
                            max(cars_in_green.values()), max(cars_in_green, key=cars_in_green.get))
                    else:
                        reason = "there are an average of %.3f cars in all green lanes" % (
                            average(cars_in_green.values()))
                else:
                    new_duration = 0
                    reason = "No cars in green"

        else:
            new_duration = traci.trafficlight.getPhaseDuration(light_id)
            reason = "the min duration has not been met"
        if args.verbose:
            print("Cars in green: ", cars_in_green)
            print("Cars in red: ", cars_in_red)
            print("New duration set to %d because %s" % (new_duration, reason))
        traci.trafficlight.setPhaseDuration(light_id, new_duration)
    print("-------STEP %d OVER-------" % step)
traci.close()
