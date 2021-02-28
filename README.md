# home_values

# Run scripts at startup

```
sudo nano /etc/rc.local
```

Add the line below to the script. Make sure to also add a `&` at the
end to run in seperate process. Because the Python scripts run in a
infite loop and will prevent further booting.

```
# Read temperature, humidity and airpressure
sudo python /home/pi/Repos/home_values/temperature.py &
```