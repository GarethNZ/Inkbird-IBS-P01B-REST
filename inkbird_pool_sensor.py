
from time import sleep
import simplepyble
import logging

class InkBirdPoolSensor:
    # TODO add these to config.ini
    characteristic_uuid = "0000fff2-0000-1000-8000-00805f9b34fb"

    def __init__(self, peripheral_mac) -> None:
        self.peripheral_mac = peripheral_mac

        self.connect()

    @staticmethod
    def float_value(nums):
        # check if temp is negative
        num = (nums[1]<<8)|nums[0]
        if nums[1] == 0xff:
            num = -( (num ^ 0xffff ) + 1)
        return float(num) / 100

    @staticmethod
    def c_to_f(temperature_c):
        return 9.0/5.0 * temperature_c + 32

    def connect_to_peripheral(self):
        adapters = simplepyble.Adapter.get_adapters()

        if len(adapters) == 0:
            logging.error("No adapters found")
            exit()

        adapter = adapters[0]
        result = adapter.scan_for(5000)
        peripherals = adapter.scan_get_results()

        for i, peripheral in enumerate(peripherals):
            if peripheral.address() == self.peripheral_mac:
                return peripheral
        return None

    def get_temperature_service(self, peripheral):
        services = peripheral.services()
        logging.info(f"Looking for service and characteristic")
        for service in services:
            for characteristic in service.characteristics():
                logging.debug(f"{service.uuid()} {characteristic.uuid()}")
                if characteristic.uuid() == InkBirdPoolSensor.characteristic_uuid:
                    return service, characteristic
        return None, None


    def connect(self):
        self.peripheral = self.connect_to_peripheral()
        if self.peripheral is None:
            logging.error(f"Peripheral {self.peripheral_mac} not found")
            exit()
        logging.info(f"Connecting to {self.peripheral_mac}")

        # TODO: ensure disconnect
        self.peripheral.connect()

        self.service, self.characteristic = self.get_temperature_service(self.peripheral)

        if self.service is None or self.characteristic is None:
            logging.error("Unable to find required service or characteristic")
            exit()

    def read_current_value(self):
        try:
            if not self.peripheral.is_connected():
                self.peripheral.connect()
            raw_value = self.peripheral.read(self.service.uuid(), self.characteristic.uuid())
            if raw_value is None:
                return None
            # little endian, first two bytes are temp
            self.temperature_c = self.float_value(raw_value[0:2])
            
            logging.info("temperature: {}".format(self.temperature_c))

            return self.temperature_c
        except Exception as ex:
            # TODO: Reconnect if the error was "Peripheral is not connected."
            template = "Error reading BTLE: type {0}. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.error(message)
            #if (ex is RuntimeError):
                #then ex.args = ('Peripheral is not connected.',)
                # Ignore the failure for now
            return False

    def daemon_function_loop(self, read_interval):
        while True:
            self.current_temp = self.read_current_value()
            
            logging.debug('Going to sleep for {} seconds ...'.format(read_interval))
            sleep(read_interval)
            
        # TODO: On script end
        #peripheral.disconnect()