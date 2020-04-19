#!/usr/bin/python3 -i

import libTX23
import matplotlib.pyplot as plt
import numpy
from pprint import pprint as pp
import time

TX23 = libTX23.TX23()

#print('##### Bruteforce Measurement #####')
#TX23._init_measurement()
#m = TX23._measure_bruteforce()
#test,data = TX23.parse_bruteforce_measurement(m)
#pp(data)
TX23._init_measurement()
time.sleep(1)

print('##### Interrupt Measurement #####')
interrupt_measurement = TX23._measure_interrupt()
data_interrupt,data_interrupt_formatted = TX23.parse_interrupt_measurement(interrupt_measurement,plot=True)
pp(data_interrupt_formatted)
print(TX23.parse_windspeed(data_interrupt_formatted['speed']))
print(TX23.parse_direction(data_interrupt_formatted['direction']))
#plt.plot(m[:,0],m[:,1])
#plt.scatter(data2[:,0],data2[:,1])
#plt.show()


