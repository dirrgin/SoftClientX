import random, string, os
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from dotenv import load_dotenv
import asyncio

load_dotenv()
servicebus_connection_str = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
queue_name1 = os.getenv('QUEUE_CREATE')
queue_name2 = os.getenv('QUEUE_CONNECTIONS')
def generate_unique_id(base_id):
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_id}_{random_suffix}"

async def prepareIngredients(nodes):
    device_ids = [f"OPCUA_{node.nodeid.Identifier}" for node in nodes]
    unique_device_ids = []
    for device_id in device_ids:
        valid_device_id = device_id.replace(' ', '_').replace('/', '_')
        unique_device_id = generate_unique_id(valid_device_id)
        #print(f"Unique Device ID: {unique_device_id}")
        unique_device_ids.append(unique_device_id)
    return unique_device_ids

async def send_device_ids(device_ids):
    async with ServiceBusClient.from_connection_string(servicebus_connection_str) as client:
            sender = client.get_queue_sender(queue_name1)
            async with sender:
                for device_id in device_ids:
                    message = ServiceBusMessage(device_id)  
                    await sender.send_messages(message)
    print(f"Sent device IDs to the queue")



async def poll_create_connections():
    connection_strings = []
    async with ServiceBusClient.from_connection_string(servicebus_connection_str) as client:
        receiver = client.get_queue_receiver(queue_name2)
        async with receiver:
            while True:
                try:
                    received_msgs = await receiver.receive_messages(max_message_count=100, max_wait_time=5)
                    if not received_msgs:
                        print("Likely no more messages there.")
                        break
                    for msg in received_msgs:
                        connections = str(msg)
                        connection_strings.append(connections)
                        await receiver.complete_message(msg)
                except asyncio.TimeoutError:
                    print("Timeout reached while waiting for messages.")
                    break
    return connection_strings


