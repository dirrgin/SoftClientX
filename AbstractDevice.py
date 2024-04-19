#classes with object obstractions
import asyncio
from asyncua import Client, ua
class productionDevice:
    def __init__(self):
        self.productionStatus = None
        self.workorderId = None
        self.goodCount = None
        self.badCount = None
        self.temperature = None
        self.deviceError = None
        self.productionRate = None