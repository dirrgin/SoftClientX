#classes with object obstractions
from asyncua import ua
import asyncio
class productionDevice:
    def __init__(self, client, repr, azureId):
        self.azureId = azureId
        self.client = client
        self.repr = repr
        self.productionStatus = 0
        self.workorderId = None
        self.goodCount = 0
        self.badCount = 0
        self.temperature = 0
        self.ProductionRate = 0
        self.error = None
    def __str__(self):
        return (f"Production Status: {self.productionStatus}, Workorder ID: {self.workorderId}, "
                f"Good Count: {self.goodCount}, Bad Count: {self.badCount}, "
                f"Temperature: {self.temperature}, Device Error: {self.deviceError}, "
                f"Production Rate: {self.ProductionRate}, "
                f"Calculated Error: {self.error}, Abstract Name: {self.iotName}.")
    async def getDevProp(self):
        self.productionStatus = await self.client.get_node(f"{self.repr}/ProductionStatus").get_value()
        self.workorderId = await self.client.get_node(f"{self.repr}/WorkorderId").get_value()
        self.goodCount = await self.client.get_node(f"{self.repr}/GoodCount").get_value()
        self.badCount = await self.client.get_node(f"{self.repr}/BadCount").get_value()
        self.temperature = await self.client.get_node(f"{self.repr}/Temperature").get_value()
        self.deviceError = await self.client.get_node(f"{self.repr}/DeviceError").get_value()
        self.ProductionRate = await self.client.get_node(f"{self.repr}/ProductionRate").get_value()
        deviceError = await self.client.get_node(f"{self.repr}/DeviceError").get_value()
        err_bin_str = bin(deviceError)[2:].zfill(4)
        self.error = [int(i) for i in err_bin_str]

    async def reset_err_status(self):
        reset = self.client.get_node(f"{self.repr}/ResetErrorStatus")
        await self.repr.call_method(reset)

    # direct method
    async def set_prod_rate(self, value):
        await self.client.set_values([self.client.get_node(f"{self.repr}/ProductionRate")],
                                [ua.DataValue(ua.Variant(int(value), ua.VariantType.Int32))])

    
    

    
   
    