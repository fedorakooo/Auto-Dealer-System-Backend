from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class CustomerCreateDTO:
    first_name: str
    second_name: str
    phone_number: str
    email: str
    password: str
    date_of_birth: date | None = None


@dataclass
class CustomerUpdateDTO:
    date_of_birth: date | None = None


@dataclass
class CustomerDTO:
    id: UUID
    user_id: UUID
    date_of_birth: date | None = None
