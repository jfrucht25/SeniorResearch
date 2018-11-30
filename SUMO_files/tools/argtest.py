import os
import sys
import argparse


parser = argparse.ArgumentParser(description="Create traffic light timings based on road lengths")
parser.add_argument("-a", type=int, default=30)
parser.add_argument("--max-wait", type=int, default=30, nargs='*',
                    help="Optional: 30 by default, maximum time before mandatory phase change")
args = parser.parse_args()
print(args.max_wait)