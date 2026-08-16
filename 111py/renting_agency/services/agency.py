"""Logic"""

from datetime import date, timedelta
from typing import Optional

from renting_agency.models.lease import Lease
from renting_agency.models.property import Property
from renting_agency.models.tenant import Tenant
from renting_agency.storage.repository import DataRepository
from renting_agency.utils.decorators import log_action, require_non_empty
from renting_agency.utils.iterators import AvailablePropertyIterator
from renting_agency.utils.validators import (
    validate_email,
    validate_phone,
    validate_property_id,
    validate_tenant_id,
)


class RentingAgency:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository
        self.properties: list[Property] = []
        self.tenants: list[Tenant] = []
        self.leases: list[Lease] = []
        self._next_property_num = 1
        self._next_tenant_num = 1
        self._next_lease_num = 1

    def load_data(self) -> None:
        data = self.repository.load()
        self.properties = [Property.from_dict(item) for item in data.get("properties", [])]
        self.tenants = [Tenant.from_dict(item) for item in data.get("tenants", [])]
        self.leases = [Lease.from_dict(item) for item in data.get("leases", [])]
        self._sync_counters()

    def save_data(self) -> None:
        self.repository.save(self.properties, self.tenants, self.leases)

    def _sync_counters(self) -> None:
        for prop in self.properties:
            if prop.property_id.startswith("PROP-"):
                num = int(prop.property_id.split("-")[1])
                self._next_property_num = max(self._next_property_num, num + 1)
        for tenant in self.tenants:
            if tenant.tenant_id.startswith("TEN-"):
                num = int(tenant.tenant_id.split("-")[1])
                self._next_tenant_num = max(self._next_tenant_num, num + 1)
        for lease in self.leases:
            if lease.lease_id.startswith("LEASE-"):
                num = int(lease.lease_id.split("-")[1])
                self._next_lease_num = max(self._next_lease_num, num + 1)

    def _generate_property_id(self) -> str:
        prop_id = f"PROP-{self._next_property_num:04d}"
        self._next_property_num += 1
        return prop_id

    def _generate_tenant_id(self) -> str:
        tenant_id = f"TEN-{self._next_tenant_num:04d}"
        self._next_tenant_num += 1
        return tenant_id

    def _generate_lease_id(self) -> str:
        lease_id = f"LEASE-{self._next_lease_num:04d}"
        self._next_lease_num += 1
        return lease_id

    @log_action
    @require_non_empty("address", "city")
    def add_property(
        self,
        address: str,
        city: str,
        bedrooms: int,
        monthly_rent: float,
        description: str = "",
    ) -> Property:
        if bedrooms < 0:
            raise ValueError("Bedrooms cannot be negative.")
        if monthly_rent <= 0:
            raise ValueError("Monthly rent must be positive.")

        prop = Property(
            property_id=self._generate_property_id(),
            address=address.strip(),
            city=city.strip(),
            bedrooms=bedrooms,
            monthly_rent=float(monthly_rent),
            description=description.strip(),
        )
        self.properties.append(prop)
        return prop

    @log_action
    @require_non_empty("full_name", "email", "phone")
    def add_tenant(
        self,
        full_name: str,
        email: str,
        phone: str,
        credit_score: int = 650,
    ) -> Tenant:
        if not validate_email(email):
            raise ValueError("Invalid email format.")
        if not validate_phone(phone):
            raise ValueError("Invalid phone format.")
        if credit_score < 300 or credit_score > 850:
            raise ValueError("Credit score must be between 300 and 850.")

        tenant = Tenant(
            tenant_id=self._generate_tenant_id(),
            full_name=full_name.strip(),
            email=email.strip(),
            phone=phone.strip(),
            credit_score=int(credit_score),
        )
        self.tenants.append(tenant)
        return tenant

    @log_action
    def create_lease(
        self,
        property_id: str,
        tenant_id: str,
        months: int,
        deposit_months: int = 1,
    ) -> Lease:
        property_id = property_id.strip().upper()
        tenant_id = tenant_id.strip().upper()

        if not validate_property_id(property_id):
            raise ValueError("Invalid property ID format (use PROP-0001).")
        if not validate_tenant_id(tenant_id):
            raise ValueError("Invalid tenant ID format (use TEN-0001).")
        if months < 1 or months > 60:
            raise ValueError("Lease duration must be between 1 and 60 months.")

        prop = self._find_property(property_id)
        tenant = self._find_tenant(tenant_id)

        if prop is None:
            raise ValueError(f"Property {property_id} not found.")
        if tenant is None:
            raise ValueError(f"Tenant {tenant_id} not found.")
        if not prop.is_available:
            raise ValueError(f"Property {property_id} is not available.")
        if not tenant.is_eligible():
            raise ValueError(
                f"Tenant {tenant_id} does not meet minimum credit score (600)."
            )

        start = date.today()
        end = start + timedelta(days=months * 30)
        deposit = prop.deposit_amount(deposit_months)

        lease = Lease(
            lease_id=self._generate_lease_id(),
            property_id=property_id,
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            monthly_rent=prop.monthly_rent,
            deposit_paid=deposit,
            is_active=True,
        )
        prop.is_available = False
        self.leases.append(lease)
        return lease

    def _find_property(self, property_id: str) -> Optional[Property]:
        for prop in self.properties:
            if prop.property_id == property_id:
                return prop
        return None

    def _find_tenant(self, tenant_id: str) -> Optional[Tenant]:
        for tenant in self.tenants:
            if tenant.tenant_id == tenant_id:
                return tenant
        return None

    def list_available_properties(self) -> list[Property]:
        iterator = AvailablePropertyIterator(self.properties)
        return list(iterator)

    def search_by_rent_range(
        self, min_rent: float, max_rent: float, available_only: bool = True
    ) -> list[Property]:
        results: list[Property] = []
        for prop in self.properties:
            in_range = min_rent <= prop.monthly_rent <= max_rent
            if available_only and not prop.is_available:
                continue
            if in_range:
                results.append(prop)
        return results

    def end_lease(self, lease_id: str) -> bool:
        lease_id = lease_id.strip().upper()
        for lease in self.leases:
            if lease.lease_id == lease_id and lease.is_active:
                lease.is_active = False
                prop = self._find_property(lease.property_id)
                if prop is not None:
                    prop.is_available = True
                return True
        return False

    def revenue_report(self) -> dict[str, float]:
        active_leases = [lease for lease in self.leases if lease.is_active]
        monthly_total = sum(lease.monthly_rent for lease in active_leases)
        annual_projection = monthly_total * 12
        deposits = sum(lease.deposit_paid for lease in active_leases)
        occupancy = 0.0
        if len(self.properties) > 0:
            rented = len(self.properties) - len(self.list_available_properties())
            occupancy = (rented / len(self.properties)) * 100
        return {
            "active_leases": float(len(active_leases)),
            "monthly_revenue": round(monthly_total, 2),
            "annual_projection": round(annual_projection, 2),
            "deposits_held": round(deposits, 2),
            "occupancy_percent": round(occupancy, 1),
        }
