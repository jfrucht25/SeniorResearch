import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/usr/bin/sumo"

import traci

def main():
    sumoFile = sys.argv[1]
    sumoCmd = [sumoBinary, '-c', sumoFile]
    traci.start(sumoCmd)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    
    traci.close()

if __name__ == "__main__":
    main()
