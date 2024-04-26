#classes with object obstractions
import asyncio
from asyncua import Client, ua
MSG_TXT = '{{"DeviceAddress": {DeviceAddress}, "ProductionStatus": {ProductionStatus}, "WorkOrderId": {WorkOrderId}, "GoodCount": {GoodCount}, "BadCount": {BadCount}, "Temperature": {Temperature}}}'
class productionDevice:
    def __init__(self, client, repr):
        self.client = client
        self.repr = repr
        self.productionStatus = None
        self.workorderId = None
        self.goodCount = None
        self.badCount = None
        self.temperature = None
        self.deviceError = None
        self.productionRate = None
    def __str__(self):
        return (f"Production Status: {self.productionStatus}, Workorder ID: {self.workorderId}, "
                f"Good Count: {self.goodCount}, Bad Count: {self.badCount}, "
                f"Temperature: {self.temperature}, Device Error: {self.deviceError}, "
                f"Production Rate: {self.productionRate}")
    async def getDevProp(self):
        self.productionStatus = await self.client.get_node(f"{self.repr}/ProductionStatus").get_value()
       #self.workorderId = await self.client.get_node(f"{self.repr}/WorkorderId").get_value()
        self.goodCount = await self.client.get_node(f"{self.repr}/GoodCount").get_value()
        self.badCount = await self.client.get_node(f"{self.repr}/BadCount").get_value()
        self.temperature = await self.client.get_node(f"{self.repr}/Temperature").get_value()
        self.deviceError = await self.client.get_node(f"{self.repr}/DeviceError").get_value()
        self.productionRate = await self.client.get_node(f"{self.repr}/ProductionRate").get_value()

    def packTelemetry(self):
        return MSG_TXT.format(
            DeviceAddress=str(self.repr),
            ProductionStatus=self.productionStatus,
            WorkOrderId=self.workorderId,
            GoodCount=self.goodCount,
            BadCount=self.badCount,
            Temperature=self.temperature
        )
        

    
    

    
   
    