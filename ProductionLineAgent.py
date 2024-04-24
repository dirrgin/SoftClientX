from AbstractDevice import productionDevice, asyncio, Client, ua
from azure.iot.device import IoTHubModuleClient, Message, MethodResponse, MethodRequest
import datetime, json


class ProductionAgent:
    def __init__(self, opcClient, connectionString):
        self.deviceBox = []
        self.opcClient = opcClient
        self.amount = None
        self.iotClient = None
        self.connectionString = connectionString

    async def initialize(self):
        self.iotClient = IoTHubModuleClient.create_from_connection_string(self.connectionString)
        self.iotClient.connect()

    async def readUANodes(self):
        print("Reading production line devices...")
        nodes={}
        nodes = await self.opcClient.get_objects_node().get_children()
        nodes = nodes[1:]
        self.amount = len(nodes)
        for node in range(self.amount):
            nodeRepr = self.opcClient.get_node(nodes[node])
            temp = productionDevice(self.opcClient, nodeRepr)
            await temp.getDevProp()
            self.deviceBox.append(temp)

    async def DtoC(self, messageContent): 
        if isinstance(messageContent, dict):
            messageContent = json.dumps(messageContent)
        try:
            await self.iotClient.send_message(messageContent)
        except Exception as e:
            print(f"An error occurred: {e}")

    async def updateTwinAsync(self): #report into the twin
        # Retrieve the twin
        twin = await self.iotClient.get_twin()
        print(f"\tInitial twin value received:\n{twin}")
        #update properties
        device_id = "Device " + str(self.repr)[-1]  # Extract the device identifier
        reported_properties = {
            device_id: {
                "DateTimeLastAppLaunch": datetime.datetime.now().isoformat(),
                "ProductionRate": self.productionRate,
                "DeviceErrors": "0000"
            }
        }
        await self.iotClient.patch_twin_reported_properties(reported_properties)
     #get desired properties from a hub and send an acknowledge
        
    async def onDesiredPropertyChange(self, desired_properties):
        print("Desired property change received: {}".format(desired_properties))
        reported_properties = {
            "DateTimeLastDesiredPropertyChangeReceived": datetime.datetime.now().isoformat()
        }
        # Use the client (passed as user_context) to patch the reported properties
        await self.iotClient.patch_twin_reported_properties(reported_properties)

    async def update_device_telemetry(self):
        while True:
            tasks = [device.getDevProp() for device in self.deviceBox]
            await asyncio.gather(*tasks)
            print("updating devices in a box ... ")
            for dev in self.deviceBox:
                print(dev)
            telemetry_data = [dev.packTelemetry() for dev in self.deviceBox]
            await self.DtoC(telemetry_data)
            print("Sent telemetry for devices:", telemetry_data)
            # Wait for a minute before repeating the process
            await asyncio.sleep(60)

    async def initializeHandlers(self):
        # Attach the Cloud-to-Device message handler
        #self.client.on_message_received = self.DtoC
        # Attach the direct method handler (if any direct methods are to be handled)
        # Attach the desired property update callback
        self.iotClient.on_twin_desired_properties_patch_received = self.onDesiredPropertyChange
    
    async def run(self):
        try:
            await self.initialize()
        except Exception as e:
            print(f"IOT HUB Connection failed: {e}")
            await self.iotClient.shutdown()
            return
        await self.readUANodes()
        await self.initializeHandlers()
        telemetry_task = asyncio.create_task(self.update_device_telemetry())
        # Run the telemetry task indefinitely
        await telemetry_task

        

