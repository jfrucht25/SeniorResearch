import argparse
import xml.etree.cElementTree as eleTree

parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-n", "--network", help="input the filename of the network")
parser.add_argument("-a", "--add", help="input the filename of the add file containing the traffic light data")
parser.add_argument("-o", "--output", help="input the name of the output file")
parser.add_argument("-c", "--cycle_length ", help="Optional: desired length of light cycle", default=-1)
# TODO: add optional weight argument that is multiplied with the max time taken

args = parser.parse_args()
netTree = eleTree.parse(args.network)
netRoot = netTree.getroot()
edges = {}  # dictionary of id -> junction info,  lane length, and speed; use network to get
lights = {}  # dictionary of id -> junction and length of states
connections = {} # dictionary of from edge -> to edge, traffic light, link index
for obj in netRoot:
    if obj.tag == "edge" and "function" not in obj.attrib.keys():
        edges[obj.attrib["id"]] = {"from": obj.attrib["from"], "to": obj.attrib["to"], "lights": obj}
    elif obj.tag == "tlLogic":
        lights[obj.attrib["id"]] = [{"duration": a.attrib["duration"], "state": a.attrib["state"]} for a in obj]
    elif obj.tag == "connection":
        connections[obj.attrib["from"]] = {"to": obj.attrib["to"], "tl": obj.attrib["tl"], "linkIndex": obj.attrib["linkIndex"]}

"""
For traffic lights that control a single intersection, the default indices generated generated by NETCONVERT are 
numbered in a clockwise pattern starting with 0 at 12 o'clock with right-turns ordered before straight connections 
and left turns. Pedestrian crossings are always assigned at the very end, also in a clockwise manner.
"""
for l in lights:
    print(l)
    for phase in lights[l]:
        greens = [i for i, v in enumerate(phase["state"]) if v in "Gg"] # indices of green links, use them with connections to determine length of this phase
        green_connects = [i for i in connections if connections[i]["linkIndex"] in greens]
        # look at every green connect from edge, find the length and the speed, and estimate how long it would
        # take a car to travel that length(length/speed). Set duration to max time
        time_taken_greens = [edges[edge]["length"]/edges[edge]["speed"] for edge in green_connects]
        phase["duration"] = max(time_taken_greens)
# TODO: If args.c is not -1, scale duration proportionally

# TODO: handle yellow phases (if yellow set small duration) but take args.c into account
print(edges)
print(lights)

