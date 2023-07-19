# Inkbird-IBS-P01B-REST
Reads Inkbird IBS-P01B Bluetooth sensor and provides a REST API for polling the temperature value

## Installation
Assuming bluetooth is up and running and python bluetooth packages are installed, run

```shell
sudo pip3 install -r requirements.txt
```

## Configuration
Change [`config.ini`](config.ini.template), add the MAC of your Inkbird device.
To get the MAC, run a BTLE scanning app and search for your device. 

You can create the file by copying the template:

```shell
cp config.{ini.template,ini}
vim config.ini
```

## Daemon Mode
To add a systemd service, run the following commands and don't forget to set daemon mode to True in the configuration file.

```shell
sudo cp /opt/Inkbird-IBS-P01B-REST/template.service /etc/systemd/system/inkbird.service

sudo systemctl daemon-reload

sudo systemctl start inkbird.service
sudo systemctl status inkbird.service

sudo systemctl enable inkbird.service
```

## Home Assistant Sensor
The easiest way to use the device within Home Assistant is to define a REST sensor. 

```yaml
sensor:
  - platform: rest
    resource: http://<IP>:5000/temperature
    name: "Temp Sensor"
    device_class: temperature
    unit_of_measurement: "°C"
    scan_interval: 900
```

## Credit
Script inspired by:
- https://github.com/ptc/Inkbird-IBS-P01B-MQTT
