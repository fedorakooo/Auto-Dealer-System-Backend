from uuid import UUID


def parse_uuid(value) -> UUID:
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        return UUID(value)
    return UUID(str(value))
