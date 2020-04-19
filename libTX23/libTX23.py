import time
import os
import numpy
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import datetime
import scipy.signal
import pathlib

GPIO.setmode(GPIO.BCM)

class TX23(object):
    def __init__(self,pulltime=500,datapin=22):     
        self.pulltime = pulltime # in milliseconds
        self.datapin = datapin     
        self.measurements = []
        self.bitwidth = 1.200 # ms
        return

    def _init_measurement(self,):
        #1 pull pin for some time
        #GPIO.cleanup()
        GPIO.setup(self.datapin, GPIO.OUT)
        GPIO.output(self.datapin,GPIO.LOW)
        time.sleep(self.pulltime*0.001)
        GPIO.setup(self.datapin, GPIO.IN,pull_up_down=GPIO.PUD_OFF)
        return

    def _measure_bruteforce(self):
        t0 = time.perf_counter() # i was told this is more precise than time.time()
        self.latest_measurement = []
        dt = 0.01
        while dt < 0.2: # after 200ms all is done!
            inp =  GPIO.input(self.datapin)
            dt = time.perf_counter() - t0
            self.latest_measurement.append([dt,inp])
        self.latest_measurement = numpy.array(self.latest_measurement)
        self.measurements.append([datetime.datetime.now(),self.latest_measurement])
        return self.latest_measurement

    def _measure_interrupt(self):
        self.t0 = time.perf_counter() # i was told this is more precise than time.time()
        ups = []
        downs = []
        self.data = []
        GPIO.add_event_detect(self.datapin,GPIO.BOTH,callback=self._callback)
        # the init measurement has to be done here, since calling it prior to add_event_detect
        # results in missing data points at the very beginning of the timeseries
        # this is probably because the add_event_detect function takes too long
        self._init_measurement()
        self.data = []
        self.t0 = time.perf_counter() # i was told this is more precise than time.time()
        time.sleep(2) #gather data
        GPIO.remove_event_detect(self.datapin)
        return numpy.array(self.data)
    
    def _callback(self,xxx):
        dt = time.perf_counter() - self.t0
        inp = GPIO.input(self.datapin)
        self.data.append([dt,inp])
        return

    def measure(self):
        self._init_measurement()
        self._measure_bruteforce()
        return self.latest_measurement

    def parse_interrupt_measurement(self,measurement,plot=False):
        """ parses the t vs signal output of an interrupt based measurement
        
        Args:
            measurement (numpy.ndarray n x 2): the measurement data as numpy array
        """              
        def s(t):
            # returns the value in between data points by 
            tidx = numpy.where(measurement[:,0] <= t)[0]
            if len(tidx) == 0:
                print('warning, no data point found')
                return -1
            tidx = tidx[-1] # 
            return  measurement[tidx,1]
        t = measurement[:,0]
        # analyze length of initial 11011 sequence; ignore first two signals!
        len1 = t[3] - t[2] # 11
        len2 = t[4] - t[3] # 0
        dt  = (len1/2 + len2) / 2.0
        # many times we get 1.220 ms
        print('measured dt = %6.3f ms' % (dt*1000,))
        dt = 1.220 / 1000.0
        tstart  = t[2] # this is where the sequence starts
        t_centers = numpy.array([tstart + dt/2 + dt*i for i in range(5+4+12+4+4+12)]) 
        data = []
        idxs = []
        for i,tc in enumerate(t_centers):
            datai = int(numpy.round(s(tc)))
            data.append(datai)
        #import pdb; pdb.set_trace()
        formatted_data = {'startup_sequqence':data[0:5],
                          'direction':data[5:9],
                          'speed':data[9:21][::-1],
                          'checksum':data[23:27],
                          'direction_inv':data[27:31],
                          'speed_inv':data[32:45]}
        if plot is True:
            tgen = numpy.linspace(0.0,0.2,1000)
            sgen = [s(x) for x in tgen]
            plt.plot(tgen,sgen)
            plt.scatter(t,measurement[:,1])
            plt.scatter(t_centers,[0]*len(t_centers))
            plt.show()
        return data,formatted_data
    
    def parse_direction(self,direction):
        intdir = self.listofbytes_to_int(direction)
        #tbi - translate integer wind direction to some string
        winddirection = 'na'
        return intdir, winddirection

    def parse_windspeed(self,windspeed_bytes):
        intspeed = self.listofbytes_to_int(windspeed_bytes)
        windspeed = 0.1 * intspeed
        return intspeed, windspeed

    def listofbytes_to_int(self,listofbytes):
        return int(numpy.sum([x*(2**i) for i,x in enumerate(listofbytes[::-1])]))
    
    def parse_bruteforce_measurement(self,measurement,plot=False):
        """ parses the t vs signal output of a bruteforce measurement
        
        Args:
            measurement (numpy.ndarray n x 2): the measurement data as numpy array
        """                
        t = measurement[:,0]
        s = measurement[:,1]
        g = numpy.gradient(s)
        gpeaks = scipy.signal.find_peaks(abs(g))[0][1:] 
        # analyze length of initial 11011 sequence
        len1 = t[gpeaks[1]] - t[gpeaks[0]] # 11
        len2 = t[gpeaks[2]] - t[gpeaks[1]] # 0
        dt  = (len1/2 + len2) / 2.0
        # many times we get 1.220 ms
        print('measured dt = %6.3f ms' % (dt*1000,))
        dt = 1.220 / 1000.0
        tstart  = t[gpeaks[0]] # this is where the sequence starts
        t_centers = numpy.array([tstart + dt/2 + dt*i for i in range(5+4+12+4+4+12)]) 
        data = []
        idxs = []
        for i,tc in enumerate(t_centers):
            idx = numpy.argmin((t-tc)**2)
            if abs(t[idx]-tc)*1000 > dt/2.0*1000.0 :
                print('warning, could not find a proper data point for %d, diff= %6.3f' % (i,(t[idx]-tc)*1000))# ms
            idxs.append(idx)
            datai = 1 if s[idx]> 0.5 else 0
            data.append(datai)
        #import pdb; pdb.set_trace()
        formatted_data = {'startup_sequqence':data[0:5],
                          'direction':data[5:9],
                          'speed':data[10:23],
                          'checksum':data[23:27],
                          'direction_inv':data[27:31],
                          'speed_inv':data[32:45]}
        if plot is True:
            plt.plot(t,s)
            plt.plot(t,g)
            plt.scatter(t_centers,[0]*len(t_centers))
            plt.scatter(t[idxs],[0.1]*len(idxs))
            plt.show()
        return data,formatted_data

    def plot_bruteforce_measurement(self,measurement,parse=False):
        fig = plt.figure(figsize=[10,6])
        ax = fig.add_subplot(111)
        ax.plot(measurement[:,0]*1000,measurement[:,1])
        ax.set_xlabel('t [ms]')
        ax.set_ylabel('signal')
        plt.show()
        return


