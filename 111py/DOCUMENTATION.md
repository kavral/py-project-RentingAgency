# Renting Agency Management System

## Description

### Problem
Small property rental agencies often track apartments, tenants, and leases on paper or in scattered spreadsheets. This leads to double-bookings, missed rent calculations, and no quick view of occupancy or revenue.

### Goal
Build an application that centralizes property listings, tenant registration, lease creation, and basic financial reporting for a renting agency.

### Solution
The **Renting Agency Management System** is a modular Python application with:

- **Property management** — add listings with address, city, bedrooms, and monthly rent
- **Tenant registration** — store contact details and credit scores with validation
- **Lease workflow** — link a tenant to a property, collect deposit, mark unit as rented
- **Search** — filter properties by monthly rent range
- **Reports** — monthly revenue, annual projection, deposits held, occupancy rate
- **Persistence** — save and load all data to a JSON file

Run the application:

```bash
python main.py
```

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

---

## System Design

### Folder Structure

```
111py/
├── main.py                      # CLI entry point (menus, I/O)
├── DOCUMENTATION.md             # This file
├── data/
│   └── agency_data.json         # Some data
├── renting_agency/              # Main package
│   ├── __init__.py
│   ├── models/                  # Domain entities
│   │   ├── property.py
│   │   ├── tenant.py
│   │   └── lease.py
│   ├── services/                # Business logic
│   │   └── agency.py
│   ├── storage/                 # Data persistence
│   │   └── repository.py
│   └── utils/                   # Helpers
│       ├── validators.py        # Regular expressions
│       ├── decorators.py        # @log_action, @require_non_empty
│       └── iterators.py         # Custom iterator + generator
└── tests/
    └── test_agency.py
```

### Modules and Responsibilities

| Module | Role |
|--------|------|
| `models.property` | `Property` dataclass: rent, deposit, availability |
| `models.tenant` | `Tenant` dataclass: eligibility by credit score |
| `models.lease` | `Lease` dataclass: duration, contract value |
| `services.agency` | `RentingAgency` — core operations and rules |
| `storage.repository` | `DataRepository` — JSON load/save |
| `utils.validators` | Regex validation for email, phone, IDs |
| `utils.decorators` | Logging and input guards on service methods |
| `utils.iterators` | `AvailablePropertyIterator`, `payment_schedule` generator |
| `main.py` | Interactive menu loop (if/while/for, user input) |

### Classes

- **`Property`** — represents a rental unit; methods: `annual_rent()`, `deposit_amount()`, `summary()`
- **`Tenant`** — represents a client; method: `is_eligible()` compares credit score to threshold
- **`Lease`** — links property and tenant; methods: `duration_months()`, `total_contract_value()`
- **`RentingAgency`** — orchestrates collections of properties, tenants, and leases
- **`DataRepository`** — handles file I/O for persistence
- **`AvailablePropertyIterator`** — custom iterator yielding only available units

### Python Concepts Demonstrated

| Requirement | Where Used |
|-------------|------------|
| Input/output | `main.py` — `input()`, `print()` |
| Variables & data types | `str`, `int`, `float`, `bool`, `list`, `dict`, `date` |
| Arithmetic & comparison | rent totals, rent range search, credit score checks |
| `if` / `elif` / `else` | menu routing, validation, eligibility |
| Logical operators | `and`, `or`, `not` in search and lease rules |
| `for` / `while` loops | listing records, menu loop, iterators |
| Multiple modules & imports | package `renting_agency` |
| **Decorators** | `@log_action`, `@require_non_empty` in `agency.py` |
| **Generators** | `payment_schedule()` in `iterators.py` |
| **Regular expressions** | `validators.py` — email, phone, ID patterns |
| **Custom iterator** | `AvailablePropertyIterator` |
| **Unit tests** | `tests/test_agency.py` |

### Data Flow

1. User selects a menu option in `main.py`.
2. `main.py` calls methods on `RentingAgency`.
3. Service validates input (regex, business rules), updates in-memory lists.
4. On save/exit, `DataRepository` writes JSON to `data/agency_data.json`.
5. On startup, data is loaded back into `RentingAgency`.

---

## Example Usage

1. Start: `python main.py`
2. Option **1** — add a property (address, city, bedrooms, rent).
3. Option **2** — register a tenant (name, email, phone, credit score ≥ 600 for leasing).
4. Option **3** — create a lease using property and tenant IDs; view payment schedule.
5. Option **6** — view revenue and occupancy report.
6. Option **0** — save and exit.

Demo properties and tenants are created automatically on first run when the data file is empty.
