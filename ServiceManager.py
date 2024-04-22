import asyncio
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, CloudToDeviceMethod
import json

async def prepareDesiredTwin(iotManager, deviceId):
    twin = iotManager.get_twin(deviceId)
    desiredProp = twin.properties.desired
    del desiredProp["$metadata"]
    del desiredProp["$version"]
    for key, value in desiredProp.items():
        desiredProp[key] = None
    twinPatch = Twin(properties=TwinProperties(desired=desiredProp))
    twin = iotManager.update_twin(deviceId, twinPatch, twin.etag)

async def receiveTwinReported(iotManager, deviceId):
    twin = iotManager.get_twin(deviceId)
    reportedProps = twin.properties.reported
    return reportedProps

async def updateTwinDesired(iotManager, deviceId, reported):
    desired = {}
    del reported["$metadata"]
    del reported["$version"]
    for key, value in reported.items():
        desired[key] = {"ProductionRate": value["ProductionRate"]}
    twin = iotManager.get_twin(deviceId)
    twin_patch = Twin(properties=TwinProperties(desired=desired))
    twin = iotManager.update_twin(deviceId, twin_patch, twin.etag)