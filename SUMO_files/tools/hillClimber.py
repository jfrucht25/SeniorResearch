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


def isValid(dict):
    if dict["min_wait"] > dict["max_wait"]:
        return False
    if dict["min_wait"] < 0:
        return False
    if dict["max_wait"] < 0:
        return False
    return True


class TrafficController:
    def __init__(self, args):
        self.arguments = args

        self.lane_indices = self.calculate_links()
        self.create_subscribers()

        self.current_wait = {light_id: 0 for light_id in traci.trafficlight.getIDList()}
        self.all_controlled_lanes = [lane_id for light_id in traci.trafficlight.getIDList()
                                for lane_id in traci.trafficlight.getControlledLanes(light_id)]
        self.lane_connections = {}
        self.junction_connections = {lane_id: self.get_link_to_junction(lane_id) for lane_id in self.all_controlled_lanes}
        for lane in traci.lane.getIDList():
            links = traci.lane.getLinks(lane)
            if links:
                self.lane_connections[lane] = [i[0] for i in links]

    def calc_cars_in_red_green(self, cars_in_lanes_dict, light):
        green = {}
        red = {}
        for l in cars_in_lanes_dict.keys():
            for link in self.lane_indices[light][l]:
                if traci.trafficlight.getRedYellowGreenState(light)[link] in "Gg":
                    green[l] = cars_in_lanes_dict[l]
                elif traci.trafficlight.getRedYellowGreenState(light)[link] in "Rr":
                    red[l] = cars_in_lanes_dict[l]
        return green, red

    def calculate_links(self):
        to_ret = {}
        for l in traci.trafficlight.getIDList():
            temp_dict = {}
            if self.arguments["verbose"]:
                print("FOR LANE %s" % l)
                print("ALL LINKS: ", traci.trafficlight.getControlledLinks(l))
                print("ALL LANES: ", traci.trafficlight.getControlledLanes(l))
                print("-------------------------------------------------------------")
            for index, controlled_lane in enumerate(traci.trafficlight.getControlledLanes(l)):
                if controlled_lane in temp_dict:
                    temp_dict[controlled_lane].append(index)
                else:
                    temp_dict[controlled_lane] = [index]
            if temp_dict:
                to_ret[l] = temp_dict
        return to_ret

    @staticmethod
    def create_subscribers():
        for light in traci.trafficlight.getIDList():
            for controlled_lane in traci.trafficlight.getControlledLanes(light):
                traci.lane.subscribe(controlled_lane, [traci.constants.LAST_STEP_VEHICLE_NUMBER])

    def get_link_to_junction(self, lane_id):
        to_add = []
        if lane_id in self.lane_connections:
            connections = self.lane_connections[lane_id]
            for c in connections:
                if c in self.all_controlled_lanes:
                    to_add.append(c)
                else:
                    to_add.extend(self.get_link_to_junction(c))
        return to_add

    def simulate(self):
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step += 1
            incoming_cars = {lane_id: 0 for lane_id in traci.lane.getIDList()}
            for light_id in traci.trafficlight.getIDList():
                num_vehicles = {}
                for lane_id in traci.trafficlight.getControlledLanes(light_id):
                    num_vehicles[lane_id] = traci.lane.getSubscriptionResults(lane_id)[
                        traci.constants.LAST_STEP_VEHICLE_NUMBER]

                cars_in_green, cars_in_red = self.calc_cars_in_red_green(num_vehicles, light_id)
                if self.arguments["verbose"]:
                    print("\n")
                    print("FOR LIGHT %s: " % light_id)
                    print("    Cars in green: ", cars_in_green)
                    print("    Cars in red: ", cars_in_red)
                for lane_id in cars_in_green:
                    cars_in_green[lane_id] += args.incoming_weight * incoming_cars[lane_id]
                for lane_id in cars_in_red:
                    cars_in_red[lane_id] += self.arguments["incoming_weight"]* incoming_cars[lane_id]

                self.current_wait[light_id] += 1
                if self.current_wait[light_id] > self.arguments["min_wait"]:
                    if self.current_wait[light_id] > self.arguments["max_wait"] and sum(cars_in_red.values()) > 0:
                        self.current_wait[light_id] = 0
                        new_duration = 0
                        reason = "the max duration of this phase was exceeded"
                    elif sum(cars_in_green.values()) < sum(cars_in_red.values()) and not self.arguments["no_red_lane_check"]:
                        self.current_wait[light_id] = 0
                        new_duration = 0
                        reason = "there are more cars are in red lanes than green"
                    else:
                        if cars_in_green.values():
                            new_duration = int(self.arguments["weight"] * (max(cars_in_green.values()) if args.use_lane_max
                                                              else average(cars_in_green.values())))
                            if self.arguments["use_lane_max"]:
                                max_lane = max(cars_in_green, key=cars_in_green.get)
                                reason = "there are %d cars in lane %s and %d incoming cars" % (
                                    max(cars_in_green.values()), max_lane, incoming_cars[max_lane])
                            else:
                                reason = "there are an average of %.3f cars across all green lanes, including incoming cars" % (
                                    average(cars_in_green.values()))
                        else:
                            new_duration = 0
                            reason = "No cars in green"

                else:
                    new_duration = traci.trafficlight.getPhaseDuration(light_id)
                    reason = "the min duration has not been met"
                if self.arguments["verbose"]:
                    to_print = {i: incoming_cars[i] for i in incoming_cars if incoming_cars[i]}
                    print("    Incoming cars (only non-zero shown): ", to_print)
                    print("    New duration set to %d because %s." % (new_duration, reason))

                traci.trafficlight.setPhaseDuration(light_id, new_duration)

                '''
                New stuff. Check the links from the cars in green lanes and send them through the next lanes.
                Possible improvement: keep going down connections until at one controlled by a traffic light
                '''
                new_cars_in_green, new_cars_in_red = self.calc_cars_in_red_green(num_vehicles, light_id)
                for lane_id in new_cars_in_green:  # get each green lane
                    for connection in self.lane_connections[lane_id]:  # get each lane it is connected to
                        # print(connection in all_controlled_lanes)
                        incoming_cars[connection] += new_cars_in_green[lane_id] / len(self.lane_connections[lane_id])
                        # for each lane, add number of cars in that lane over total links out from that lane
                        # assumes that cars in a lane equally split between possible lane destinations
            # print("-------STEP %d OVER-------" % step)
        return step


