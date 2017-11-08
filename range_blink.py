import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG = 23 
ECHO = 24


def setup():
    # GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

    logIt("Distance Measurement In Progress")
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    res()
 
def res():
    """resets sensor."""
    GPIO.output(TRIG, False)
    logIt("Waiting For Sensor To Settle")

    time.sleep(5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
  
def blink():
    while True:
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        saveData(distance)
        res()

def destroy():
    GPIO.cleanup()                  # Release resource

def saveData(distance):
    """Saves provided data to database"""
    logIt('Distance: %s cm' % (distance))

def logIt(text):
    """Logs provided text to log file."""
    print text

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        blink()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
    except Exception as e:
        logIt("Something went wrong. Exception: %s" % (str(e)))
