from logging import exception
from pydantic import validator, BaseModel
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




