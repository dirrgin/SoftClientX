from azure.iot.device import IoTHubModuleClient, Message, MethodResponse, MethodRequest, IoTHubDeviceClient
import asyncio
import json
#D2C, C2D receive, direct methods, device twin, handlers
def twinPatch_Handler(twinPatch):
    print("Twin patch received:", twinPatch)
    # add a code to process the twinPatch and update a device settings

def prepareClient(connectionString):
    iotClient = IoTHubModuleClient.create_from_connection_string(connectionString)
    try:
        iotClient.on_twin_desired_properties_patch_received = twinPatch_Handler
        iotClient.connect()
    except Exception as e:
        print(f"IOT HUB Connection failed: {e}")
        iotClient.shutdown()
        raise
    return iotClient


async def DtoC(device, iotClient): 
    iotClient.send_message(str(device.packTelemetry()))

async def twinReport(device, iotClient):
    reportedProperties = {"Device" + str(device.repr)[-1]: {"ProductionRate": device.productionRate, "DeviceErrors": "0000"}}                                          
    iotClient.patch_twin_reported_properties(reportedProperties)

