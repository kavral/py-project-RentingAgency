"""Custom iterator and generators for rental data."""

from datetime import date
from typing import Generator, Iterable, Iterator, Tuple

from renting_agency.models.property import Property


class AvailablePropertyIterator:
    """Custom iterator: yields only available properties."""

    def __init__(self, properties: Iterable[Property]) -> None:
        self._properties = list(properties)
        self._index = 0

    def __iter__(self) -> Iterator[Property]:
        return self

    def __next__(self) -> Property:
        while self._index < len(self._properties):
            prop = self._properties[self._index]
            self._index += 1
            if prop.is_available:
                return prop
        raise StopIteration


def payment_schedule(
    monthly_rent: float,
    months: int,
    start: date | None = None,
) -> Generator[Tuple[int, date, float], None, None]:
    """Here generator yields (month_number, due_date, amount) for each payment."""
    if months < 1:
        return
    base = start or date.today()
    year, month = base.year, base.month
    for number in range(1, months + 1):
        due = date(year, month, 1)
        yield number, due, round(monthly_rent, 2)
        month += 1
        if month > 12:
            month = 1
            year += 1
