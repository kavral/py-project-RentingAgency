from datetime import date
from pathlib import Path

from renting_agency.services.agency import RentingAgency
from renting_agency.storage.repository import DataRepository
from renting_agency.utils.iterators import payment_schedule


DATA_FILE = Path(__file__).parent / "data" / "agency_data.json"


def print_header(title: str) -> None:
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def read_float(prompt: str, default: float | None = None) -> float:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            value = float(raw)
            return value
        except ValueError:
            print("Please enter a valid number.")


def read_int(prompt: str, default: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            value = int(raw)
            return value
        except ValueError:
            print("Please enter a valid integer.")


def menu_add_property(agency: RentingAgency) -> None:
    print_header("Add Property")
    address = input("Street address: ")
    city = input("City: ")
    bedrooms = read_int("Number of bedrooms: ")
    rent = read_float("Monthly rent ($): ")
    description = input("Description (optional): ")

    try:
        prop = agency.add_property(address, city, bedrooms, rent, description)
        print(f"\nProperty added: {prop.summary()}")
        print(f"Annual rent: ${prop.annual_rent():.2f}")
        print(f"Deposit (1 month): ${prop.deposit_amount():.2f}")
    except ValueError as error:
        print(f"Error: {error}")


def menu_add_tenant(agency: RentingAgency) -> None:
    print_header("Register Tenant")
    name = input("Full name: ")
    email = input("Email: ")
    phone = input("Phone (+1234567890): ")
    score = read_int("Credit score (300-850): ", default=650)

    try:
        tenant = agency.add_tenant(name, email, phone, score)
        print(f"\nTenant registered: {tenant.summary()}")
    except ValueError as error:
        print(f"Error: {error}")


def menu_create_lease(agency: RentingAgency) -> None:
    print_header("Create Lease")
    if not agency.list_available_properties():
        print("No available properties.")
        return

    print("\nAvailable properties:")
    for prop in agency.list_available_properties():
        print(f"  {prop.summary()}")

    property_id = input("\nProperty ID (e.g. PROP-0001): ").strip().upper()
    tenant_id = input("Tenant ID (e.g. TEN-0001): ").strip().upper()
    months = read_int("Lease duration (months): ")

    try:
        lease = agency.create_lease(property_id, tenant_id, months)
        print(f"\nLease created: {lease.summary()}")
        print(f"Total contract value: ${lease.total_contract_value():.2f}")
        print(f"Deposit collected: ${lease.deposit_paid:.2f}")

        print("\nPayment schedule:")
        for number, due_date, amount in payment_schedule(
            lease.monthly_rent, lease.duration_months(), date.today()
        ):
            print(f"  Month {number}: {due_date} — ${amount:.2f}")
    except ValueError as error:
        print(f"Error: {error}")


def menu_search(agency: RentingAgency) -> None:
    print_header("Search Properties by Rent")
    min_rent = read_float("Minimum rent ($): ", default=0)
    max_rent = read_float("Maximum rent ($): ", default=10000)
    available_only = input("Available only? (y/n): ").strip().lower() == "y"

    results = agency.search_by_rent_range(min_rent, max_rent, available_only)
    if not results:
        print("No properties match your criteria.")
        return

    print(f"\nFound {len(results)} property/properties:")
    for prop in results:
        print(f"  {prop.summary()}")


def menu_list_all(agency: RentingAgency) -> None:
    print_header("All Records")

    print("\n--- Properties ---")
    if agency.properties:
        for prop in agency.properties:
            print(f"  {prop.summary()}")
    else:
        print("  (none)")

    print("\n--- Tenants ---")
    if agency.tenants:
        for tenant in agency.tenants:
            print(f"  {tenant.summary()}")
    else:
        print("  (none)")

    print("\n--- Leases ---")
    if agency.leases:
        for lease in agency.leases:
            print(f"  {lease.summary()}")
    else:
        print("  (none)")


def menu_revenue(agency: RentingAgency) -> None:
    print_header("Revenue Report")
    report = agency.revenue_report()

    for key, value in report.items():
        label = key.replace("_", " ").title()
        if "percent" in key:
            print(f"  {label}: {value}%")
        elif "leases" in key:
            print(f"  {label}: {int(value)}")
        else:
            print(f"  {label}: ${value:,.2f}")


def menu_end_lease(agency: RentingAgency) -> None:
    print_header("End Lease")
    lease_id = input("Lease ID (e.g. LEASE-0001): ").strip().upper()
    if agency.end_lease(lease_id):
        print(f"Lease {lease_id} ended. Property is available again.")
    else:
        print("Lease not found or already ended.")


def load_demo_data(agency: RentingAgency) -> None:

    if agency.properties or agency.tenants:
        return

    agency.add_property("42 Oak Street", "Almaty", 2, 185000.0, "Near metro")
    agency.add_property("15 River View", "Astana", 3, 245000.0, "Balcony, parking")
    agency.add_property("8 Studio Lane", "Almaty", 1, 120000.0, "Furnished studio")
    agency.add_tenant("Aida Nurpeisova", "aida@email.com", "+77001234567", 720)
    agency.add_tenant("Bekzat Karimov", "bek@email.com", "+77007654321", 580)
    agency.save_data()


def main() -> None:
    repository = DataRepository(DATA_FILE)
    agency = RentingAgency(repository)
    agency.load_data()
    load_demo_data(agency)

    menu_options = {
        "1": ("Add property", menu_add_property),
        "2": ("Register tenant", menu_add_tenant),
        "3": ("Create lease", menu_create_lease),
        "4": ("Search by rent range", menu_search),
        "5": ("List all records", menu_list_all),
        "6": ("Revenue report", menu_revenue),
        "7": ("End lease", menu_end_lease),
        "0": ("Save and exit", None),
    }

    while True:
        print_header("Renting Agency Management System")
        for key in sorted(menu_options.keys(), key=lambda k: (k == "0", k)):
            label, _ = menu_options[key]
            print(f"  {key}. {label}")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            agency.save_data()
            print("\nData saved. Goodbye!")
            break
        elif choice in menu_options and menu_options[choice][1] is not None:
            _, handler = menu_options[choice]
            handler(agency)
            agency.save_data()
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()