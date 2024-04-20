from azure.iot.device import IoTHubModuleClient, Message, MethodResponse, MethodRequest, IoTHubDeviceClient
import asyncio
import json
#D2C, C2D receive, direct methods, device twin, handlers

async def DtoC(device, iotClient): 
    iotClient.send_message(str(device.packTelemetry()))

async def twinReported(device, iotClient):
    reportedProperties = {"Device" + str(device.repr)[-1]: {"ProductionRate": device.productionRate, "DeviceErrors": "0000"}}                                                       }}
    iotClient.patch_twin_reported_properties(reportedProperties)

