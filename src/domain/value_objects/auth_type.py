from enum import StrEnum


class AuthType(StrEnum):
    BEARER = "BEARER"


class TokenType(StrEnum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    PASSWORD_RESET = "PASSWORD_RESET"
