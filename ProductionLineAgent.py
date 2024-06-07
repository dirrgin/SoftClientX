import time, json
from azure.iot.device import IoTHubDeviceClient, Message, IoTHubModuleClient, MethodResponse, MethodRequest, Message
from AbstractDevice import productionDevice, asyncio

async def d2c(client, device):
    message = {}
    message["DeviceName"] = str(device.repr)[7:]
    message["ProductionStatus"] = device.productionStatus
    message["WorkorderId"] = device.workorderId
    message["ProductionRate"] = device.ProductionRate
    message["GoodCount"] = device.goodCount
    message["BadCount"] = device.badCount
    message["Temperature"] = device.temperature
    message["DeviceError"] = device.error
    error_sum = sum(_ for _ in range(len(device.error)))
    if error_sum>0:
        message["IsDevErr"] = "true"
    else:
        message["IsDevErr"] = "false"
    print(message["IsDevErr"])
    client.send_message(str(message))

async def twin_reported(client, device):
    reported_props = {"Device" + str(device.repr)[-1]: {"ProductionRate": device.ProductionRate,
                                                            "Errors": device.error}}
    
    client.patch_twin_reported_properties(reported_props)


async def compare_production_rates(twin_patch, lst_devices):
    for i in range(len(lst_devices)):
        name = "Device" + str(lst_devices[i].repr)[-1]
        rate = twin_patch[name]["ProductionRate"]
        if name in twin_patch.keys() and twin_patch[name] is not None and rate != lst_devices[i].ProductionRate:
            await lst_devices[i].set_prod_rate(rate)
            print(f"{name} set production rate successfully to {rate}")


async def receive_twin_desired(client, lst_devices):
    def twin_patch_handler(twin_patch):
        print("received desired properties: \t", twin_patch)
        try:
            print("Twin patch received.")
            twin_patch.pop('$version', None)
            for i in range(len(lst_devices)):
                name = "Device" + str(lst_devices[i].repr)[-1]
                rate = twin_patch[name]["ProductionRate"]
                if name in twin_patch.keys() and twin_patch[name] is not None and rate != lst_devices[i].ProductionRate:
                    asyncio.run(lst_devices[i].set_prod_rate(rate))
                    print(f"{name} set production rate successfully to {rate}")
        except Exception as e:
            print(f"Exception 1: {str(e)}")
    try:
        client.on_twin_desired_properties_patch_received = twin_patch_handler
    except Exception as e:
        print(f"Exception 2: {str(e)}")


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


async def take_direct_method(client, opc_client):
    def handle_method(request):
        try:
            print(f"Direct Method called: {request.name}")
            print(f"Request: {request}")
            print(f"Payload: {request.payload}")

            if request.name == "emergency_stop":
                device_name = request.payload
                asyncio.run(run_emergency_stop(opc_client, device_name))
                payload = {"result": True}
                status = 200
            elif request.name == "reset_err_status":
                device_name = request.payload
                asyncio.run(run_res_err_status(opc_client, device_name))
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


