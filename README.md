# SeniorResearch

Basics
-
Model four-way and three-way intersections with traffic lights made using SUMO. Run the .config file to view the simulation. Open the .net.xml file in NETEDIT to change the road network. Remember to generate new routes after changing the network. Real world intersections came directly from data in osmWebWizard, and can be run in the same way as the model intersections. Traffic light timings are stored in the NETNAME_tl.add.xml file.

Note: work on BDQ is here: https://github.com/jfrucht25/BDQ

Commands 
-------------------
- Run SUMO with more information
	sumo -c SUMOCFG.sumocfg --tripinfo-output FILE.tripinfo.xml
	--tripinfo provides info about vehicle departure and arrival
- Generate random paths 

	python randomTrips.py -n NETNAME.rou.xml -r ROUTENAME.rou.xml
	
- Alter duration and (optionally) phase of given traffic light file
	
	python setTrafficTimings -n NETNAME.add.xml
	
	python setTrafficTimings --help 
-Visualization
	python plot_net_dump -n NETNAME.net.xml -i NETNAME.dump.xml,NETNAME.dump.xml  -m MEASURE1, MEASURE2 -o PICNAME.png
	measures should be in the dump file, they are displayed in the figure
	
