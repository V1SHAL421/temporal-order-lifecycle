from pydantic import BaseModel

class Order(BaseModel):
    state: str
    address_json: str

class Payment(BaseModel):
    order_id: str
    status: str
    amount: int

class Event(BaseModel):
    order_id: str
    type: str
    payload_json: str
    # ts: str