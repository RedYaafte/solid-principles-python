import os
from typing import Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import stripe
from stripe import Charge
from stripe.error import StripeError
from dotenv import load_dotenv
from pydantic import BaseModel


_ = load_dotenv()


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerData(BaseModel):
    name: str
    contact_info: ContactInfo


class PaymentData(BaseModel):
    amount: int
    source: str


@dataclass
class CustomerValidator:

    def validate(self, customer_data: CustomerData):
        if not customer_data.name:
            print("Invalid customer data: missing name")
            raise ValueError("Invalid customer data: missing name")

        if not customer_data.contact_info:
            print("Invalid customer data: missing contact info")
            raise ValueError("Invalid customer data: missing contact info")

        if not (customer_data.contact_info.email or customer_data.contact_info):
            print("Invalid customer data: missing email and phone")
            raise ValueError("Invalid customer data: missing email and phone")


@dataclass
class PaymentDataValidator:

    def validate(self, payment_data: PaymentData):
        if not payment_data.source:
            print("Invalid payment data")
            raise ValueError("Invalid payment data")


class PaymentProcessor(ABC):

    @abstractmethod
    def process_transaction(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> Charge: ...


@dataclass
class StripePaymentProcessor(PaymentProcessor):

    def process_transaction(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> Charge:
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        try:
            charge = stripe.Charge.create(
                amount=payment_data.amount,
                currency="usd",
                source=payment_data.source,
                description="Charge for " + customer_data.name,
            )
            print("Payment successful")
        except StripeError as e:
            print("Payment failed:", e)
            return

        return charge


@dataclass
class TransactionLogger:

    def log(
        self, customer_data: CustomerData, payment_data: PaymentData, charge: Charge
    ):
        with open("transactions.log", "a") as log_file:
            log_file.write(f"{customer_data.name} paid {payment_data.amount}\n")
            if charge:
                log_file.write(f"Payment status: {charge.status}\n")


class Notifier(ABC):

    @abstractmethod
    def send_confirmation(self, customer_data: CustomerData): ...


class EmailNotifier(Notifier):

    def send_confirmation(self, customer_data: CustomerData):
        # import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText("Thank you for your payment.")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email

        # server = smtplib.SMTP("localhost")
        # server.send_message(msg)
        # server.quit()
        print("Email sent to", customer_data.contact_info.email)


class SMSNotifier(Notifier):

    def send_confirmation(self, customer_data: CustomerData):
        phone_number = customer_data.contact_info.phone
        sms_gateway = "the custom SMS Gateway"
        print(
            f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
        )


@dataclass
class PaymentService:
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notifier = field(default_factory=EmailNotifier)
    logger = TransactionLogger()

    def process_transaction(
        self, customer_data: CustomerData, payment_data: PaymentData
    ) -> Charge:
        try:
            self.customer_validator.validate(customer_data)
        except ValueError as e:
            raise e

        try:
            self.payment_validator.validate(payment_data)
        except ValueError as e:
            raise e

        try:
            charge = self.payment_processor.process_transaction(
                customer_data, payment_data
            )
            self.notifier.send_confirmation(customer_data)
            self.logger.log(customer_data, payment_data, charge)
            return charge
        except StripeError as e:
            print("Payment failed: ", e)
            raise e


if __name__ == "__main__":
    sms_notifier = SMSNotifier()
    payment_processor = PaymentService(notifier=sms_notifier)

    customer_data_with_email_d = {
        "name": "John Doe",
        "contact_info": {"email": "e@mail.com"},
    }
    customer_data_with_phone_d = {
        "name": "Platzi Python",
        "contact_info": {"phone": "1234567890"},
    }
    customer_data_with_email = CustomerData(**customer_data_with_email_d)
    customer_data_with_phone = CustomerData(**customer_data_with_phone_d)

    payment_data_d = {"amount": 500, "source": "tok_mastercard", "cvv": 123}
    payment_data = PaymentData(**payment_data_d)
    payment_processor.process_transaction(customer_data_with_email, payment_data)
    payment_processor.process_transaction(customer_data_with_phone, payment_data)

    # Payment with error
    payment_data_with_error_d = {
        "amount": 700,
        "source": "tok_visa_chargeDeclined",
        "cvv": 123,
    }
    payment_data_with_error = PaymentData(**payment_data_with_error_d)
    try:
        payment_processor.process_transaction(
            customer_data_with_email, payment_data_with_error
        )
    except Exception as e:
        print(f"Error con el procesamiento: {e}")
