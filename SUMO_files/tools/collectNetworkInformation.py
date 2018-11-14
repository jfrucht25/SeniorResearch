"""
Get information about roads, intersections, what vehicles are on the roads, and avg wait time
"""

import argparse
import xml.etree.cElementTree as eleTree


parser = argparse.ArgumentParser(description="Create traffic light timings")
parser.add_argument("-n", help="input the filename of the network")
parser.add_argument("-t", help="input the filename of the tripinfo file")
#parser.add_argument("-p", help="show pollution info. tripinfo file required")

args = parser.parse_args()

netTree = eleTree.parse(args.n)
netRoot = netTree.getroot()
edge_dict = {}
junction_dict = {}
tl_count = 0
for e in netRoot.iter('edge'):
    if 'function' in e.attrib and e.attrib['function'] == 'internal':
        pass
    else:
        edge_dict[e.attrib['id']] = len(e)

for j in netRoot.iter('junction'):
    if j.attrib['type'] != 'internal':
        junction_dict[j.attrib['id']] = j.attrib['type']

print(edge_dict)
print(junction_dict)
print("There are %d total edges." % len(edge_dict))
for k in edge_dict.keys():
    print("Edge %s has %d lanes" % (k, edge_dict[k]))

for k in junction_dict.keys():
    print("Junction %s is a %s" % (k, junction_dict[k]))

if args.t:
    trip_num = 0
    wait_sum = 0
    wait_max = -1
    vaporized_num = 0
    tripTree = eleTree.parse(args.t)
    tripRoot = tripTree.getroot()
    for t in tripRoot.iter('tripinfo'):
        w = float(t.attrib['waitingTime'])
        wait_sum += w
        trip_num += 1
        wait_max = max(wait_max, w)
        vaporized_num += 1 if t.attrib['vaporized'] else 0


    print("Total number of trips: %d trips" % trip_num)
    if vaporized_num:
        print("CRITICAL PROBLEM: %d cars had to be teleported" % vaporized_num)
    print("Average waiting time: %f seconds" % (wait_sum/trip_num))
    print("Maximum waiting time: %d seconds" % wait_max)

