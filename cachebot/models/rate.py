from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class RateSnapshot:
    usd_rate: Decimal
    fee_percent: Decimal

    @property
    def fee_multiplier(self) -> Decimal:
        return self.fee_percent / Decimal("100")

    def usdt_amount(self, cash_amount: Decimal) -> Decimal:
        """
        Считает, сколько USDT нужно отправить, чтобы выдать указанную сумму наличными.
        usd_rate трактуем как курс «1 USDT = usd_rate RUB».
        """
        base = cash_amount / self.usd_rate
        fee = base * self.fee_multiplier
        return base + fee

    def cash_amount(self, usdt_amount: Decimal) -> Decimal:
        """
        Вычисляет сумму наличных, которую можно выдать за указанное количество USDT.
        """
        factor = Decimal("1") + self.fee_multiplier
        effective = usdt_amount / factor
        return effective * self.usd_rate