###### Database backend ################

    def init_database(self,db_fname='measurements.sqlite',raw_data_path = None, data_path = None):
        if raw_data_path is None:
            raw_data_path = os.environ['MEASUREMENT_RAW_DATA_PATH']
        if data_path is None:
            data_path = os.environ['MEASUREMENT_DATA_PATH']
        self.data_path = data_path
        self.raw_data_path = raw_data_path
        self.dbpath = data_path+ '/' + db_fname
        self.db = DAL(('sqlite://%s' % (self.dbpath,)),migrate=False,fake_migrate=False)
        db = self.db
        db.define_table('measurement',
            Field('datetime','datetime'),
            Field('wind_speed','float'),
            Field('wind_direction','float'),
            Field('measurement_type','string',
            Field('raw_data_file','string'))
            )

            
    def add_measurement(self,measurement,raw_measurement=None):
        db = self.db
        if raw_measurement is not None:
            now  = datetime.datetime.now()
            raw_data_file = now.strftime('%m_%d_%Y_%H_%M_%S_%f') + '.dat'
        db.measurement.insert(datetime=datetime.datetime.now(),
                                wind_speed = measurement['wind_speed'],
                                wind_direction = measurement['wind_direction'],
                                measurement_type = measurement['measurement_type'],
                                raw_data_file = raw_data_file
                                )
        db.commit()

    def write_measurement_ascii(self,measurement,fhandle):

        return

    def write_raw_data_file(self):

        return


