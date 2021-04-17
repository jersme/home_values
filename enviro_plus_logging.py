#!/usr/bin/env python3

# Script for reading temperature, air humidity and air
# pressure from the pimoroni enviro+ sensor. The results
# are written to a local SQLite database.
#
# The standard settings and names are:
# database name = home_values.db
# table_name = results_thp
#
# Both the database and table need to be created manually.


# Import packages
import time
import colorsys
import sys
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

# Get temperature
try:
    while True:
        cpu_temp = get_cpu_temperature()
        raw_temp = bme280.get_temperature()
        data_temp = raw_temp - ((cpu_temp - raw_temp) / factor)
        print(data_temp) 
        time.sleep(2)

except KeyboardInterrupt:
    pass