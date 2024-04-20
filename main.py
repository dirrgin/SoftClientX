from ProductionLineAgent import IoTHubModuleClient, DtoC, twinReported
from asyncua import Client
from AbstractDevice import asyncio, ua, productionDevice
import sys

async def main():
    _iotDevKey ="HostName=Cirencester-End.azure-devices.net;DeviceId=demo_device1;SharedAccessKey=rq4bvlv6Jd3UEKJL6zHVt2IuwdpKbHhwMAIoTHcgMho="
    _opcUaServer = "opc.tcp://10.103.0.110:4840/"
    opcClient = Client(_opcUaServer)
    iotClient = IoTHubModuleClient.create_from_connection_string(_iotDevKey)
    try:
        await opcClient.connect()
    except Exception as exc:
        print("OPC UA Connection failed")
        print(f"Error: {exc}")
        #sys.exit(1)
    else:
        print("OPC UA successful connection")

    try:
        iotClient.connect()
    except Exception as e:
        print("IOT HUB Connection failed")
        print(f"Error: {e}")
        sys.exit(1)
    else:
        print("IOT HUB successful connection")
    
    print("Reading production line devices...")
    nodes = []
    nodes = await opcClient.get_objects_node().get_children()
    nodes = nodes[1:]
    devices = []
    for node in range(len(nodes)):
        nodeRepr = opcClient.get_node(nodes[node])
        temp = productionDevice(opcClient, nodeRepr)
        await temp.getDevProp()
        devices.append(temp)
    
    twin = iotClient.get_twin()['reported']
    del twin["$version"]
    for key, value in twin.items():
        twin[key] = None
    iotClient.patch_twin_reported_properties(twin)
    
    for it in range(len(devices)):
        print(it)
        await DtoC(devices[it], iotClient)
        await twinReported(devices[it], iotClient)

if __name__ == "__main__":
    asyncio.run(main())