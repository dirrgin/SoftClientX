from AbstractDevice import productionDevice, asyncio, MSG_TXT, Client, ua
from azure.iot.device import IoTHubModuleClient, Message, MethodResponse, MethodRequest
import datetime, json

MSG_LOG = '{{"Name": {name},"DeviceId": {deviceId}}}'
INTERVAL = 2

class ProductionAgent:
    def __init__(self, opcClient, connectionString):
        self.deviceBox = []
        self.opcClient = opcClient
        self.amount = None
        self.iotClient = None
        self.connectionString = connectionString

    async def initialize(self):
        self.iotClient = IoTHubModuleClient.create_from_connection_string(self.connectionString)
        try: 
            self.iotClient.connect()
            print("Successful connection to IOT HUB")
        except:
            self.iotClient.stutdown()
            raise
    def message_received_handler(message):
        print("the data in the message received was ")
        print(message.data)
        print("custom properties are")
        print(message.custom_properties)

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

    # async def updateTwinAsync(self): #report into the twin
    #     # Retrieve the twin
    #     twin = await self.iotClient.get_twin()
    #     print(f"\tInitial twin value received:\n{twin}")
    #     reported_properties = {}

    #     for device in self.deviceBox:
    #         device_id = "Device " + str(device.repr)[-1]
    #         reported_properties[device_id] = {
    #             "DateTimeLastAppLaunch": datetime.datetime.now().isoformat(),
    #             "ProductionRate": device.productionRate,
    #             "DeviceErrors": "0000"
    #         }
    #     await self.iotClient.patch_twin_reported_properties(reported_properties)

    #     message = Message(json.dumps(reported_properties))
    #     message.content_encoding = "utf-8"
    #     message.content_type = "application/json"
    #     # Send the message
    #     await self.iotClient.send_message(message)
        
    async def twinPatchHandler(self, desired_properties):
        print("Desired property change received: {}".format(desired_properties))
        reported_properties = {
            "DateTimeLastDesiredPropertyChangeReceived": datetime.datetime.now().isoformat()
        }
        await self.iotClient.patch_twin_reported_properties(reported_properties)
            
    async def methodRequestHandler(self, method_request):
        print(MSG_LOG.format(name=method_request.name, deviceId=method_request.deviceId))
        if method_request.name == "EmergencyStop":
            #if it experiences more than 3 errors in under 1 minut
            try:
                emStop = self.opcClient.get_node(method_request.deviceId)
                node = self.opcClient.get_node(method_request.deviceId)
                await node.call_method(emStop)
                print("Emergency stop called")
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined ".format(method_request.name)}
            response_status = 404
        method_response = MethodResponse.create_from_method_request(method_request, response_status, response_payload)
        await self.iotClient.send_method_response(method_response)

    async def initializeHandlers(self):
        try:
            await self.initialize()
            self.iotClient.on_method_request_received = self.methodRequestHandler
            self.iotClient.on_twin_desired_properties_patch_received = self.twinPatchHandler
            self.iotClient.on_message_received_handler = self.message_received_handler
            twin =  self.iotClient.get_twin()#✅
            print ( "Twin at startup is" )
            print ( twin )
            await self.readUANodes()
        except Exception as e:
            print(f"IOT HUB failed: {e}")
            self.iotClient.shutdown()
            return   
       
    
    async def run(self):
        while True:
            tasks = [device.getDevProp() for device in self.deviceBox]
            await asyncio.gather(*tasks)
            telemetry_data=[]
            for dev in self.deviceBox:
                telemetry_dict = dev.packTelemetry()
                telemetry_data.append(telemetry_dict)
            message_payload = json.dumps(telemetry_data)
            message = Message(message_payload)
            #message.content_encoding = "utf-8"
            #message.content_type = "application/json"
            
            print("Sending d2c: {}".format(message))
            self.iotClient.send_message(message)
            print("d2c sent.")
            await asyncio.sleep(60)
       
        

