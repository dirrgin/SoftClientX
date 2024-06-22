import json,sys
from azure.iot.device import IoTHubModuleClient, MethodResponse
from AbstractDevice import asyncio
#from azure.iot.hub.models import Twin, TwinProperties

async def connect_to_devices(connection_strings):
    productionLine=[]
    for connection in connection_strings:
        if connection:
            try:
                client_iot = IoTHubModuleClient.create_from_connection_string(connection)
                client_iot.connect()
                await asyncio.sleep(1)
                productionLine.append(client_iot)
            except Exception as e:
                print("Device connection failed")
                print(f"Error: {e}")
                sys.exit(1)
            else:
                print("Device connection success! ")
    return productionLine

'''async def clear_desired_twin(iothub_registry_manager, device):
    twin = iothub_registry_manager.get_twin(device)
    des = twin.properties.desired
    del des["$metadata"]
    del des["$version"]
    for key, value in des.items():
        des[key] = None
    twin_patch = Twin(properties=TwinProperties(desired=des))
    twin = iothub_registry_manager.update_twin(device, twin_patch, twin.etag)'''

def clean_twin(productionLine):
    for client_iot in productionLine:
        try:
            twin = client_iot.get_twin()['reported']
            del twin["$version"]
            client_iot.patch_twin_reported_properties(twin)
        except Exception as e:
            print(f"Failed to clean twin for device: {e}")


async def d2c(client, machine):
    message = {}
    message["DeviceName"] = machine.azureId
    message["MachineName"] = str(machine.repr)[7:]
    message["ProductionStatus"] = machine.productionStatus
    message["WorkorderId"] = machine.workorderId
    message["ProductionRate"] = machine.ProductionRate
    message["GoodCount"] = machine.goodCount
    message["BadCount"] = machine.badCount
    message["Temperature"] = machine.temperature
    message["DeviceError"] = machine.error
    error_sum = sum(machine.error)
    if error_sum > 0:
        message["IsDevErr"] = "true"
    else:
        message["IsDevErr"] = "false"
    message_json = json.dumps(message)
    client.send_message(message_json.encode('utf-8'))

#When value changes, a single D2C message must be sent to IoT platform
async def d2c_Error(client, machine):
    message = {}
    message["DeviceName"] = machine.azureId
    message["MachineName"] = str(machine.repr)[7:]
    message["ProductionStatus"] = 3
    message["WorkorderId"] = machine.workorderId
    message["ProductionRate"] = 0
    message["GoodCount"] = 0
    message["BadCount"] = 0
    message["Temperature"] = 0
    define_error = ""
    if machine.error[0]==1:
        define_error+="Unknown, "
    if machine.error[1]==1:
        define_error+="Sensor Failure, "
    if machine.error[2]==1:
        define_error+="Power Failure, "  
    if machine.error[3]==1:
        define_error+="Emergency Stop"  
    if define_error.endswith(", "):
        define_error = define_error[:-2]
    message["DeviceError"] = define_error
    message["IsDevErr"] = "true"
    print("d2c error: ", define_error)
    message_json = json.dumps(message)
    client.send_message(message_json.encode('utf-8'))

async def twin_reported(client, machine):
    reported_props = {"ProductionRate": machine.ProductionRate,"Errors": machine.error}
    
    client.patch_twin_reported_properties(reported_props)


async def compare_production_rates(twin_patch, lst_devices):
    for i in range(len(lst_devices)):
        name = "Device" + str(lst_devices[i].repr)[-1]
        rate = twin_patch["ProductionRate"]
        if rate != lst_devices[i].ProductionRate:
            await lst_devices[i].set_prod_rate(rate)
            print(f"{name} set production rate successfully to {rate}")


async def receive_twin_desired(client, machine):
    def twin_patch_handler(twin_patch):
        try:
            print("Twin patch received.")
            twin_patch.pop('$version', None)
            print("received desired properties: \t", twin_patch)
            name = "Device" + str(machine.repr)[-1]
            rate = twin_patch['ProductionRate']
            if rate != machine.ProductionRate:
                asyncio.run(machine.set_prod_rate(rate))
                print(f"{name} set production rate successfully to {rate}")
        except Exception as e:
            print(f"Exception in twin_patch_handler: {str(e)}")
    try:
        client.on_twin_desired_properties_patch_received = twin_patch_handler
    except Exception as e:
        print(f"Exception in receive_twin_desired: {str(e)}")


async def run_emergency_stop(opc_client, device_name):
    try:
        nodeES = opc_client.get_node(f"ns=2;s={device_name}/EmergencyStop")
        node = opc_client.get_node(f"ns=2;s={device_name}")
        await node.call_method(nodeES)
        print("Emergency stop called. Success")
    except Exception as opc_er:
        print(f"Emergency stop Error: {opc_er}")


async def run_res_err_status(opc_client, device_name):
    try:
        nodeRES = opc_client.get_node(f"ns=2;s={device_name}/ResetErrorStatus")
        node = opc_client.get_node(f"ns=2;s={device_name}")
        await node.call_method(nodeRES)
        print("Reset error status called. Success")
    except Exception as opc_er:
        print(f"Reset error status Error: {opc_er}")


async def take_direct_method(client, machine):
    def handle_method(request):
        try:
            print(f"Direct Method called: {request.name}")
            print(f"Request: {request}")
            print(f"Payload: {request.payload}")
            device_name = "Device " + str(machine.repr)[-1]
            if request.name == "emergency_stop":
                asyncio.run(run_emergency_stop(machine.client, device_name))
                payload = {"result": True}
                status = 200
            elif request.name == "reset_err_status":
                asyncio.run(run_res_err_status(machine.client, device_name))
                payload = {"result": True}
                status = 200
            else:
                # Respond with a failure message if the method is unknown
                payload = {"result": False, "data": "Unknown method"}
                status = 404

            # Send the response
            method_response = MethodResponse.create_from_method_request(request, status, payload)
            client.send_method_response(method_response)
        
        except Exception as e:
            print(f"Exception caught in handle_method: {e}")
            # 

    try:
        client.on_method_request_received = handle_method
    except:
        pass


