import RPi.GPIO as GPIO
import time
import cayenne.client
import time
GPIO.setmode(GPIO.BCM)

TRIG = 5
ECHO_PINS = { "1": 19,
              "2": 26,
              "3": 6,
              "4": 13}

# Cayanne creds
MQTT_USERNAME  = "6ebd1c90-d8bf-11e7-ba6c-75d14f3b7ebe"
MQTT_PASSWORD  = "9a7d1fcc88802a51170e151eeb195e035ae9af33"
MQTT_CLIENT_ID = "9577cb70-ddb3-11e7-b67f-67bba9556416"


class SmartBin():
    def __init__(self, mqtt_username, mqtt_password, mqtt_client_id, trig, echo_pins, debug = True):
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.mqtt_client_id = mqtt_client_id
        self.trig = trig
        self.echo_pins = echo_pins
        self.debug = debug
        client = None
        self.setup()

    # The callback for when a message is received from Cayenne.
    def on_message(self, message):
        self.log_msg("message received: " + str(message))
        # If there is an error processing the message return an error string, otherwise return nothing.

    def log_msg(self, message):
        """If debug, prints text on screen. Logs message to file."""
        if self.debug:
            print message

    def setup(self):
        """Set up pins for sensor."""
        # GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

        self.log_msg("Distance measurement in progress")
        GPIO.setup(self.trig,GPIO.OUT)
        for i in self.echo_pins:
            GPIO.setup(self.echo_pins[i],GPIO.IN)
        self.res()

    def res(self):
        """Resets sensor."""
        GPIO.output(self.trig, False)
        self.log_msg("Waiting for sensor to settle")

        time.sleep(1)

        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

    def monitor(self):
        """Gets sensor values, calcuclates and saves distance."""
        while True:
            self.client.loop()
            for i in self.echo_pins:
                data_list = []
                for j in xrange(5):
                    self.res()
                    k = 0
                    while GPIO.input(self.echo_pins[i])==0:
                        pulse_start = time.time()
                        k += 1
                        if k > 200:
                            self.log_msg("Could not get response from sensor %s, continuing with next" % (i))
                            break

                    while GPIO.input(self.echo_pins[i])==1:
                        pulse_end = time.time()

                    pulse_duration = pulse_end - pulse_start
                    distance = pulse_duration * 17150
                    distance = round(distance, 2)

                    if distance < 200:
                        if distance < 10:
                            self.log_msg("Recycle bin %s is full! Sending notification" % (i))
                        data_list.append(distance)
                    else:
                        self.log_msg("Skipping sensor %s results. %s is too big." % (i, distance))
                if len(data_list) > 0:
                    average_distance = round(sum(data_list) / len(data_list), 2)
                    self.save_data(i, average_distance)
                else:
                    self.log_msg("Sensor %s returned corrupt data, skipping data upload" % (i))

    def destroy(self):
        """Clean up."""
        GPIO.cleanup()                  # Release resource

    def save_data(self, sensor_number, distance):
        """Saves provided data to database"""
        self.log_msg("Sensor %s shows distance: %s cm" % (sensor_number, distance))
        self.client.virtualWrite(int(sensor_number), distance)

    def run_it(self):
        self.client = cayenne.client.CayenneMQTTClient()
        self.client.on_message = self.on_message
        self.client.begin(self.mqtt_username, self.mqtt_password, self.mqtt_client_id)
        i=0
        timestamp = 0
        self.monitor()

if __name__ == '__main__':     # Program start from here
    smart_bin = SmartBin(mqtt_username = MQTT_USERNAME,
                         mqtt_password = MQTT_PASSWORD,
                         mqtt_client_id = MQTT_CLIENT_ID,
                         trig = TRIG,
                         echo_pins = ECHO_PINS)
    try:
        smart_bin.run_it()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        smart_bin.destroy()
    except Exception as e:
        logIt("Something went wrong. Exception: %s" % (str(e)))
