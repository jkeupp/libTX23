#!/usr/bin/python3
# runs the measurement and writes the result 

import libTX23
import matplotlib.pyplot as plt
import numpy
from pprint import pprint as pp
import time
import datetime
import os
import pickle
import time
TX23 = libTX23.TX23()
now = datetime.datetime.now()
raw_data_file = now.strftime('%m_%d_%Y_%H_%M') + '.dat'
f = open(raw_data_file,'w')

TX23._init_measurement()
time.sleep(1)

done=False
os.system('mkdir pickled_data')

while not done:
    try:
        #TX23._init_measurement()
        #time.sleep(1)
        interrupt_measurement = TX23._measure_interrupt()
        data_raw, data = TX23.parse_interrupt_measurement(interrupt_measurement,plot=False)
        intdirection,direction = TX23.parse_direction(data['direction'])
        now = datetime.datetime.now()
        nows = now.strftime('%m_%d_%Y_%H_%M_%S_%f')
        print(data['speed'],data['direction'])
        print(data_raw)
        intspeed,speed = TX23.parse_windspeed(data['speed'])
        f.write('%s %d %d %10.6f\n' % (nows,intdirection,intspeed,speed))
        pickle.dump({'measurement':interrupt_measurement,'raw_data':data_raw,'data':'data'},
                    open('pickled_data/'+nows+'.pickle','wb'))
        time.sleep(1)
        f.flush()
    except:
        print('ERROR')
        time.sleep(2)
f.close()





#        formatted_data = {'startup_sequqence':data[0:5],
#                          'direction':data[5:9],
#                          'speed':data[10:23],
#                          'checksum':data[23:27],
#                          'direction_inv':data[27:31],
#                          'speed_inv':data[32:45]}