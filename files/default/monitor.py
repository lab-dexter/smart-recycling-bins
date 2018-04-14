import RPi.GPIO as GPIO
import cayenne.client
import time
import ConfigParser
GPIO.setmode(GPIO.BCM)


class SmartBin():
    def __init__(self, mqtt_username, mqtt_password, mqtt_client_id, trig, echo_pins, sleep_time, debug = True):
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.mqtt_client_id = mqtt_client_id
        self.trig = trig
        self.echo_pins = echo_pins
        self.sleep_time = sleep_time
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
        """Gets sensor values, calculates and saves distance."""
        while True:
            try:
                self.client.loop()
            except:
                self.log_msg("Got exception while connecting to cayanne. Continuing")
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

                    k = 0
                    while GPIO.input(self.echo_pins[i])==1:
                        pulse_end = time.time()
                        k += 1
                        if k > 200:
                            self.log_msg("Could not get response from sensor %s, continuing with next" % (i))
                            break

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
                time.sleep(sleep_time)

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
    config = ConfigParser.ConfigParser()
    config.read('/home/pi/smart-recycling-bins-app/smart-recycling-bins/monitor.ini')
    sleep_time = config.get('default', 'sleep_time')
    MQTT_USERNAME = config.get('default', 'MQTT_USERNAME')
    MQTT_PASSWORD = config.get('default', 'MQTT_PASSWORD')
    MQTT_CLIENT_ID = config.get('default', 'MQTT_CLIENT_ID')
    TRIG = config.getint('default', 'TRIG')
    ECHO_PINS = config.get('default', 'ECHO_PINS')
    smart_bin = SmartBin(mqtt_username = MQTT_USERNAME,
                         mqtt_password = MQTT_PASSWORD,
                         mqtt_client_id = MQTT_CLIENT_ID,
                         trig = TRIG,
                         echo_pins = ECHO_PINS,
                         sleep_time = sleep_time)
    try:
        smart_bin.run_it()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        smart_bin.destroy()
    except Exception as e:
        smart_bin.log_msg("Something went wrong. Exception: %s" % (str(e)))