default_max_wait = 30
default_min_wait = 5
default_weight = 10.0
default_incoming_weight = 1.0
parser = argparse.ArgumentParser(description="Create traffic light timings based on cars in the lanes")
parser.add_argument("-s", "--sumocfg", help="input the filename of the SUMO config file")
parser.add_argument("--gui", default=False, action="store_true", help="Optional: False by default, use for GUI")
parser.add_argument("--max-wait", type=int, default=default_max_wait,
                    help="Optional: %d by default, initial maximum time before mandatory phase change." % default_max_wait)
parser.add_argument("--min-wait", type=int, default=default_min_wait,
                    help="Optional: %d by default, initial minimum time before phase can change. "
                         % default_min_wait)
parser.add_argument("--use-lane-max", default=False, action="store_true", help="Optional: False by default. If true, "
                                                                               "traffic light looks at lane with most "
                                                                               "cars when determining timings")
parser.add_argument("--no-red-lane-check", default=False, action="store_true",
                    help="Optional: False by default, if true"
                         " program does not look at red lanes to determine switch times")
parser.add_argument("-w", "--weight", type=float, default=default_weight,
                    help="Optional: %f by default, each car in  a lane represents "
                         "this many seconds to the light." % default_weight)
parser.add_argument("--incoming-weight", type=float, default=default_incoming_weight, help="Optional: %f by default, "
                                                                                         "each car coming from another "
                                                                                         "light represents this many "
                                                                                         "seconds." %
                                                                                         default_incoming_weight)
parser.add_argument("--verbose", action="store_true", default=False, help="Use for more print statements")

args = parser.parse_args()
print(vars(args))

if args.gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')
new_args = vars(args).copy()
if not args.sumocfg or ".sumocfg" not in args.sumocfg:
    parser.error("You must provide a .sumocfg file")
if args.min_wait > args.max_wait:
    parser.error("min_wait cannot be greater than max_wait")
if args.min_wait < 0:
    parser.error("min_wait cannot be below 0")
if args.max_wait < 0:
    parser.error("max_wait cannot be below 0")
if args.weight < 0:
    parser.error("weight cannot be below 0")
if args.incoming_weight < 0:
    parser.error("incoming_weight cannot be below 0")

summary = []
sumoCmd = [sumoBinary, "-c", args.sumocfg, "--duration-log.statistics"]

current_min_wait = args.min_wait
current_max_wait = args.max_wait
current_args = vars(args)
current_args["max_wait"] = current_max_wait
current_args["min_wait"] = current_min_wait
traci.start(sumoCmd)
controller = TrafficController(current_args)
current_steps = controller.simulate()
traci.close()
print("Minimum waiting time: %d" % current_args["min_wait"])
print("Maximum waiting time: %d" % current_args["max_wait"])
print("Steps required to complete: %d" % current_steps)


past_runs = {(current_min_wait, current_max_wait): current_steps}
while True:
    improved = False
    neighbors = []
    for key in ["max_wait", "min_wait"]:
        for adder in [-1, 1]:
            temp = current_args.copy()
            temp[key] += adder
            if isValid(temp):
                neighbors.append(temp)
    for n in neighbors:
        min_wait = n["min_wait"]
        max_wait = n["max_wait"]
        if (min_wait, max_wait) in past_runs:
            steps_taken = past_runs[(min_wait, max_wait)]
        else:
            traci.start(sumoCmd)
            controller = TrafficController(n)
            steps_taken = controller.simulate()
            traci.close()
            past_runs[(min_wait, max_wait)] = steps_taken
        summary.append((min_wait, max_wait, steps_taken))
        if steps_taken < current_steps:
            current_args = n.copy()
            current_steps = steps_taken
            print("This neighbor is better; using as current")
            improved = True
            break
        print("Minimum waiting time: %d" % min_wait)
        print("Maximum waiting time: %d" % max_wait)
        print("Steps required to complete: %d" % steps_taken)
        print("-------------------")
    if not improved:
        break
for tup in summary:
    print("Minimum waiting time: %d" % tup[0])
    print("Maximum waiting time: %d" % tup[1])
    print("Steps required to complete: %d" % tup[2])
traci.close()
