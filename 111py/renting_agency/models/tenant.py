"""Tenant model."""

from dataclasses import dataclass


@dataclass
class Tenant:
    tenant_id: str
    full_name: str
    email: str
    phone: str
    credit_score: int = 0

    def is_eligible(self, minimum_score: int = 600) -> bool:
        return self.credit_score >= minimum_score

    def summary(self) -> str:
        eligible = "eligible" if self.is_eligible() else "review required"
        return (
            f"[{self.tenant_id}] {self.full_name} | {self.email} | "
            f"score: {self.credit_score} ({eligible})"
        )

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "credit_score": self.credit_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tenant":
        return cls(
            tenant_id=data["tenant_id"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            credit_score=int(data.get("credit_score", 0)),
        )
