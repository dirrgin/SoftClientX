import time
import sys
from AbstractDevice import productionDevice, asyncio, ua
from asyncua import Client
from ProductionLineAgent import \
    d2c, connect_to_devices,\
    twin_reported, clean_twin,\
    receive_twin_desired, \
    take_direct_method, d2c_Error
from HubDevice import prepareIngredients, send_device_ids, poll_create_connections, os, load_dotenv

load_dotenv()
nodes=[] #the list of nodes from the opc ua
lst_machines=[] #the list of productionDevice instances, use them for the opc ua methods
lst_dev_err_new = [] #the list of errors 
unique_names=[] #the list of iot device names
productionLine=[] #the list of iot hub clients
connections = [] #the list of iot devices connection strings
async def main():
    opcua_endpoint = os.getenv('OPC_UA_ENDPOINT')
    #opcua_endpoint = "opc.tcp://172.20.10.10:4840/"
    # Connection to OPC UA server
    try:
        client_opc = Client(opcua_endpoint)
        await client_opc.connect()
    except Exception as e:
        print("OPC UA connection failed")
        print(f"Error: {e}")
        sys.exit(1)
    else:
        print("OPC UA connection success")
    # Connect, create, start
    nodes = await client_opc.get_objects_node().get_children()
    nodes = nodes[1:]
    '''unique_names = await prepareIngredients(nodes)
    await send_device_ids(unique_names)
    await asyncio.sleep(4)
    connections = await poll_create_connections()'''
    unique_names = ['OPCUA_Device_1_irctm3', 'OPCUA_Device_2_dqfv7p']
    connections = ['HostName=Cirencester-End.azure-devices.net;DeviceId=OPCUA_Device_1_irctm3;SharedAccessKey=mVMKbqroNNuNKW/25TW1W+cZM7EQhj/3Z3Dyj1nCWeA=', 'HostName=Cirencester-End.azure-devices.net;DeviceId=OPCUA_Device_2_dqfv7p;SharedAccessKey=kbpmc4fWZu89SxxW8TV+d/yt+Nl6Ij4woMXPT8cYDCA=']
    productionLine = await connect_to_devices(connections)
    
    for i in range(len(nodes)):
        nodeRepr = client_opc.get_node(nodes[i])
        machine = productionDevice(client_opc, nodeRepr, unique_names[i])
        lst_machines.append(machine)
        lst_dev_err_new.append(None)

    # Clean reported twins
    clean_twin(productionLine)

    try:
        while True: 
            ''' # are there new devices ? update the productionLine : continue 
            lst = await client_opc.get_objects_node().get_children() 
            lst = lst[1:] if len(nodes)<len(lst): new_devices = [] [new_devices.append(x) for x in range(len(nodes), len(lst))] uniqueIds = await prepareIngredients(new_devices) await send_device_ids(uniqueIds) await asyncio.sleep(4) connection_strings = await poll_create_connections()
            new_devices = await connect_to_devices(connection_strings, client_connection_str) [productionLine.append(new_device) for new_device in new_devices]'''
            # update data
            for j in range(len(lst_machines)):
                try:
                    await lst_machines[j].getDevProp()
                    if lst_dev_err_new[j] != lst_machines[j].error:
                        if lst_dev_err_new[j] != None: 
                            await d2c_Error(productionLine[j], lst_machines[j])
                        lst_dev_err_new[j] = lst_machines[j].error
                        #print("Send D2C - new Error State")
                    await receive_twin_desired(productionLine[j], lst_machines[j])
                    await d2c(productionLine[j], lst_machines[j])
                    await twin_reported(productionLine[j], lst_machines[j])
                    print("Send D2C , Twin Reported") 
                    await take_direct_method(productionLine[j], lst_machines[j])      
                except asyncio.TimeoutError:
                    print("Timeout error while awaiting for: d2c/twin_reported/direct method")
                except asyncio.CancelledError:
                    print("Task was cancelled")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard stopped program")

    # disconnect
    await client_opc.disconnect()
    client_iot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())