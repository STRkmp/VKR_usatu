from logging import exception
from threading import Thread
from pydantic import validator, BaseModel
from qmanager.qmanager import QueueManager
from datetime import datetime

class Client(BaseModel):
    id : int
    message_id: int
    symbol: str
    


class ClientRequest(Client):
    type: list[str]
    add_info: str = ''
    date: datetime = datetime.now()
    @validator('symbol')
    def validate_symbol(cls,symbol):
        ##
        

        ##
        return  symbol

class ClientResponse(Client):
    def copy_req(self, cl: ClientRequest):
        try:
            self.id = cl.id
            self.message_id = cl.message_id
            self.symbol = cl.symbol
        except exception:
            print(exception)
    description: dict = dict()
    images : dict = dict()
    @validator('id')
    def validate_id(cls,id):
        ##
        
        ##
        return id
    class Config:
        arbitrary_types_allowed = True        

class ThreadedConsumer(Thread):
    def __init__(self, qmanager:QueueManager, queue_name:str):
        Thread.__init__(self)
        self.qmanager : QueueManager = qmanager
        self.queue_name : str = queue_name

    def run(self):
        print(f'{self.name} Consuming...')
        self.qmanager.consume(queue_name = self.queue_name)


