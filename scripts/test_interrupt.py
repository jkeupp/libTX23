import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
import numpy
sleep_init = 500
 #ms

def time2():
    return time.time_ns()
GPIO.setmode(GPIO.BCM)

dPIN =  22 # hardware pin number 15, but we're using 
# a single cycle

#1 pull pin for some time
GPIO.setup(dPIN, GPIO.OUT)
GPIO.output(dPIN,GPIO.LOW)

t0 = time.time()
time.sleep(sleep_init*0.001)
#t0 = time.perf_counter()
def callback(xxx):
    ups.append(time.time()-t0)


GPIO.setup(dPIN, GPIO.IN,pull_up_down=GPIO.PUD_OFF)

GPIO.add_event_detect(dPIN,GPIO.BOTH,callback=callback)

#GPIO.add_event_detect(dPIN,GPIO.UP,callback=callback_up)
#GPIO.add_event_detect(dPIN,GPIO.DOWN,callback=callback_down)
ups = []

time.sleep(0.5)


ups = numpy.array(ups)
d = numpy.diff(ups)



## stuff from c
#define TX23_DATA_SET_OUTPUT_LOW
#	bcm2835_gpio_write(RPI_GPIO_TX23_DATA, LOW);\
#   bcm2835_gpio_fsel(RPI_GPIO_TX23_DATA, BCM2835_GPIO_FSEL_OUTP)

#define	TX23_DATA_SET_INPUT 		
#   bcm2835_gpio_fsel(RPI_GPIO_TX23_DATA, BCM2835_GPIO_FSEL_INPT);\
#	bcm2835_gpio_set_pud(RPI_GPIO_TX23_DATA, BCM2835_GPIO_PUD_OFF)

#define TX23_DATA_GET_BIT		
#   bcm2835_gpio_lev(RPI_GPIO_TX23_DATA)