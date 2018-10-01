"""
Set traffic light timings by reading in user input. Take in network file and options
"""

import argparse
import msvcrt
import xml.etree.cElementTree as ET


parser = argparse.ArgumentParser(description="Create traffic light timings")
parser.add_argument("-n",help="input the filename of the network or add file with traffic")
args = parser.parse_args()

tree = ET.parse(args.n)
root = tree.getroot()
print(root)
print(root[0])
print(root[0][0])
for light in root:
    for phase in light:
        print(phase.attrib['duration'])
        print("Phase is ", phase.attrib)
        print("Change timings to:", end="",flush=True)
        new_timing = input("")
        phase.attrib['duration'] = new_timing
tree.write(args.n)
#TODO: set phase duration through command line (show each one and let user modify)