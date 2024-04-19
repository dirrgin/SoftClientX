
from asyncua import Client
from AbstractDevice import asyncio, ua, productionDevice
import sys

async def main():
    _opcUaServer = "opc.tcp://10.103.0.110:4840/"
    opcClient = Client(_opcUaServer)
    try:
        await opcClient.connect()
    except Exception as exc:
        print("Connection failed")
        print(f"Error: {exc}")
        sys.exit(1)
    else:
        print("OPC UA successful connection")
    
    #read child nodes to the list
    nodes = []
    nodes = await opcClient.get_objects_node().get_children()
    nodes = nodes[1:]
    devices = []
    for node in range(len(nodes)):
        nodeRepr = opcClient.get_node(nodes[node])
        temp = productionDevice(opcClient, nodeRepr)
        await temp.getDevProp()
        devices.append(temp)

    print("lets print D: ")
    print(devices[0])
    
if __name__ == "__main__":
    asyncio.run(main())