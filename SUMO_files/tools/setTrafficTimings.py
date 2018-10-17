"""
Set traffic light timings by reading in user input. Take in network file and options
"""

import argparse
import xml.etree.cElementTree as eleTree


parser = argparse.ArgumentParser(description="Create traffic light timings")
parser.add_argument("-n", help="input the filename of add file with traffic lights")
parser.add_argument("-s", help="change state as well as duration by setting flag to a true value")
args = parser.parse_args()

tree = eleTree.parse(args.n)
root = tree.getroot()
for light in root:
    for phase in light:
        print("Phase is ", phase.attrib)
        if args.s:
            #possible states are rygGsuoO
            new_state = input("Change state to: ")
            while not all(i in "rygGsuoO" for i in new_state) or len(new_state) != len(phase.attrib['state']):
                new_state = input("Change state to (only use r, y, g, G, s, u, o, or O; must be length %d): "% len(phase.attrib['state']))
            phase.attrib['state'] = new_state
        new_timing = input("Change duration to: ")
        while not new_timing.isdigit():
            new_timing = input("Change duration to (enter an integer): ")
        phase.attrib['duration'] = new_timing
tree.write(args.n)