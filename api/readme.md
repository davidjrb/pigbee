## Basic DeConz API commands

replace `100.93.70.27` with your controller's IP

replace `7156FE2C12` with your controller's API token

### To control a group no.`4`:

**Turn group ON**
```bash
curl -X PUT -d '{"on": true}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**Turn group OFF**
```bash
curl -X PUT -d '{"on": false}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**MAX brightness, transition 10 seconds**
```bash
curl -X PUT -d '{"bri": 254, "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**MIN brightness, transition 10 seconds**
```bash
curl -X PUT -d '{"bri": 1, "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**Color Temperature: 2000K (very warm amber), transition 10 seconds**
```bash
curl -X PUT -d '{"xy": [0.526, 0.413], "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**Color Temperature: 5500K (cool, bright white), transition 10 seconds**
```bash
curl -X PUT -d '{"bri": 254, "xy": [0.33, 0.34], "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/groups/4/action
```

**Get status of group**
```bash
curl -X GET http://100.93.70.27/api/7156FE2C12/groups/4
```

---

### To control a single light

Turn light ON
~~~
curl -X PUT -d '{"on": true}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

Turn light OFF
~~~
curl -X PUT -d '{"on": false}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

MAX brightness, transition 10 seconds
~~~
curl -X PUT -d '{"bri": 254, "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

MIN brightness, transition 10 seconds
~~~
curl -X PUT -d '{"bri": 254, "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

Color Temperature: 2000K (very warm amber), transition 10 seconds
~~~
curl -X PUT -d '{"xy": [0.526, 0.413], "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

Color Temperature: 5500K (cool, bright white), transition 10 seconds
~~~
curl -X PUT -d '{"bri": 254, "xy": [0.33, 0.34], "transitiontime": 100}' http://100.93.70.27/api/7156FE2C12/lights/1/state
~~~

Get status of light
~~~
curl -X GET http://100.93.70.27/api/7156FE2C12/lights/1
~~~

