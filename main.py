#!/usr/bin/env python
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

""" Example for using the SGP30 with CircuitPython and the Adafruit library"""

import datetime
import time
import board
import busio
import adafruit_sgp30
from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "grafana"
ifpass = "EtelC0m56"
ifdb = "home"
ifhost = "127.0.0.1"
ifport = 8086
measurement_name = "Taux"

# connect to influx
ifclient = InfluxDBClient(ifhost,  ifport, ifuser, ifpass, ifdb)

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)
sgp30.set_iaq_relative_humidity(celcius=22.1, relative_humidity=44)

elapsed_sec = 0

while True:
    print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    time.sleep(0.1)
    elapsed_sec += 1
    if elapsed_sec > 10:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC))
    # format the data as a single measurement for influx
    timee = datetime.datetime.utcnow()
    body = [
        {
            "measurement": measurement_name,
            "time": timee,

            "fields": {
                "eCO2": sgp30.eCO2,
                "TVOC": sgp30.TVOC,
            }
        }
    ]
    # write the measurement
    ifclient.switch_database('home')
    ifclient.write_points(body)
