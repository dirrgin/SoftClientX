
from asyncua import Client
from AbstractDevice import asyncio, ua
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
if __name__ == "__main__":
    asyncio.run(main())