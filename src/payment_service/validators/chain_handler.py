from abc import ABC, abstractmethod

from typing import Self, Optional
from dataclasses import dataclass

from commons import Request


@dataclass
class ChainHandler(ABC):
    _nex_handler: Optional[Self] = None

    def set_next(self, handler: Self):
        self._nex_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: Request): ...
