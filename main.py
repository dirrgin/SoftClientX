from ProductionLineAgent import ProductionAgent, asyncio, Client, IoTHubModuleClient

from ServiceManager import IoTHubRegistryManager, receiveTwinReported, prepareTwin, updateTwinDesired
import sys
_iotManKey = "HostName=Cirencester-End.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=4THcWqn7NQdn21nYhOcsUm6iWCa3Z4knLAIoTDcDVKI="
_iotDevName = "demo_device1"
_iotDevKey ="HostName=Cirencester-End.azure-devices.net;DeviceId=demo_device1;SharedAccessKey=rq4bvlv6Jd3UEKJL6zHVt2IuwdpKbHhwMAIoTHcgMho="
_opcUaServer = "opc.tcp://10.103.0.110:4840/"   
async def main():
    opcClient = Client(_opcUaServer)
    #iotManager = IoTHubRegistryManager(_iotManKey)
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
    iotClient = ProductionAgent(opcClient, _iotDevKey)
    await iotClient.initializeHandlers()
    await iotClient.run()
   
    '''
    print("MANAGER SIDE **** ")
    await asyncio.sleep(40)
    print("5. Receive reported twin")
    getTwinReported = await receiveTwinReported(iotManager, _iotDevName)
    print(getTwinReported)

    print("5. Update desired twin")
    await updateTwinDesired(iotManager, _iotDevKey, getTwinReported)'''

if __name__ == "__main__":
    asyncio.run(main())