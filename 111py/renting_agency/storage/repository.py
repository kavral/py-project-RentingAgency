import json
from pathlib import Path
from typing import Any

from renting_agency.models.lease import Lease
from renting_agency.models.property import Property
from renting_agency.models.tenant import Tenant

class DataRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def load(self) -> dict[str, list[dict[str, Any]]]:
        if not self.file_path.exists():
            return {"properties": [], "tenants": [], "leases": []}
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(
        self,
        properties: list[Property],
        tenants: list[Tenant],
        leases: list[Lease],
    ) -> None:
        data = {
            "properties": [p.to_dict() for p in properties],
            "tenants": [t.to_dict() for t in tenants],
            "leases": [lease.to_dict() for lease in leases],
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
