import time
import sys
from AbstractDevice import productionDevice, asyncio, ua
from asyncua import Client
from ProductionLineAgent import \
    IoTHubModuleClient, \
    Message, \
    d2c, \
    twin_reported, \
    receive_twin_desired, \
    take_direct_method
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties

async def clear_desired_twin(iothub_registry_manager, device):
    twin = iothub_registry_manager.get_twin(device)
    des = twin.properties.desired
    del des["$metadata"]
    del des["$version"]
    for key, value in des.items():
        des[key] = None
    twin_patch = Twin(properties=TwinProperties(desired=des))
    twin = iothub_registry_manager.update_twin(device, twin_patch, twin.etag)

async def main():
    opcua_endpoint = "opc.tcp://10.103.0.110:4840/"
    CONNECTION_STRING = "HostName=Cirencester-End.azure-devices.net;DeviceId=demo_device1;SharedAccessKey=rq4bvlv6Jd3UEKJL6zHVt2IuwdpKbHhwMAIoTHcgMho="
    CONNECTION_STRING_MANAGER="HostName=Cirencester-End.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=4THcWqn7NQdn21nYhOcsUm6iWCa3Z4knLAIoTDcDVKI="
    client_opc = Client(opcua_endpoint)

    DEVICE_ID = "demo_device1"
    iothub_registry_manager = IoTHubRegistryManager(CONNECTION_STRING_MANAGER)
    await clear_desired_twin(iothub_registry_manager, DEVICE_ID)
    

    # Connection to OPC UA server
    try:
        await client_opc.connect()
    except Exception as e:
        print("OPC UA connection failed")
        print(f"Error: {e}")
        sys.exit(1)
    else:
        print("OPC UA connection success")

    # Connection to IoTHub
    try:
        client_iot = IoTHubModuleClient.create_from_connection_string(CONNECTION_STRING)
        client_iot.connect()
    except Exception as e:
        print("IoTHub connection failed")
        print(f"Error: {e}")
        sys.exit(1)
    else:
        print("IoTHub connection success")

    # Clean the reported twin
    twin = client_iot.get_twin()['reported']
    del twin["$version"]
    for key, value in twin.items():
        twin[key] = None
    client_iot.patch_twin_reported_properties(twin)


    lst_dev_err_old = []
    try:
        while True:
            lst = await client_opc.get_objects_node().get_children()
            lst = lst[1:]

            # list of actual devices
            lst_machines = []
            # actualization
            lst_dev_err_new = []

            # write devices in list and update data
            for i in range(len(lst)):
                nodeRepr = client_opc.get_node(lst[i])
                device = productionDevice(client_opc, nodeRepr)
                await device.getDevProp()
                lst_machines.append(device)
                lst_dev_err_new.append(device.error)
                #print("\t write devices in list and update data ", i)
                #print(lst_machines[i])
                #print(lst_dev_err_new[i])

            await receive_twin_desired(client_iot, lst_machines)
            print("after receive_twin_desired")
            # print actual data about our devices
            for j in range(len(lst_machines)):
                print("\t device ** :", str(lst_machines[j].repr))
                await d2c(client_iot, lst_machines[j])
                await twin_reported(client_iot, lst_machines[j])

            # take a direct methods and call them
            await take_direct_method(client_iot, client_opc)#🌐

            time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard stopped program")

    # disconnect
    await client_opc.disconnect()
    client_iot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())