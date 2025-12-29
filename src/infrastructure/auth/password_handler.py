import bcrypt

from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.logger import get_logger

logger = get_logger(__name__)


class PasswordHandler(IPasswordHandler):
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode("utf-8")

    def validate_password(self, password: str, hashed_password: str) -> bool:
        try:
            if not hashed_password.startswith("$2a$") and not hashed_password.startswith("$2b$"):
                logger.warning("Invalid bcrypt hash format")
                return False

            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except (ValueError, TypeError) as e:
            logger.warning(f"Password validation failed due to invalid hash format: {e}")
            return False
