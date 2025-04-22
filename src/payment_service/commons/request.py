from pydantic import BaseModel

from .payment_data import PaymentData
from .customer import CustomerData


class Request(BaseModel):
    customer_data: CustomerData
    payment_data: PaymentData
