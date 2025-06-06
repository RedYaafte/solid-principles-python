from enum import Enum
from pydantic import BaseModel


class PaymentType(Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class PaymentData(BaseModel):
    amount: int
    source: str
    currency: str = "MXN"
    type: PaymentType = PaymentType.ONLINE
