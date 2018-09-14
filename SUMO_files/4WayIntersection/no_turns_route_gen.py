import random
xml_file = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
  <vType id="GenericCar" length="5.0" minGap="2.5" maxSpeed="50.0" accel="3.0" decel="6.0" sigma="0.5" /> 

  <route id="east_west" edges="EW_1 EW_2"/>
  <route id="west_east" edges="WE_1 WE_2"/>
  <route id="north_south" edges="NS_1 NS_2"/>
  <route id="south_north" edges="SN_1 SN_2"/>"""

probabilityWE = 1/10.0
probabilityEW = 1/13.0
probabilityNS = 1/11.0
probabilitySN = 1/17.0
vehNr = 0
for i in range(10000):
	if random.uniform(0,1) < probabilityWE:
		xml_file += '    <vehicle id="we_%i" type="GenericCar" route="west_east" depart="%i" />\n' % (vehNr, i)
		vehNr += 1
	if random.uniform(0,1) < probabilityEW:
		xml_file += '    <vehicle id="ew_%i" type="GenericCar" route="east_west" depart="%i" />\n' % (vehNr, i)
		vehNr += 1
	if random.uniform(0,1) < probabilityNS:
		xml_file += '    <vehicle id="ns_%i" type="GenericCar" route="north_south" depart="%i" />\n' % (vehNr, i)
		vehNr += 1
	if random.uniform(0,1) < probabilitySN:
		xml_file += '    <vehicle id="sn_%i" type="GenericCar" route="south_north" depart="%i" />\n' % (vehNr, i)
		vehNr += 1

xml_file += '</routes>'

with open("no_turns.rou.xml","w") as f:
	f.write(xml_file)