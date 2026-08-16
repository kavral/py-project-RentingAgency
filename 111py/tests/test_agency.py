"""For testing purposes."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from renting_agency.services.agency import RentingAgency
from renting_agency.storage.repository import DataRepository
from renting_agency.utils.iterators import AvailablePropertyIterator, payment_schedule
from renting_agency.utils.validators import (
    validate_email,
    validate_phone,
    validate_property_id,
    validate_tenant_id,
)
from renting_agency.models.property import Property


class TestValidators(unittest.TestCase):
    def test_valid_email(self) -> None:
        self.assertTrue(validate_email("user@example.com"))

    def test_invalid_email(self) -> None:
        self.assertFalse(validate_email("not-an-email"))

    def test_valid_phone(self) -> None:
        self.assertTrue(validate_phone("+77001234567"))

    def test_property_id_format(self) -> None:
        self.assertTrue(validate_property_id("PROP-0001"))
        self.assertFalse(validate_property_id("P-1"))

    def test_tenant_id_format(self) -> None:
        self.assertTrue(validate_tenant_id("TEN-0042"))
        self.assertFalse(validate_tenant_id("tenant1"))


class TestPropertyModel(unittest.TestCase):
    def test_annual_rent_and_deposit(self) -> None:
        prop = Property("PROP-0001", "1 Main St", "City", 2, 1000.0)
        self.assertEqual(prop.annual_rent(), 12000.0)
        self.assertEqual(prop.deposit_amount(2), 2000.0)


class TestIterators(unittest.TestCase):
    def test_available_property_iterator(self) -> None:
        props = [
            Property("PROP-0001", "A", "X", 1, 500.0, is_available=True),
            Property("PROP-0002", "B", "X", 2, 600.0, is_available=False),
            Property("PROP-0003", "C", "X", 1, 700.0, is_available=True),
        ]
        available = list(AvailablePropertyIterator(props))
        self.assertEqual(len(available), 2)
        self.assertEqual(available[0].property_id, "PROP-0001")

    def test_payment_schedule_generator(self) -> None:
        schedule = list(payment_schedule(1000.0, 3, date(2025, 1, 15)))
        self.assertEqual(len(schedule), 3)
        self.assertEqual(schedule[0][2], 1000.0)
        self.assertEqual(schedule[1][1], date(2025, 2, 1))


class TestRentingAgency(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "test_data.json"
        self.repo = DataRepository(self.data_path)
        self.agency = RentingAgency(self.repo)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_property_and_tenant(self) -> None:
        prop = self.agency.add_property("10 Test Rd", "Almaty", 2, 150000.0)
        tenant = self.agency.add_tenant(
            "Test User", "test@mail.com", "+77001112233", 700
        )
        self.assertTrue(validate_property_id(prop.property_id))
        self.assertTrue(validate_tenant_id(tenant.tenant_id))
        self.assertTrue(tenant.is_eligible())

    def test_create_lease_marks_property_unavailable(self) -> None:
        prop = self.agency.add_property("5 Lease Ave", "Astana", 1, 90000.0)
        tenant = self.agency.add_tenant(
            "Renter One", "r@mail.com", "+77009998877", 650
        )
        lease = self.agency.create_lease(prop.property_id, tenant.tenant_id, 12)
        self.assertFalse(prop.is_available)
        self.assertTrue(lease.is_active)
        self.assertEqual(lease.monthly_rent, 90000.0)

    def test_low_credit_score_blocks_lease(self) -> None:
        prop = self.agency.add_property("1 Block St", "City", 1, 50000.0)
        tenant = self.agency.add_tenant(
            "Low Score", "low@mail.com", "+77005554433", 500
        )
        with self.assertRaises(ValueError):
            self.agency.create_lease(prop.property_id, tenant.tenant_id, 6)

    def test_search_by_rent_range(self) -> None:
        self.agency.add_property("Cheap", "A", 1, 50000.0)
        self.agency.add_property("Mid", "A", 2, 100000.0)
        self.agency.add_property("Expensive", "A", 3, 300000.0)
        results = self.agency.search_by_rent_range(60000, 150000)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].address, "Mid")

    def test_revenue_report(self) -> None:
        prop = self.agency.add_property("Rev St", "City", 2, 100000.0)
        tenant = self.agency.add_tenant(
            "Paying Tenant", "pay@mail.com", "+77001230000", 700
        )
        self.agency.create_lease(prop.property_id, tenant.tenant_id, 12)
        report = self.agency.revenue_report()
        self.assertEqual(report["active_leases"], 1.0)
        self.assertEqual(report["monthly_revenue"], 100000.0)

    def test_persistence_round_trip(self) -> None:
        self.agency.add_property("Save St", "City", 1, 75000.0)
        self.agency.save_data()

        agency2 = RentingAgency(self.repo)
        agency2.load_data()
        self.assertEqual(len(agency2.properties), 1)
        self.assertEqual(agency2.properties[0].address, "Save St")


if __name__ == "__main__":
    unittest.main()
