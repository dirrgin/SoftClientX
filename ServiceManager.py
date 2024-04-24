from azure.iot.hub import IoTHubRegistryManager
from ProductionLineAgent import asyncio, MethodResponse, MethodRequest, Client, ua
from azure.iot.device import IoTHubDeviceClient

'''async def prepareDesiredTwin(iotManager, deviceId):
    twin = iotManager.get_twin(deviceId)
    desiredProp = twin.properties.desired
    del desiredProp["$metadata"]
    del desiredProp["$version"]
    print(desiredProp)
    for key, value in desiredProp.items():
        print("key: ", key, ": ", desiredProp[key])
        desiredProp[key] = None
    twinPatch = Twin(properties=TwinProperties(desired=desiredProp))
    twin = iotManager.update_twin(deviceId, twinPatch, twin.etag)
    print("iotManager changed desired twin: ", desiredProp)'''
#clean all the properties in a Twin
async def prepareTwin(iotManager, deviceId):
    twin = iotManager.get_twin(deviceId)
    # Clear desired properties
    desired_prop = twin.properties.desired
    desired_prop["$metadata"]= None
    desired_prop["$version"]= None

    # Clear reported properties
    reported_prop = twin.properties.reported
    reported_prop["$metadata"]= None
    reported_prop["$version"]= None

    # Construct the patch for the twin with cleared properties
    twin_patch = Twin(properties=TwinProperties(desired=desired_prop, reported=reported_prop))

    # Update the twin using the patch
    twin = iotManager.update_twin(deviceId, twin_patch, twin.etag)

    # Output the result
    print("Cleared desired and reported properties from the twin: ", twin_patch)

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