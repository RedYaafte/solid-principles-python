from commons import PaymentData, PaymentType

from processors import (
    PaymentProcessorProtocol,
    OfflinePaymentProcessor,
    StripePaymentProcessor,
    LocalPaymentProcessor,
)


class PaymentProcessorFactory:
    """Logica para decidir que procesador de pagos se debe de usar"""

    @staticmethod
    def create_payment_processor(payment_data: PaymentData) -> PaymentProcessorProtocol:
        match payment_data.type:
            case PaymentType.OFFLINE:
                return OfflinePaymentProcessor()

            case PaymentType.ONLINE:
                match payment_data.currency:
                    case "MXN":
                        return StripePaymentProcessor()
                    case _:
                        return LocalPaymentProcessor()

            case _:
                raise ValueError("No se soporta este tipo de pago")
