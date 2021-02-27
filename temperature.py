#!/usr/bin/env python

# Script for reading temperature, air humidity and air
# pressure from the pimoroni BME680 sensor. The results
# are written to a local SQLite database.
#
# The standard settings and names are:
# database name = home_values.db
# table_name = results_thp
#
# Both the database and table need to be created manually.

# Settings
readout_freq = 5 # Set the frequency of the readout in seconds
database_location = '/home/pi/Databases/SQLite/home_values.db'

# Import packages
import bme680
import time
import sqlite3

# Functions
def insertValuesTHP(temperature, airpressure, humidity, timestamp):
    try:
        sqliteConnection = sqlite3.connect(database_location)
        cursor = sqliteConnection.cursor()
        print("Connected to database")

        sqlite_insert_with_param = """INSERT INTO results_thp
                          (temperature, airpressure, humidity, timestamp) 
                          VALUES (?, ?, ?, ?);"""

        data_tuple = (temperature, airpressure, humidity, timestamp)
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

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# Sensor data
# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

# Read data from BME680 sensor and write to defined
# database.
print('Getting values:')
try:
    while True:
        if sensor.get_sensor_data():
            output = '{0:.2f},{1:.2f},{2:.3f}'.format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity)
            output = output + "," + str(int(time.time()))
            output = output.split(',')
            insertValuesTHP(output[0], output[1], output[2], output[3])
            print(output)
        time.sleep(readout_freq)

except KeyboardInterrupt:
    pass
