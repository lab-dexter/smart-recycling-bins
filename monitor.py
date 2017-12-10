import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

TRIG = 5
echo_pins = { "pirmas": 19,
              "antras": 26, 
              "trecias": 6,
              "ketvirtas": 13}
#ECHO = 19
#ECHO2 = 26

def setup():
    """Set up pins for sensor."""
    # GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

    logIt("Distance Measurement In Progress")
    GPIO.setup(TRIG,GPIO.OUT)
    for i in echo_pins:
        GPIO.setup(echo_pins[i],GPIO.IN)
    res()
 
def res():
    """Resets sensor."""
    GPIO.output(TRIG, False)
    logIt("Waiting For Sensor To Settle")

    time.sleep(1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
  
def blink():
    """Gets sensor values, calcuclates and saves distance."""
    while True:
        for i in echo_pins:
            while GPIO.input(echo_pins[i])==0:
                pulse_start = time.time()

            while GPIO.input(echo_pins[i])==1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)

            if distance < 200:
                if distance < 10:
                    logIt("%s recycle bin is full! Sending notification" % (i))
                saveData(i, distance)
            else:
                logIt("skipping %s sensor results. %s is too big." % (i, distance))
            res()

def destroy():
    """Clean up."""
    GPIO.cleanup()                  # Release resource

def saveData(sensor_name, distance):
    """Saves provided data to database"""
    logIt("Sensor %s shows distance: %s cm" % (sensor_name, distance))

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
