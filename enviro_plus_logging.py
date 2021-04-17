#!/usr/bin/env python3

# Script for reading temperature, air humidity and air
# pressure from the pimoroni enviro+ sensor. The results
# are written to a local SQLite database.
#
# The standard settings and names are:
# database name = home_values.db
# table_name = enviro
#
# Both the database and table need to be created manually.

# Settings
readout_freq = 5 # Set the frequency of the readout in seconds
database_location = '/home/pi/Databases/SQLite/home_values.db'


# Import packages
import time
import colorsys
import sys
import sqlite3
import time
import logging
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from subprocess import PIPE, Popen

# Init sensors
bme280 = BME280()
pms5003 = PMS5003()

# Temperature correction for cpu temperature radiation to the sensor
# for a raspberry pi zero
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

factor = 2.25 # Tuning factor
cpu_temps = [get_cpu_temperature()] * 5

def insertValuesEnviro(timestamp, temperature, humidity, lux, oxidizing, reducing, nh3, pm1, pm2_5, pm10, pressure):
    try:
        sqliteConnection = sqlite3.connect(database_location)
        cursor = sqliteConnection.cursor()
        print("Connected to database")

        sqlite_insert_with_param = """INSERT INTO enviro
                          (timestamp, temperature, humidity, lux, oxidizing, reducing, nh3, pm1, pm2_5, pm10, pressure) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        data_tuple = (timestamp, temperature, humidity, lux, oxidizing, reducing, nh3, pm1, pm2_5, pm10, pressure)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        print("Python Variables inserted successfully into the table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The database connection is closed")


# Get all values from the sensors
try:
    while True:
        cpu_temp = get_cpu_temperature()
        raw_temp = bme280.get_temperature()
        data_temp = raw_temp - ((cpu_temp - raw_temp) / factor)
        data_humi = bme280.get_humidity()
        data_lux = ltr559.get_lux()
        data_gas = gas.read_all()
        data_oxi = data_gas.oxidising / 1000
        data_red = data_gas.reducing / 1000,
        data_nh3 = data_gas.nh3 / 1000
        try:
            data_part = pms5003.read()
        except pmsReadTimeoutError:
            logging.warning("Failed to read PMS5003")
        else:
            data_pm1 = float(data_part.pm_ug_per_m3(1.0))
            data_pm2_5 = float(data_part.pm_ug_per_m3(2.5))
            data_pm10 = float(data_part.pm_ug_per_m3(10))
        data_time = int(time.time())
        data_pres = bme280.get_pressure()
        insertValuesEnviro(str(data_time), str(data_temp), str(data_humi), str(data_lux), str(data_oxi), str(data_red), str(data_nh3), str(data_pm1), str(data_pm2_5), str(data_pm10), str(data_pres))
        
        print_values = ("Temp: " + str(data_temp) + 
        " Humi: " + str(data_humi) + 
        " Lux: " + str(data_lux) +
        " Oxi: " + str(data_gas.oxidising / 1000) +
        " Redu: " + str(data_gas.reducing / 1000) +
        " NH3: " + str(data_gas.nh3 / 1000) +
        " pm1: " + str(data_pm1) +
        " pm2_5: " + str(data_pm2_5) + 
        " pm10: " + str(data_pm10))
        print(print_values)
        print(data_time)

        time.sleep(readout_freq)

except KeyboardInterrupt:
    pass