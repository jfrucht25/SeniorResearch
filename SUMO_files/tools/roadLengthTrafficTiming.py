import argparse
import xml.etree.cElementTree as eleTree

parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-n", help="input the filename of the network")
parser.add_argument("-a", help="input the filename of the add file containing the traffic light data")

parser.add_argument("-o", help="input the name of the output file")

args = parser.parse_args()
netTree = eleTree.parse(args.n)
netRoot = netTree.getroot()
edges = {}  # dictionary of id -> junction info,  lane length, and speed
lights = {}  # dictionary of id -> junction and length of states
 
