from ProductionLineAgent import IoTHubModuleClient, DtoC, twinReport, prepareClient
from asyncua import Client
from AbstractDevice import asyncio, ua, productionDevice
from ServiceManager import IoTHubRegistryManager, receiveTwinReported, prepareDesiredTwin, updateTwinDesired
import sys
_iotManKey = "HostName=Cirencester-End.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=4THcWqn7NQdn21nYhOcsUm6iWCa3Z4knLAIoTDcDVKI="
_iotDevName = "demo_device1"
_iotDevKey ="HostName=Cirencester-End.azure-devices.net;DeviceId=demo_device1;SharedAccessKey=rq4bvlv6Jd3UEKJL6zHVt2IuwdpKbHhwMAIoTHcgMho="
_opcUaServer = "opc.tcp://10.103.0.110:4840/"   
async def main():
    iotClient = prepareClient(_iotDevKey)
    opcClient = Client(_opcUaServer)
    iotManager = IoTHubRegistryManager(_iotManKey)
    ####
    try:
        await opcClient.connect()
    except Exception as exc:
        print("OPC UA Connection failed")
        print(f"Exception Type: {type(exc).__name__}")
        print(f"Error: {exc}")
        sys.exit(1)
    else:
        print("OPC UA successful connection")
    
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
    print("1. Prepare (CLEAN) desired twin ... ")
    await prepareDesiredTwin(iotManager, _iotDevName)
    
    print("2. Client gets a twin ")
    twin = iotClient.get_twin()['reported']

    print("Twin items before clean: ", twin.items())
    del twin["$version"]
    for key, value in twin.items():
        twin[key] = None
    print("TWin items after clean: ", twin.items())
    await asyncio.sleep(30)
    print("3. Update reported properties")
    iotClient.patch_twin_reported_properties(twin)

    print("4. Send D2C and send a raport2C")
    for it in range(len(devices)):
        print(it)
        await DtoC(devices[it], iotClient)
        await twinReport(devices[it], iotClient)

    print("MANAGER SIDE **** ")
    await asyncio.sleep(40)
    print("5. Receive reported twin")
    getTwinReported = await receiveTwinReported(iotManager, _iotDevName)
    print(getTwinReported)

    print("5. Update desired twin")
    await updateTwinDesired(iotManager, _iotDevKey, getTwinReported)

if __name__ == "__main__":
    asyncio.run(main())