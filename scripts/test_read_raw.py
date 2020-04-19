import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
import numpy
sleep_init = 500 #ms

GPIO.setmode(GPIO.BCM)

dPIN =  22 # hardware pin number 15, but we're using BCM! 
# a single cycle

#1 pull pin for some time
GPIO.setup(dPIN, GPIO.OUT)
GPIO.output(dPIN,GPIO.LOW)

time.sleep(sleep_init*0.001)


GPIO.setup(dPIN, GPIO.IN,pull_up_down=GPIO.PUD_OFF)

i=0
data = []
t0 = time.perf_counter()
while i < 2e5:
    inp =  GPIO.input(dPIN)
    data.append([time.perf_counter()-t0,inp])
    if i % 1000 == 0: 
        print(i,inp)
    i += 1
GPIO.cleanup()
data = numpy.array(data)
t = data [:,0]
d = data[:,1]
dd = numpy.abs(numpy.gradient(d))*2
ddd = numpy.where(dd > 0.5)
dts = t[ddd[0]][2:]

plt.plot(data[:,0],data[:,1])
plt.xlabel('t  [s]')
plt.ylabel('signal')
plt.show()

## stuff from c
#define TX23_DATA_SET_OUTPUT_LOW
#	bcm2835_gpio_write(RPI_GPIO_TX23_DATA, LOW);\
#   bcm2835_gpio_fsel(RPI_GPIO_TX23_DATA, BCM2835_GPIO_FSEL_OUTP)

#define	TX23_DATA_SET_INPUT 		
#   bcm2835_gpio_fsel(RPI_GPIO_TX23_DATA, BCM2835_GPIO_FSEL_INPT);\
#	bcm2835_gpio_set_pud(RPI_GPIO_TX23_DATA, BCM2835_GPIO_PUD_OFF)

#define TX23_DATA_GET_BIT		
#   bcm2835_gpio_lev(RPI_GPIO_TX23_DATA)
