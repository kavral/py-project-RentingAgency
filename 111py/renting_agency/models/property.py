"""Property model."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Property:
    property_id: str
    address: str
    city: str
    bedrooms: int
    monthly_rent: float
    is_available: bool = True
    description: str = ""

    def annual_rent(self) -> float:
        return self.monthly_rent * 12

    def deposit_amount(self, months: int = 1) -> float:
        return round(self.monthly_rent * months, 2)

    def summary(self) -> str:
        status = "Available" if self.is_available else "Rented"
        return (
            f"[{self.property_id}] {self.address}, {self.city} | "
            f"{self.bedrooms} bed | ${self.monthly_rent:.2f}/mo | {status}"
        )

    def to_dict(self) -> dict:
        return {
            "property_id": self.property_id,
            "address": self.address,
            "city": self.city,
            "bedrooms": self.bedrooms,
            "monthly_rent": self.monthly_rent,
            "is_available": self.is_available,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Property":
        return cls(
            property_id=data["property_id"],
            address=data["address"],
            city=data["city"],
            bedrooms=int(data["bedrooms"]),
            monthly_rent=float(data["monthly_rent"]),
            is_available=bool(data.get("is_available", True)),
            description=data.get("description", ""),
        )
