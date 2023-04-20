import simplepyble

#debug from pprint import pprint
from pprint import pprint

def float_value(nums):
    # check if temp is negative
    num = (nums[1]<<8)|nums[0]
    if nums[1] == 0xff:
        num = -( (num ^ 0xffff ) + 1)
    return float(num) / 100

if __name__ == "__main__":
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    if len(adapters) > 1:    
        # Query the user to pick an adapter
        print("Please select an adapter:")
        for i, adapter in enumerate(adapters):
            print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

        choice = int(input("Enter choice: "))
        adapter = adapters[choice]
    else:
        adapter = adapters[0]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

    # Scan for 5 seconds
    adapter.scan_for(5000)
    peripherals = adapter.scan_get_results()

    
    # Connect to 49:22:05:28:0d:0e
    peripheral = None
    peripheralID = "49:22:05:28:0d:0e"
    for i, peripheralOption in enumerate(peripherals):
        if peripheralOption.address() == peripheralID:
            peripheral = peripheralOption

    if peripheral is None:
        print(f"Peripheral {peripheralID} not found")
        exit()
    # Query the user to pick a peripheral
    # print("Please select a peripheral:")
    # for i, peripheral in enumerate(peripherals):
    #     print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

    # choice = int(input("Enter choice: "))
    # peripheral = peripherals[choice]

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral.connect()

    print("Successfully connected, listing services...")
    services = peripheral.services()
    service_characteristic_pair = []
    for service in services:
        for characteristic in service.characteristics():
            service_characteristic_pair.append((service.uuid(), characteristic.uuid()))
            print(f"{service.uuid()} {characteristic.uuid()}")
            try:
                contents = peripheral.read(service.uuid(), characteristic.uuid())
                print(f"Contents: {contents}")
                if characteristic.uuid() == "0000fff2-0000-1000-8000-00805f9b34fb":
                    temperature_c = float_value(contents[0:2])
                    print(f"temperature: {temperature_c}")
            except RuntimeError:
                print("Cannot be read")

    # # Query the user to pick a service/characteristic pair
    # print("Please select a service/characteristic pair:")
    # for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
    #     print(f"{i}: {service_uuid} {characteristic}")

    # choice = int(input("Enter choice: "))
    # service_uuid, characteristic_uuid = service_characteristic_pair[choice]

    # # Write the content to the characteristic
    # contents = peripheral.read(service_uuid, characteristic_uuid)
    # print(f"Contents: {contents}")

    peripheral.disconnect()