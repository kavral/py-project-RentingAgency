"""Lease model."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Lease:
    lease_id: str
    property_id: str
    tenant_id: str
    start_date: date
    end_date: date
    monthly_rent: float
    deposit_paid: float
    is_active: bool = True

    def duration_months(self) -> int:
        months = (self.end_date.year - self.start_date.year) * 12
        months += self.end_date.month - self.start_date.month
        if self.end_date.day < self.start_date.day:
            months -= 1
        return max(months, 1)

    def total_contract_value(self) -> float:
        return round(self.monthly_rent * self.duration_months(), 2)

    def summary(self) -> str:
        status = "active" if self.is_active else "ended"
        return (
            f"[{self.lease_id}] {self.property_id} -> {self.tenant_id} | "
            f"{self.start_date} to {self.end_date} | ${self.monthly_rent:.2f}/mo | {status}"
        )

    def to_dict(self) -> dict:
        return {
            "lease_id": self.lease_id,
            "property_id": self.property_id,
            "tenant_id": self.tenant_id,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "monthly_rent": self.monthly_rent,
            "deposit_paid": self.deposit_paid,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Lease":
        return cls(
            lease_id=data["lease_id"],
            property_id=data["property_id"],
            tenant_id=data["tenant_id"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            monthly_rent=float(data["monthly_rent"]),
            deposit_paid=float(data["deposit_paid"]),
            is_active=bool(data.get("is_active", True)),
        )
