"""
Set traffic light timings by reading in user input. Take in network file and options
"""

import argparse 
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
        print("Phase is ", phase.attrib)
#TODO: set phase duration through command line (show each one and let user modify)
print(args.n)