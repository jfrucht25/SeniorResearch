"""
Set traffic light timings by reading in user input. Take in network file and options
"""

import argparse

parser = argparse.ArgumentParser(description="Create traffic light timings")
parser.add_argument("-n",help="input the filename of the network")
args = parser.parse_args()
print(args)