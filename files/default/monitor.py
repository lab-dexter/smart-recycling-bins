import RPi.GPIO as GPIO
import cayenne.client
import time
from datetime import datetime
import ConfigParser
import ast
import requests
import os
import json
GPIO.setmode(GPIO.BCM)


class SmartBin():
    def __init__(self, mqtt_username, mqtt_password, mqtt_client_id, trig, echo_pins, sleep_time, api_url, eth_MAC, debug=True):
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.mqtt_client_id = mqtt_client_id
        self.trig = trig
        self.echo_pins = echo_pins
        self.sleep_time = sleep_time
        self.api_url = api_url
        self.eth_MAC = eth_MAC
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
        GPIO.setup(self.trig, GPIO.OUT)
        for i in self.echo_pins:
            GPIO.setup(self.echo_pins[i], GPIO.IN)
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
                    while GPIO.input(self.echo_pins[i]) == 0:
                        pulse_start = time.time()
                        k += 1
                        if k > 200:
                            self.log_msg("Could not get response from sensor %s, continuing with next" % (i))
                            break

                    k = 0
                    while GPIO.input(self.echo_pins[i]) == 1:
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
        url = self.api_url + "/v1/data"
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            data = {"id": sensor_number, "mac": self.eth_MAC, "data": distance, "time": timestamp}
            requests.post(url, data=json.dumps(data))
        except:
            pass

    def run_it(self):
        self.client = cayenne.client.CayenneMQTTClient()
        self.client.on_message = self.on_message
        self.client.begin(self.mqtt_username, self.mqtt_password, self.mqtt_client_id)
        self.monitor()


def get_eth_name():
    # Get name of the Ethernet interface
    try:
        for root, dirs, files in os.walk('/sys/class/net'):
            for dir in dirs:
                if dir[:3] == 'enx' or dir[:3] == 'eth':
                    interface = dir
    except:
        interface = "None"
    return interface


def get_MAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' % interface).read()
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]


if __name__ == '__main__':     # Program start from here
    config = ConfigParser.ConfigParser()
    config.read('/home/pi/smart-recycling-bins-app/smart-recycling-bins/monitor.ini')
    sleep_time = config.getint('default', 'sleep_time')
    MQTT_USERNAME = config.get('default', 'MQTT_USERNAME')
    MQTT_PASSWORD = config.get('default', 'MQTT_PASSWORD')
    MQTT_CLIENT_ID = config.get('default', 'MQTT_CLIENT_ID')
    TRIG = config.getint('default', 'TRIG')
    ECHO_PINS = ast.literal_eval(config.get('default', 'ECHO_PINS'))
    api_url = config.get('default', 'api_url')
#    eth_name = get_eth_name()
#    eth_MAC = get_MAC(eth_name)
    eth_MAC = get_MAC('wlan0')
    smart_bin = SmartBin(mqtt_username=MQTT_USERNAME,
                         mqtt_password=MQTT_PASSWORD,
                         mqtt_client_id=MQTT_CLIENT_ID,
                         trig=TRIG,
                         echo_pins=ECHO_PINS,
                         sleep_time=sleep_time,
                         api_url=api_url,
                         eth_MAC=eth_MAC)
    try:
        smart_bin.run_it()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        smart_bin.destroy()
    except Exception as e:
        smart_bin.log_msg("Something went wrong. Exception: %s" % (str(e)))
